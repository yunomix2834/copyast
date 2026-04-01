from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from app.domain.models import CopyastEntry


class CopyastPort(ABC):
    @abstractmethod
    def load(self, path: Path) -> list[CopyastEntry]:
        raise NotImplementedError

    @abstractmethod
    def save(self, path: Path, entries: list[CopyastEntry]) -> None:
        raise NotImplementedError


class CopyastIgnorePort(ABC):
    @abstractmethod
    def is_ignore(self, relative_path: str, is_directory: bool = False) -> bool:
        raise NotImplementedError


class GitPort(ABC):
    @abstractmethod
    def is_git_repo(self, root: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def dict_changed_files(self, root: Path) -> dict[str, list[str]]:
        """
        Return a dict:
        {
            'modified': [...],
            'deleted': [...],
            'untracked': [...]
        }
        paths are relative to root
        """
        raise NotImplementedError


class FilePort(ABC):
    @abstractmethod
    def read_text(self, path: Path) -> str:
        raise NotImplementedError

    @abstractmethod
    def write_text(self, path: Path, content: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_exists(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def is_binary(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def walk_files(self, root: Path) -> Iterable[Path]:
        raise NotImplementedError
