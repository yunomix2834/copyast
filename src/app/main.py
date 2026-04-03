from __future__ import annotations

import argparse
import sys

from app.application.factories import CommandFactory


class CLI:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog="copyast",
            description="Export files to a txt export file, manage entries, and sync with git diff.",
        )
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        self._build()

    def _add_root_dir(
        self,
        parser: argparse.ArgumentParser,
        *,
        multiple: bool = False,
    ) -> None:
        if multiple:
            parser.add_argument(
                "--root-dir",
                action="append",
                default=[],
                help=(
                    "Project root directory. Repeatable. "
                    "Supports alias syntax: alias=/path/to/root"
                ),
            )
        else:
            parser.add_argument("--root-dir", default=".", help="Project root directory")

    def _add_export(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--export", required=True, help="Export txt file path")

    def _add_file_dir_targets(
        self,
        parser: argparse.ArgumentParser,
        *,
        include_list_file: bool = False,
        include_contains: bool = False,
    ) -> None:
        parser.add_argument(
            "--file",
            action="append",
            default=[],
            help="File target, repeat this flag to pass multiple files",
        )
        parser.add_argument(
            "--dir",
            action="append",
            default=[],
            help="Directory target, repeat this flag to pass multiple directories",
        )
        if include_list_file:
            parser.add_argument(
                "--list-file",
                help="Txt file containing targets. Use file:<path> or dir:<path>. Trailing / is treated as dir.",
            )
        if include_contains:
            parser.add_argument(
                "--contains",
                action="append",
                default=[],
                help="Substring matcher, repeatable",
            )

    def _build(self) -> None:
        export = self.subparsers.add_parser(
            "export", help="Export all files from one or many folders to one txt export file"
        )
        self._add_root_dir(export, multiple=True)
        self._add_export(export)
        export.add_argument(
            "--ignore-file",
            default=".copyastignore.example",
            help="Ignore file path relative to each root-dir",
        )
        export.add_argument(
            "--ignore", action="append", default=[], help="Additional ignore pattern"
        )
        export.add_argument(
            "--append",
            action="store_true",
            help="Append/merge into existing export file instead of overwriting it",
        )

        import_one = self.subparsers.add_parser(
            "import", help="Import file(s) or directory(s) from one or many roots into export"
        )
        self._add_root_dir(import_one, multiple=True)
        self._add_export(import_one)
        self._add_file_dir_targets(import_one)

        bulk_import = self.subparsers.add_parser(
            "bulk-import", help="Bulk import file(s) or directory(s) from one or many roots into export"
        )
        self._add_root_dir(bulk_import, multiple=True)
        self._add_export(bulk_import)
        self._add_file_dir_targets(bulk_import, include_list_file=True)

        delete = self.subparsers.add_parser(
            "delete", help="Delete file(s) or directory(s) from export"
        )
        self._add_export(delete)
        self._add_file_dir_targets(delete)

        bulk_delete = self.subparsers.add_parser(
            "bulk-delete", help="Bulk delete file(s) or directory(s) from export"
        )
        self._add_export(bulk_delete)
        self._add_file_dir_targets(bulk_delete, include_list_file=True)

        scan_delete = self.subparsers.add_parser(
            "scan-delete",
            help="Delete by substring match and/or exact file/dir targets from export",
        )
        self._add_export(scan_delete)
        self._add_file_dir_targets(scan_delete, include_contains=True)

        sync_git = self.subparsers.add_parser(
            "sync-git", help="Sync export according to git changes"
        )
        self._add_root_dir(sync_git, multiple=True)
        self._add_export(sync_git)

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