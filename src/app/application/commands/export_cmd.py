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
        roots = self.service.parse_root_specs(args.root_dir)
        export_file = Path(args.export).resolve()

        ignore_by_alias: dict[str, CopyastIgnoreAdapter] = {}
        for spec in roots:
            ignore_file = self.config.get_ignore_file(args.ignore_file)
            ignore_matcher = CopyastIgnoreAdapter.from_sources(
                spec.path, spec.path / ignore_file, args.ignore
            )
            ignore_by_alias[spec.alias] = ignore_matcher

        count = self.service.export_directories(
            roots=roots,
            export_file=export_file,
            ignore_by_alias=ignore_by_alias,
            append=args.append,
        )
        self.config.logger.info("Exported %s file(s) to %s", count, export_file)
        return 0