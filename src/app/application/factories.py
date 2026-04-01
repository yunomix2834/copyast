from __future__ import annotations

from app.application.bootstrap import Bootstrap
from app.application.commands.base import Command
from app.application.commands.bulk_delete_cmd import BulkDeleteCommand
from app.application.commands.bulk_import_cmd import BulkImportCommand
from app.application.commands.delete_cmd import DeleteCommand
from app.application.commands.export_cmd import ExportCommand
from app.application.commands.import_cmd import ImportCommand
from app.application.commands.scan_delete_cmd import ScanDeleteCommand
from app.application.commands.sync_git_cmd import SyncGitCommand
from app.infrastructure.config import CopyastConfig


# Khi factory được tạo thì sẽ
# - Tạo các config dùng chung
# - Gọi bootstrap để dựng service
class CommandFactory:
    def __init__(self) -> None:
        self.config = CopyastConfig()
        self.service = Bootstrap.build_copyast_service()

    def create(self, command_name: str) -> Command:
        mapping: dict[str, type[Command]] = {
            "export": ExportCommand,
            "import": ImportCommand,
            "bulk-import": BulkImportCommand,
            "delete": DeleteCommand,
            "bulk-delete": BulkDeleteCommand,
            "scan-delete": ScanDeleteCommand,
            "sync-git": SyncGitCommand,
        }
        command_class = mapping.get(command_name)
        if command_class is None:
            raise ValueError(f"Unsupported command: {command_name}")
        return command_class(self.service, self.config)
