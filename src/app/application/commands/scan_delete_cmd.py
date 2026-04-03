from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from app.application.commands.base import Command
from app.domain.services import CopyastService
from app.infrastructure.config import CopyastConfig


class ScanDeleteCommand(Command):
    def __init__(self, service: CopyastService, config: CopyastConfig) -> None:
        self.service = service
        self.config = config

    def execute(self, args: Namespace) -> int:
        export_file = Path(args.export).resolve()
        deleted = self.service.scan_delete(
            export_file=export_file,
            contains_list=args.contains,
            files=args.file,
            dirs=args.dir,
        )
        self.config.logger.info("Scan delete removed %s file block(s)", deleted)
        return 0