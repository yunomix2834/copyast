from __future__ import annotations

import subprocess
from pathlib import Path

from app.ports.ports import GitPort


class GitAdapter(GitPort):
    def is_git_repo(self, root: Path) -> bool:

        # ["git", "rev-parse", "--is-inside-work-tree"]: lệnh shell dạng list
        # cwd=root: chạy lệnh trong thư mục root
        # capture_output=True: bắt stdout/stderr
        # text=True: output trả về string thay vì bytes
        # check=False: không tự ném exception khi return code khác 0
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

        return result.returncode == 0 and result.stdout.strip() == "true"

    def dict_changed_files(self, root: Path) -> dict[str, list[str]]:
        # git status --porcelain cho output ngắn, dễ parse bằng máy.
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Cannot read git status")

        modified: list[str] = []
        deleted: list[str] = []
        untracked: list[str] = []

        for raw_line in result.stdout.splitlines():
            if not raw_line.strip():
                continue
            status = raw_line[:2]
            path = raw_line[3:].strip()
            if " -> " in path:
                # rename file: old -> new
                _, new_path = path.split(" -> ", 1)
                path = new_path.strip()

            if status == "??":
                untracked.append(path)
            elif "D" in status:
                deleted.append(path)
            else:
                modified.append(path)

        return {
            "modified": sorted(set(modified)),
            "deleted": sorted(set(deleted)),
            "untracked": sorted(set(untracked)),
        }
