import os
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret-key")
# Ruta absoluta fuera de /mnt/c: en WSL, SQLite sobre un disco de Windows puede
# fallar con "disk I/O error" por el locking de archivos.
_test_db_dir = Path.home() / ".local" / "share" / "dyp-lasercore"
_test_db_dir.mkdir(parents=True, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_dir / 'test.db'}"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
