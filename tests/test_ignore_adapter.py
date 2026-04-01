from app.infrastructure.adapter.copyast_adapter import CopyastIgnoreAdapter


def test_ignore_directory_pattern():
    matcher = CopyastIgnoreAdapter([".idea/"])

    assert matcher.is_ignore(".idea")
    assert matcher.is_ignore(".idea/workspace.xml")
    assert not matcher.is_ignore("src/app/main.py")


def test_ignore_wildcard_pattern():
    matcher = CopyastIgnoreAdapter(["*.log"])

    assert matcher.is_ignore("app.log")
    assert matcher.is_ignore("logs/error.log")
    assert not matcher.is_ignore("logs/error.txt")


def test_ignore_exact_file_pattern():
    matcher = CopyastIgnoreAdapter([".env"])

    assert matcher.is_ignore(".env")
    assert matcher.is_ignore("config/.env")
    assert not matcher.is_ignore("config/.env.example")