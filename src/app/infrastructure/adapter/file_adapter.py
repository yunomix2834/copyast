from __future__ import annotations

from pathlib import Path
from typing import Iterable

from app.ports.ports import FilePort


class FileAdapter(FilePort):
    # Đọc file text UTF-8.
    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    # Tạo thư mục cha nếu chưa có
    # Ghi file text
    def write_text(self, path: Path, text: str) -> None:
        # parents=True: tạo cả thư mục cha trung gian
        # exist_ok=True: nếu thư mục đã tồn tại thì không lỗi
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def is_exists(self, path: Path) -> bool:
        return path.exists()

    # Đọc 4096 byte đầu
    # Nếu có byte null \x00 thì coi là binary
    # Nếu đọc lỗi thì cũng coi là binary luôn
    def is_binary(self, path: Path) -> bool:
        try:
            with path.open("rb") as fh:
                chunk = fh.read(8192)

            if b"\x00" in chunk:
                return True

            chunk.decode("utf-8")
            return False
        except (UnicodeDecodeError, OSError):
            return True

    # yield biến hàm thành generator.
    # Thay vì trả toàn bộ list file một lần, nó “nhả” từng file một.
    # Tiết kiệm memory hơn khi duyệt nhiều file.
    def walk_files(self, root: Path) -> Iterable[Path]:
        for path in root.rglob("*"):
            if path.is_file():
                yield path
