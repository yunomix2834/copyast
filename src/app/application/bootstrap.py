from __future__ import annotations

from app.domain.services import CopyastService
from app.infrastructure.adapter.copyast_adapter import CopyastAdapter
from app.infrastructure.adapter.file_adapter import FileAdapter
from app.infrastructure.adapter.git_adapter import GitAdapter
from app.infrastructure.config import CopyastConfig


# Dependency Injection
class Bootstrap:
    @staticmethod
    def build_copyast_service() -> CopyastService:
        conf = CopyastConfig()
        fs = FileAdapter()
        repo = CopyastAdapter()
        git = GitAdapter()

        return CopyastService(fs=fs, repo=repo, git=git, conf=conf)
