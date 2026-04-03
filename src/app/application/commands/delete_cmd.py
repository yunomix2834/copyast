from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from app.application.commands.base import Command
from app.domain.services import CopyastService
from app.infrastructure.config import CopyastConfig


class DeleteCommand(Command):
    def __init__(self, service: CopyastService, config: CopyastConfig) -> None:
        self.service = service
        self.config = config

    def execute(self, args: Namespace) -> int:
        export_file = Path(args.export).resolve()
        deleted = self.service.delete_targets(
            export_file=export_file,
            files=args.file,
            dirs=args.dir,
        )
        self.config.logger.info("Deleted %s file(s) from export", deleted)
        return 0
