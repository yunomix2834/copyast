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
        root = Path(args.root).resolve()
        bundle = Path(args.bundle).resolve()
        updated = self.service.upsert_paths(root, bundle, [args.path])
        self.config.logger.info("Imported/updated %s file(s)", updated)
        return 0
