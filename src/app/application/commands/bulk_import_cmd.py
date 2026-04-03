from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from app.application.commands.base import Command
from app.domain.services import CopyastService
from app.infrastructure.config import CopyastConfig


def _load_targets_from_list_file(list_file: str | None) -> tuple[list[str], list[str]]:
    if not list_file:
        return [], []

    file_targets: list[str] = []
    dir_targets: list[str] = []

    lines = Path(list_file).resolve().read_text(encoding="utf-8").splitlines()
    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if line.startswith("file:"):
            file_targets.append(line.removeprefix("file:").strip())
        elif line.startswith("dir:"):
            dir_targets.append(line.removeprefix("dir:").strip())
        elif line.endswith("/"):
            dir_targets.append(line.rstrip("/"))
        else:
            file_targets.append(line)

    return file_targets, dir_targets


class BulkImportCommand(Command):
    def __init__(self, service: CopyastService, config: CopyastConfig) -> None:
        self.service = service
        self.config = config

    def execute(self, args: Namespace) -> int:
        roots = self.service.parse_root_specs(args.root_dir)
        export_file = Path(args.export).resolve()

        list_files, list_dirs = _load_targets_from_list_file(args.list_file)

        updated = self.service.upsert_targets_multi(
            roots=roots,
            export_file=export_file,
            files=[*(args.file or []), *list_files],
            dirs=[*(args.dir or []), *list_dirs],
        )
        self.config.logger.info("Bulk imported/updated %s file(s)", updated)
        return 0
