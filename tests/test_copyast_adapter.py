from pathlib import Path

from app.domain.models import CopyastEntry
from app.infrastructure.adapter.copyast_adapter import CopyastAdapter


def test_save_and_load_bundle_roundtrip(tmp_path: Path):
    bundle = tmp_path / "copyast.txt"
    adapter = CopyastAdapter()

    entries = [
        CopyastEntry(path="src/app/main.py", content="print('hello')"),
        CopyastEntry(path="README.md", content="# copyast"),
    ]

    adapter.save(bundle, entries)
    loaded = adapter.load(bundle)

    assert len(loaded) == 2
    assert loaded[0].path == "README.md"
    assert loaded[0].content == "# copyast"
    assert loaded[1].path == "src/app/main.py"
    assert loaded[1].content == "print('hello')"
