"""
Database connection utilities.

This module centralizes how the application connects to the database so that
moving from SQLite to Postgres (e.g., AWS RDS) is just a config change.
"""

from sqlalchemy import create_engine
from pathlib import Path
import os
import yaml


def load_config():
    """
    Load configuration from config/settings.yaml if present.
    """
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "config" / "settings.yaml"
    if cfg_path.exists():
        with cfg_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def get_default_db_url() -> str:
    """
    Returns the default SQLAlchemy database URL.

    Precedence:
    1. DB_URL environment variable
    2. config/settings.yaml -> database.url
    3. SQLite file at db/solriver_mvp.db
    """
    env_url = os.getenv("DB_URL")
    if env_url:
        return env_url

    cfg = load_config()
    cfg_url = (cfg.get("database") or {}).get("url")
    if cfg_url:
        return cfg_url

    root = Path(__file__).resolve().parents[1]
    db_path = root / "db" / "solriver_mvp.db"
    return f"sqlite:///{db_path}"


def get_engine(db_url: str | None = None):
    """
    Create and return an SQLAlchemy engine.

    Parameters
    ----------
    db_url : str, optional
        If provided, use this URL; otherwise use the default.
    """
    url = db_url or get_default_db_url()
    return create_engine(url, future=True)
