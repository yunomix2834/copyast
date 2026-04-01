from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from app.application.commands.base import Command
from app.domain.services import CopyastService
from app.infrastructure.adapter.copyast_adapter import CopyastIgnoreAdapter
from app.infrastructure.config import CopyastConfig


class ExportCommand(Command):
    def __init__(self, service: CopyastService, config: CopyastConfig) -> None:
        self.service = service
        self.config = config

    def execute(self, args: Namespace) -> int:
        root = Path(args.root).resolve()
        bundle_path = (
            (root / args.output).resolve()
            if not Path(args.output).is_absolute()
            else Path(args.output)
        )
        ignore_file = self.config.get_ignore_file(args.ignore_file)
        ignore_matcher = CopyastIgnoreAdapter.from_sources(
            root, root / ignore_file, args.ignore
        )
        count = self.service.export_directory(root, bundle_path, ignore_matcher)
        self.config.logger.info("Exported %s file(s) to %s", count, bundle_path)
        return 0
