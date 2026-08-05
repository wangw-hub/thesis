from pathlib import Path


def test_repository_has_no_password_logging():
    root=Path(__file__).resolve().parents[3]/"src"/"epoch_auth_r3"/"database"
    text="\n".join(p.read_text("utf-8") for p in root.glob("*.py"))
    assert "logger" not in text
    assert "R3_I4_DB_PASSWORD" not in text
