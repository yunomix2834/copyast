from pathlib import Path

from app.domain.services import CopyastService
from app.infrastructure.adapter.copyast_adapter import (
    CopyastAdapter,
    CopyastIgnoreAdapter,
)
from app.infrastructure.adapter.file_adapter import FileAdapter
from app.infrastructure.adapter.git_adapter import GitAdapter
from app.infrastructure.config import CopyastConfig


def test_export_and_delete(tmp_path: Path):
    root = tmp_path
    (root / "a.txt").write_text("hello", encoding="utf-8")
    (root / "b.txt").write_text("world", encoding="utf-8")
    bundle = root / "bundle.txt"

    service = CopyastService(
        fs=FileAdapter(),
        repo=CopyastAdapter(),
        git=GitAdapter(),
        conf=CopyastConfig(),
    )
    matcher = CopyastIgnoreAdapter([])
    roots = service.parse_root_specs([str(root)])

    count = service.export_directories(
        roots=roots,
        export_file=bundle,
        ignore_by_alias={roots[0].alias: matcher},
        append=False,
    )
    assert count == 2

    deleted = service.delete_targets(bundle, files=["a.txt"], dirs=[])
    assert deleted == 1

    text = bundle.read_text(encoding="utf-8")
    assert "a.txt" not in text
    assert "b.txt" in text
