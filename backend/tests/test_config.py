from pathlib import Path

from lca.config import Paths


def test_explicit_base_wins(tmp_path):
    assert Paths(base=tmp_path).base_dir() == tmp_path
    assert Paths(base=tmp_path).db_path() == tmp_path / "data" / "lca.db"


def test_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("LCA_BASE_DIR", str(tmp_path))
    assert Paths().base_dir() == tmp_path
    assert Paths().default_engine_path().parent == tmp_path / "stockfish"


def test_dev_default_is_repo_root(monkeypatch):
    monkeypatch.delenv("LCA_BASE_DIR", raising=False)
    root = Paths().base_dir()
    assert (root / "backend" / "lca").is_dir()
    assert Path(__file__).resolve().is_relative_to(root)
