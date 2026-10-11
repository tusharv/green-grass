import os

from app.config import apply_env_file


def test_blank_process_env_uses_the_dotenv_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OLLAMA_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("OLLAMA_API_KEY", "")
    apply_env_file(env_file)
    assert os.environ["OLLAMA_API_KEY"] == "from-file"


def test_process_env_wins_over_the_dotenv_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OLLAMA_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("OLLAMA_API_KEY", "from-shell")
    apply_env_file(env_file)
    assert os.environ["OLLAMA_API_KEY"] == "from-shell"
