from pathlib import Path
from unittest.mock import Mock, patch

from app.infrastructure.adapter.git_adapter import GitAdapter


def test_is_git_repo_true(tmp_path: Path):
    adapter = GitAdapter()

    mock_result = Mock(returncode=0, stdout="true\n")
    with patch("subprocess.run", return_value=mock_result):
        assert adapter.is_git_repo(tmp_path) is True


def test_dict_changed_files_parses_status(tmp_path: Path):
    adapter = GitAdapter()

    mock_result = Mock(
        returncode=0,
        stdout=" M src/app/main.py\n?? tests/test_new.py\n D old.txt\n",
        stderr="",
    )

    with patch("subprocess.run", return_value=mock_result):
        result = adapter.dict_changed_files(tmp_path)

    assert result["modified"] == ["src/app/main.py"]
    assert result["untracked"] == ["tests/test_new.py"]
    assert result["deleted"] == ["old.txt"]
