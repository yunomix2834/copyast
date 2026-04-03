from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.domain.models import CopyastEntry
from app.infrastructure.config import CopyastConfig
from app.ports.ports import CopyastIgnorePort, CopyastPort, FilePort, GitPort


@dataclass(frozen=True, slots=True)
class RootSpec:
    alias: str
    path: Path


class CopyastService:
    def __init__(
        self, fs: FilePort, repo: CopyastPort, git: GitPort, conf: CopyastConfig
    ) -> None:
        self.fs = fs
        self.repo = repo
        self.git = git
        self.conf = conf

    def parse_root_specs(self, raw_roots: list[str] | None) -> list[RootSpec]:
        raw_roots = raw_roots or ["."]
        specs: list[RootSpec] = []

        for raw in raw_roots:
            item = raw.strip()
            if not item:
                continue

            if "=" in item:
                alias, raw_path = item.split("=", 1)
                alias = alias.strip()
                root_path = Path(raw_path.strip()).resolve()
            else:
                root_path = Path(item).resolve()
                alias = root_path.name

            if not alias:
                raise ValueError(f"Invalid root-dir alias: {raw}")

            specs.append(RootSpec(alias=alias, path=root_path))

        if not specs:
            specs = [RootSpec(alias=Path(".").resolve().name, path=Path(".").resolve())]

        aliases = [x.alias for x in specs]
        if len(set(aliases)) != len(aliases):
            raise ValueError(
                "Duplicate root aliases detected. Use alias=/path syntax for each root-dir."
            )

        return specs

    def _build_bundle_path(self, spec: RootSpec, full: Path, *, multi_root: bool) -> str:
        rel = str(full.resolve().relative_to(spec.path.resolve())).replace("\\", "/")
        return f"{spec.alias}/{rel}" if multi_root else rel

    def _expand_files_and_dirs_multi(
        self,
        roots: list[RootSpec],
        files: list[str] | None = None,
        dirs: list[str] | None = None,
    ) -> list[tuple[RootSpec, Path]]:
        collected: list[tuple[RootSpec, Path]] = []
        seen: set[tuple[str, Path]] = set()

        for spec in roots:
            for raw_file in files or []:
                full = (
                    (spec.path / raw_file).resolve()
                    if not Path(raw_file).is_absolute()
                    else Path(raw_file).resolve()
                )
                if not full.exists():
                    continue
                if full.is_dir():
                    self.conf.logger.warning("Expected file but got directory: %s", raw_file)
                    continue

                key = (spec.alias, full)
                if key not in seen:
                    seen.add(key)
                    collected.append((spec, full))

            for raw_dir in dirs or []:
                full_dir = (
                    (spec.path / raw_dir).resolve()
                    if not Path(raw_dir).is_absolute()
                    else Path(raw_dir).resolve()
                )
                if not full_dir.exists():
                    continue
                if not full_dir.is_dir():
                    self.conf.logger.warning("Expected directory but got file: %s", raw_dir)
                    continue

                for file_path in self.fs.walk_files(full_dir):
                    key = (spec.alias, file_path)
                    if key not in seen:
                        seen.add(key)
                        collected.append((spec, file_path))

        return collected

    def export_directories(
        self,
        roots: list[RootSpec],
        export_file: Path,
        ignore_by_alias: dict[str, CopyastIgnorePort],
        *,
        append: bool = False,
    ) -> int:
        export_file = export_file.resolve()
        multi_root = len(roots) > 1

        current = self.repo.load(export_file) if append else []
        dict_entry_path = {entry.path: entry for entry in current}

        for spec in roots:
            ignore = ignore_by_alias[spec.alias]

            for file_path in self.fs.walk_files(spec.path):
                if file_path.resolve() == export_file:
                    continue

                rel = str(file_path.relative_to(spec.path)).replace("\\", "/")
                if ignore.is_ignore(rel):
                    continue
                if self.fs.is_binary(file_path):
                    self.conf.logger.info("Skip non-utf8/binary: %s", rel)
                    continue

                try:
                    content = self.fs.read_text(file_path)
                except (UnicodeDecodeError, OSError) as exc:
                    self.conf.logger.warning("Skip unreadable text file %s: %s", rel, exc)
                    continue

                bundle_path = self._build_bundle_path(spec, file_path, multi_root=multi_root)
                dict_entry_path[bundle_path] = CopyastEntry(path=bundle_path, content=content)

        self.repo.save(export_file, list(dict_entry_path.values()))
        return len(dict_entry_path)

    def upsert_targets_multi(
        self,
        roots: list[RootSpec],
        export_file: Path,
        files: list[str] | None = None,
        dirs: list[str] | None = None,
    ) -> int:
        entries = self.repo.load(export_file)
        dict_entry_path = {entry.path: entry for entry in entries}
        updated = 0
        multi_root = len(roots) > 1

        for spec, full in self._expand_files_and_dirs_multi(roots, files, dirs):
            if self.fs.is_binary(full):
                rel = str(full.relative_to(spec.path)).replace("\\", "/")
                self.conf.logger.info("Skip non-utf8/binary: %s", rel)
                continue

            try:
                content = self.fs.read_text(full)
            except (UnicodeDecodeError, OSError) as exc:
                rel = str(full.relative_to(spec.path)).replace("\\", "/")
                self.conf.logger.warning("Skip unreadable text file %s: %s", rel, exc)
                continue

            bundle_path = self._build_bundle_path(spec, full, multi_root=multi_root)
            dict_entry_path[bundle_path] = CopyastEntry(path=bundle_path, content=content)
            updated += 1

        self.repo.save(export_file, list(dict_entry_path.values()))
        return updated

    def delete_targets(
        self,
        export_file: Path,
        files: list[str] | None = None,
        dirs: list[str] | None = None,
    ) -> int:
        normalized_files = {p.replace("\\", "/") for p in (files or [])}
        normalized_dirs = {
            p.replace("\\", "/").rstrip("/") for p in (dirs or []) if p.strip()
        }

        entries = self.repo.load(export_file)
        filtered: list[CopyastEntry] = []

        for entry in entries:
            entry_path = entry.path.replace("\\", "/")
            if entry_path in normalized_files:
                continue

            matched_dir = any(
                entry_path == dir_path or entry_path.startswith(dir_path + "/")
                for dir_path in normalized_dirs
            )
            if matched_dir:
                continue

            filtered.append(entry)

        deleted = len(entries) - len(filtered)
        self.repo.save(export_file, filtered)
        return deleted

    def scan_delete(
        self,
        export_file: Path,
        contains_list: list[str] | None = None,
        files: list[str] | None = None,
        dirs: list[str] | None = None,
    ) -> int:
        contains_list = [x for x in (contains_list or []) if x]
        normalized_files = {p.replace("\\", "/") for p in (files or [])}
        normalized_dirs = {
            p.replace("\\", "/").rstrip("/") for p in (dirs or []) if p.strip()
        }

        entries = self.repo.load(export_file)
        filtered: list[CopyastEntry] = []

        for entry in entries:
            entry_path = entry.path.replace("\\", "/")

            if entry_path in normalized_files:
                continue

            if any(entry_path == d or entry_path.startswith(d + "/") for d in normalized_dirs):
                continue

            if any(token in entry_path for token in contains_list):
                continue

            filtered.append(entry)

        deleted = len(entries) - len(filtered)
        self.repo.save(export_file, filtered)
        return deleted

    def sync_git_multi(self, roots: list[RootSpec], export_file: Path) -> dict[str, int]:
        total_modified = 0
        total_untracked = 0
        total_deleted = 0
        imported = 0
        deleted = 0
        multi_root = len(roots) > 1

        entries = self.repo.load(export_file)
        dict_entry_path = {entry.path: entry for entry in entries}

        for spec in roots:
            if not self.git.is_git_repo(spec.path):
                raise RuntimeError(f"{spec.path} is not a git repository")

            status = self.git.dict_changed_files(spec.path)

            total_modified += len(status["modified"])
            total_untracked += len(status["untracked"])
            total_deleted += len(status["deleted"])

            for raw_file in status["modified"] + status["untracked"]:
                full = (spec.path / raw_file).resolve()
                if not full.exists() or full.is_dir():
                    continue
                if self.fs.is_binary(full):
                    continue

                try:
                    content = self.fs.read_text(full)
                except (UnicodeDecodeError, OSError):
                    continue

                bundle_path = self._build_bundle_path(spec, full, multi_root=multi_root)
                dict_entry_path[bundle_path] = CopyastEntry(path=bundle_path, content=content)
                imported += 1

            deleted_paths = {
                f"{spec.alias}/{p}" if multi_root else p.replace("\\", "/")
                for p in status["deleted"]
            }
            for key in list(dict_entry_path.keys()):
                if key in deleted_paths:
                    dict_entry_path.pop(key)
                    deleted += 1

        self.repo.save(export_file, list(dict_entry_path.values()))
        return {
            "imported_or_updated": imported,
            "deleted": deleted,
            "modified_count": total_modified,
            "untracked_count": total_untracked,
            "deleted_count": total_deleted,
        }