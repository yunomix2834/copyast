from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from app.application.commands.base import Command
from app.domain.services import CopyastService
from app.infrastructure.config import CopyastConfig


class ImportCommand(Command):
    def __init__(self, service: CopyastService, config: CopyastConfig) -> None:
        self.service = service
        self.config = config

    def execute(self, args: Namespace) -> int:
        roots = self.service.parse_root_specs(args.root_dir)
        export_file = Path(args.export).resolve()

        updated = self.service.upsert_targets_multi(
            roots=roots,
            export_file=export_file,
            files=args.file,
            dirs=args.dir,
        )
        self.config.logger.info("Imported/updated %s file(s)", updated)
        return 0
