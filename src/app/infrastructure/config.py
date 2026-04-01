from __future__ import annotations

import logging
from pathlib import Path
from threading import Lock


class SingletonMeta(type):
    _instances: dict[type, object] = {}
    _lock = Lock()

    # cls là class đang được gọi để tạo instance
    # with cls._lock: để thread-safe
    # nếu class chưa có instance thì tạo
    # nếu rồi thì trả instance cũ
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(SingletonMeta, cls).__call__(
                    *args, **kwargs
                )
        return cls._instances[cls]


class CopyastConfig(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.default_ignore_file = ".copyastignore.example"
        self.default_encoding = "utf-8"
        self.header_prefix = " === FILE: "
        self.header_suffix = " ==="
        self.logger = logging.getLogger("copyast-sync")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(levelname)s | %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_header(self, path: str) -> str:
        return f"{self.header_prefix}{path}{self.header_suffix}"

    def get_ignore_file(self, path: str | None) -> Path:
        return Path(path or self.default_ignore_file)
