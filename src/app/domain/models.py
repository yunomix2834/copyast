from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


# frozen=True: Object immutable tương đối, tức là tạo xong thì không sửa field được.
# slots=True: Giảm memory và ngăn tạo attribute linh tinh ngoài dự kiến.
@dataclass(frozen=True, slots=True)
class CopyastEntry:
    path: str
    content: str

    # @staticmethod nghĩa là hàm thuộc class nhưng không cần self
    @staticmethod
    def from_path(path: Path, content: str, root: Path) -> "CopyastEntry":
        return CopyastEntry(
            path=str(path.relative_to(root)).replace("\\", "/"), content=content
        )
