from pathlib import Path

from app.domain.services import CopyastService
from app.infrastructure.adapter.copyast_adapter import CopyastAdapter, CopyastIgnoreAdapter
from app.infrastructure.adapter.file_adapter import FileAdapter
from app.infrastructure.adapter.git_adapter import GitAdapter
from app.infrastructure.config import CopyastConfig


def build_service() -> CopyastService:
    return CopyastService(
        fs=FileAdapter(),
        repo=CopyastAdapter(),
        git=GitAdapter(),
        conf=CopyastConfig(),
    )


def test_export_multi_root_prefixes_alias(tmp_path: Path):
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    repo_a.mkdir()
    repo_b.mkdir()

    (repo_a / "main.py").write_text("print('a')", encoding="utf-8")
    (repo_b / "main.py").write_text("print('b')", encoding="utf-8")

    bundle = tmp_path / "bundle.txt"
    service = build_service()

    roots = service.parse_root_specs(
        [f"app={repo_a}", f"ci={repo_b}"]
    )

    count = service.export_directories(
        roots=roots,
        export_file=bundle,
        ignore_by_alias={
            "app": CopyastIgnoreAdapter([]),
            "ci": CopyastIgnoreAdapter([]),
        },
        append=False,
    )

    assert count == 2

    text = bundle.read_text(encoding="utf-8")
    assert "=== FILE: app/main.py ===" in text
    assert "=== FILE: ci/main.py ===" in text
    assert "print('a')" in text
    assert "print('b')" in text


def test_export_append_merges_existing_bundle(tmp_path: Path):
    repo_a = tmp_path / "repo_a"
    repo_b = tmp_path / "repo_b"
    repo_a.mkdir()
    repo_b.mkdir()

    (repo_a / "a.txt").write_text("A", encoding="utf-8")
    (repo_b / "b.txt").write_text("B", encoding="utf-8")

    bundle = tmp_path / "bundle.txt"
    service = build_service()

    roots_a = service.parse_root_specs([f"app={repo_a}"])
    service.export_directories(
        roots=roots_a,
        export_file=bundle,
        ignore_by_alias={"app": CopyastIgnoreAdapter([])},
        append=False,
    )

    roots_b = service.parse_root_specs([f"ci={repo_b}"])
    service.export_directories(
        roots=roots_b,
        export_file=bundle,
        ignore_by_alias={"ci": CopyastIgnoreAdapter([])},
        append=True,
    )

    text = bundle.read_text(encoding="utf-8")
    assert "=== FILE: a.txt ===" in text or "=== FILE: app/a.txt ===" in text
    assert "=== FILE: b.txt ===" in text or "=== FILE: ci/b.txt ===" in text