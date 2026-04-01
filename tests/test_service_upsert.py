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


def test_upsert_paths_adds_and_updates_entries(tmp_path: Path):
    root = tmp_path
    bundle = root / "copyast.txt"

    file_a = root / "a.txt"
    file_a.write_text("v1", encoding="utf-8")

    service = build_service()

    updated = service.upsert_paths(root, bundle, ["a.txt"])
    assert updated == 1

    text = bundle.read_text(encoding="utf-8")
    assert "a.txt" in text
    assert "v1" in text

    file_a.write_text("v2", encoding="utf-8")
    updated = service.upsert_paths(root, bundle, ["a.txt"])
    assert updated == 1

    text = bundle.read_text(encoding="utf-8")
    assert "v2" in text
    assert "v1" not in text


def test_export_skips_ignored_file(tmp_path: Path):
    root = tmp_path
    bundle = root / "copyast.txt"

    (root / "keep.txt").write_text("keep", encoding="utf-8")
    (root / "skip.log").write_text("skip", encoding="utf-8")

    service = build_service()
    matcher = CopyastIgnoreAdapter(["*.log"])

    count = service.export_directory(root, bundle, matcher)
    assert count == 1

    text = bundle.read_text(encoding="utf-8")
    assert "keep.txt" in text
    assert "skip.log" not in text