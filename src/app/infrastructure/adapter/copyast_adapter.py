from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from app.domain.models import CopyastEntry
from app.infrastructure.adapter.file_adapter import FileAdapter
from app.infrastructure.config import CopyastConfig
from app.ports.ports import CopyastIgnorePort, CopyastPort


class CopyastAdapter(CopyastPort):
    def __init__(self) -> None:
        self.conf = CopyastConfig()
        self.fs = FileAdapter()

    # Nếu bundle chưa tồn tại -> trả list rỗng
    # Đọc file
    # Tách từng dòng
    # Parse từng block
    def load(self, path: Path) -> list[CopyastEntry]:
        if not self.fs.is_exists(path):
            return []

        text = self.fs.read_text(path)
        lines = text.splitlines()
        entries: list[CopyastEntry] = []

        current_path: str | None = None
        buffer: list[str] = []

        for line in lines:
            if line.startswith(self.conf.header_prefix) and line.endswith(
                self.conf.header_suffix
            ):
                if current_path is not None:
                    entries.append(
                        CopyastEntry(
                            path=current_path, content="\n".join(buffer).rstrip("\n")
                        )
                    )
                current_path = line[
                    len(self.conf.header_prefix) : -len(self.conf.header_suffix)
                ]
                buffer = []
            else:
                if current_path is not None:
                    buffer.append(line)

        if current_path is not None:
            entries.append(
                CopyastEntry(path=current_path, content="\n".join(buffer).rstrip("\n"))
            )

        return entries

    # Sort entry theo path
    # Mỗi file được lưu thành 1 block
    def save(self, path: Path, entries: list[CopyastEntry]) -> None:
        blocks: list[str] = []
        for entry in sorted(entries, key=lambda x: x.path):
            blocks.append(self.conf.get_header(entry.path))
            blocks.append(entry.content)
            blocks.append("")
        # Nối list string thành 1 string lớn, ngăn cách bởi newline
        # Bỏ newline / dấu trắng thừa cuối file
        # Rồi thêm đúng 1 newline cuối file
        content = "\n".join(blocks).rstrip() + "\n"
        self.fs.write_text(path, content)


# Đọc ignore patter từ:
# - ignore file truyền vào
# - .gitignore
# - extra pattern từ CLI
class CopyastIgnoreAdapter(CopyastIgnorePort):
    # Strip từng dòng
    # Bỏ dòng rỗng
    # Bỏ comment bắt đầu bằng #
    def __init__(self, patterns: list[str] | None = None) -> None:
        # self.patterns là danh sách rule ignore, ví dụ có thể là:
        """
        [
            "*.log",
            "node_modules/",
            "build/",
            ".env",
            "__pycache__/"
        ]
        """
        self.patterns = [
            p.strip()
            for p in (patterns or [])
            if p.strip() and not p.strip().startswith("#")
        ]

    # Gom pattern từ nhiều nguồn
    @staticmethod
    def from_sources(
        root: Path, ignore_file: Path, extra_patterns: list[str] | None = None
    ) -> "CopyastIgnoreAdapter":
        patterns: list[str] = []

        # Nếu có file ignore riêng thì đọc vào
        if ignore_file.exists():
            patterns.extend(ignore_file.read_text(encoding="utf-8").splitlines())

        # Đọc thêm .gitignore
        gitignore = root / ".gitignore"
        if gitignore.exists():
            patterns.extend(gitignore.read_text(encoding="utf-8").splitlines())

        # Đọc thêm pattern từ CLI
        if extra_patterns:
            patterns.extend(extra_patterns)

        return CopyastIgnoreAdapter(patterns)

    # Kiểm tra path có bị ignore hay không
    # Chuẩn hóa path đang xét
    # Duyệt từng pattern ignore
    # Với mỗi pattern:
    #  - nếu pattern là kiểu thư mục (build/)
    #  - hoặc pattern là wildcard (*.log)
    #  - hoặc pattern là tên file (.env)
    # Nếu thấy match với bất kỳ rule nào → return True
    # Duyệt hết mà không match → return False
    def is_ignore(self, relative_path: str, is_directory: bool = False) -> bool:
        normalized = relative_path.replace("\\", "/")
        for raw in self.patterns:
            pattern = raw.strip()
            if not pattern:
                continue

            dir_only = pattern.endswith("/")
            plain = pattern.rstrip("/")

            if dir_only:
                # Ignore toàn bộ thư mục đó và toàn bộ file con
                if normalized == plain or normalized.startswith(plain + "/"):
                    return True
                continue

            # fnmatch là gì?
            # Là hàm so khớp wildcard kiểu shell:
            # * = bất kỳ chuỗi nào
            # ? = một ký tự
            # ví dụ:
            #  - "*.py"
            #  - "app/*.py"
            #  - "test_?.txt"

            # So cả đường dẫn đầy đủ tương đối với pattern.
            if fnmatch(normalized, pattern):
                return True

            # So pattern chỉ với tên file, bỏ qua thư mục cha.
            if fnmatch(Path(normalized).name, pattern):
                return True

            # So nếu path đúng bằng pattern
            # hoặc path nằm bên dưới pattern đó
            if normalized == plain or normalized.startswith(plain + "/"):
                return True

        return False
