from __future__ import annotations

import argparse
import sys

from app.application.factories import CommandFactory


class CLI:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog="copyast",
            description="Export files to a txt bundle, manage entries, and sync with git diff.",
        )
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        self._build()

    # Thêm argument --root vào nhiều subcommand
    def _common_add_arg_root(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--root", default=".", help="Project root directory")

    def _build(self) -> None:
        # Export
        export = self.subparsers.add_parser(
            "export", help="Export all files from a folder to a txt bundle"
        )
        self._common_add_arg_root(export)
        export.add_argument("--output", required=True, help="Output txt bundle path")
        export.add_argument(
            "--ignore-file",
            default=".copyastignore.example",
            help="Ignore file path relative to root",
        )
        export.add_argument(
            "--ignore", action="append", default=[], help="Additional ignore pattern"
        )

        # Import
        import_one = self.subparsers.add_parser(
            "import", help="Import one file path into existing bundle"
        )
        self._common_add_arg_root(import_one)
        import_one.add_argument("--bundle", required=True, help="Bundle txt path")
        import_one.add_argument("--path", required=True, help="File path to import")

        # Bulk Import
        bulk_import = self.subparsers.add_parser(
            "bulk-import", help="Import many files into bundle"
        )
        self._common_add_arg_root(bulk_import)
        bulk_import.add_argument("--bundle", required=True, help="Bundle txt path")
        bulk_import.add_argument(
            "--paths", nargs="*", default=[], help="List of file paths"
        )
        bulk_import.add_argument(
            "--list-file", help="A txt file containing file paths, one per line"
        )

        # Delete
        delete = self.subparsers.add_parser(
            "delete", help="Delete one file entry from bundle"
        )
        delete.add_argument("--bundle", required=True, help="Bundle txt path")
        delete.add_argument(
            "--path", required=True, help="Relative path to remove from bundle"
        )

        # Bulk Delete
        bulk_delete = self.subparsers.add_parser(
            "bulk-delete", help="Delete many file entries from bundle"
        )
        bulk_delete.add_argument("--bundle", required=True, help="Bundle txt path")
        bulk_delete.add_argument(
            "--paths", nargs="*", default=[], help="List of relative paths"
        )
        bulk_delete.add_argument(
            "--list-file", help="A txt file containing paths, one per line"
        )

        # Scan Delete
        scan_delete = self.subparsers.add_parser(
            "scan-delete",
            help="Remove blocks where header path contains a given string",
        )
        scan_delete.add_argument("--bundle", required=True, help="Bundle txt path")
        scan_delete.add_argument(
            "--contains",
            required=True,
            help="Substring to search inside file header path",
        )

        # Sync Git
        sync_git = self.subparsers.add_parser(
            "sync-git", help="Sync bundle according to git changes"
        )
        self._common_add_arg_root(sync_git)
        sync_git.add_argument("--bundle", required=True, help="Bundle txt path")

    def parse_args(self, argv: list[str] | None = None) -> argparse.Namespace:
        return self.parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    cli = CLI()
    args = cli.parse_args(argv)
    factory = CommandFactory()
    command = factory.create(args.command)
    return command.execute(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
