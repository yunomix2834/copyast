from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from app.application.commands.base import Command
from app.domain.services import CopyastService
from app.infrastructure.config import CopyastConfig


class BulkImportCommand(Command):
    def __init__(self, service: CopyastService, config: CopyastConfig) -> None:
        self.service = service
        self.config = config

    def execute(self, args: Namespace) -> int:
        root = Path(args.root).resolve()
        bundle = Path(args.bundle).resolve()
        paths = list(args.paths or [])
        if args.list_file:
            list_file = Path(args.list_file).resolve()
            paths.extend(
                [
                    line.strip()
                    for line in list_file.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
            )
        updated = self.service.upsert_paths(root, bundle, paths)
        self.config.logger.info("Bulk imported/updated %s file(s)", updated)
        return 0
