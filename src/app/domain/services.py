from __future__ import annotations

from pathlib import Path

from app.domain.models import CopyastEntry
from app.infrastructure.config import CopyastConfig
from app.ports.ports import CopyastIgnorePort, CopyastPort, FilePort, GitPort


class CopyastService:
    def __init__(
        self, fs: FilePort, repo: CopyastPort, git: GitPort, conf: CopyastConfig
    ) -> None:
        self.fs = fs
        self.repo = repo
        self.git = git
        self.conf = conf

    # Đi qua tất cả các file trong thư mục root
    # -> chuyển mỗi file thành CopyastEntry(path, content)
    # -> Bỏ qua file output chính nó
    # -> Bỏ qua file bị ignore
    # -> Bỏ qua file binary
    # -> Save lại tất cả
    def export_directory(
        self, root: Path, path: Path, ignore: CopyastIgnorePort
    ) -> int:
        entries: list[CopyastEntry] = []
        for file_path in self.fs.walk_files(root):
            rel = str(file_path.relative_to(root)).replace("\\", "/")
            if rel == str(path.relative_to(root)).replace("\\", "/"):
                continue
            if ignore.is_ignore(rel):
                continue
            if self.fs.is_binary(file_path):
                self.conf.logger.info("Skip binary: %s", rel)
                continue
            content = self.fs.read_text(file_path)
            entries.append(CopyastEntry(path=rel, content=content))

        self.repo.save(path, entries)
        return len(entries)

    # Load bundle hiện tại
    # Biến list entry thành dict
    # Nếu path đã tồn tại thì update
    # Nếu chưa có thì insert mới
    def upsert_paths(self, root: Path, path: Path, paths: list[str]) -> int:
        entries = self.repo.load(path)
        dict_entry_path = {entry.path: entry for entry in entries}
        updated = 0

        for p in paths:
            # Nếu p là relative path thì ghép với root
            # Nếu đã là absolute path thì dùng luôn
            full = (root / p).resolve() if not Path(p).is_absolute() else Path(p)
            if not full.exists() or full.is_dir():
                self.conf.logger.warning("Path is not found or is directory: %s", p)
                continue
            if self.fs.is_binary(full):
                self.conf.logger.info("Skip binary: %s", p)
                continue
            # Chuyển về relative path
            # Ghi đè vào dict theo key rel
            # Nếu key cũ đã có -> update
            # Nếu key chưa có -> thêm mới
            rel = str(full.relative_to(root.resolve())).replace("\\", "/")
            dict_entry_path[rel] = CopyastEntry(
                path=rel, content=self.fs.read_text(full)
            )
            updated += 1

        self.repo.save(path, list(dict_entry_path.values()))
        return updated

    # Load bundle
    # loại bỏ entry nào có path nằm trong paths
    def delete_paths(self, path: Path, paths: list[str]) -> int:
        target = {p.replace("\\", "/"): p for p in paths}
        entries = self.repo.load(path)
        list_entries = [entry for entry in entries if entry.path not in target]
        deleted = len(entries) - len(list_entries)
        self.repo.save(path, list_entries)
        return deleted

    # Xóa mọi entry mà entry.path chứa chuỗi contains
    def scan_delete(self, path: Path, contains: str) -> int:
        entries = self.repo.load(path)
        list_entries = [entry for entry in entries if contains not in entry.path]
        deleted = len(entries) - len(list_entries)
        self.repo.save(path, list_entries)
        return deleted

    # Check thư mục có phải Git repo không
    # Lấy file changed từ git
    # File modified + untracked -> import / update vào bundle
    # File deleted -> xóa khỏi bundle
    # Trả ra thống kê
    def sync_git(self, root: Path, path: Path) -> dict[str, int]:
        if not self.git.is_git_repo(root):
            raise RuntimeError(f"{root} is not a git repository")

        status = self.git.dict_changed_files(root)
        imported = self.upsert_paths(
            root, path, status["modified"] + status["untracked"]
        )
        deleted = self.delete_paths(path, status["deleted"])

        return {
            "imported_or_updated": imported,
            "deleted": deleted,
            "modified_count": len(status["modified"]),
            "untracked_count": len(status["untracked"]),
            "deleted_count": len(status["deleted"]),
        }
