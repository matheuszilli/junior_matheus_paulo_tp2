import argparse
import os
import sqlite3
from pathlib import Path

from security.senhas import gerar_hash_senha


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(
    os.environ.get("DATABASE_PATH", BASE_DIR / "database.db")
).resolve()


def criar_banco(recriar: bool = False):
    if recriar:
        DATABASE_PATH.unlink(missing_ok=True)

    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.execute("PRAGMA foreign_keys=ON")
    cursor = conexao.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            intencao TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
        """
    )

    usuarios = [
        (1, "admin", gerar_hash_senha("infnet")),
        (2, "usuario2", gerar_hash_senha("teste123")),
    ]

    cursor.executemany(
        """
        INSERT INTO users (id, username, password_hash)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET password_hash=excluded.password_hash
        """,
        usuarios,
    )

    predictions = [
        (1, "Quero meu dinheiro de volta", "Refund request", 1),
        (2, "Meu produto ainda não chegou", "Delivery issue", 2),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO predictions (id, texto, intencao, owner_id)
        VALUES (?, ?, ?, ?)
        """,
        predictions,
    )

    conexao.commit()
    conexao.close()

    print(f"Banco criado e populado em: {DATABASE_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recriar",
        action="store_true",
        help="Remove o banco existente antes de criar os dados de exemplo.",
    )
    argumentos = parser.parse_args()
    criar_banco(recriar=argumentos.recriar)
