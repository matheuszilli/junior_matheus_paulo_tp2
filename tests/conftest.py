import os
import sys
import tempfile
from pathlib import Path


FASTAPI_DIR = Path(__file__).resolve().parents[1] / "fastapi"
sys.path.insert(0, str(FASTAPI_DIR))

TEST_DIR = Path(tempfile.mkdtemp(prefix="tp2-testes-"))
os.environ["DATABASE_PATH"] = str(TEST_DIR / "test_database.db")
os.environ["JWT_SECRET"] = "chave-exclusiva-dos-testes-com-mais-de-32-caracteres"

from sqlite_database import criar_banco


criar_banco(recriar=True)
