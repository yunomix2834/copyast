from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from app.application.commands.base import Command
from app.domain.services import CopyastService
from app.infrastructure.config import CopyastConfig


class SyncGitCommand(Command):
    def __init__(self, service: CopyastService, config: CopyastConfig) -> None:
        self.service = service
        self.config = config

    def execute(self, args: Namespace) -> int:
        root = Path(args.root).resolve()
        bundle = Path(args.bundle).resolve()
        result = self.service.sync_git(root, bundle)
        self.config.logger.info(
            "sync-git => modified=%s untracked=%s deleted=%s | updated=%s removed=%s",
            result["modified_count"],
            result["untracked_count"],
            result["deleted_count"],
            result["imported_or_updated"],
            result["deleted"],
        )
        return 0
