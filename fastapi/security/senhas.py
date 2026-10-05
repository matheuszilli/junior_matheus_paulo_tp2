import hashlib
import hmac
import secrets


ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000


def gerar_hash_senha(senha: str) -> str:
    salt = secrets.token_hex(16)
    hash_senha = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        ITERACOES,
    ).hex()

    return f"{ALGORITMO}${ITERACOES}${salt}${hash_senha}"


def verificar_senha(senha: str, valor_armazenado: str) -> bool:
    try:
        algoritmo, iteracoes, salt, hash_armazenado = valor_armazenado.split("$", 3)
    except ValueError:
        return False

    if algoritmo != ALGORITMO:
        return False

    hash_calculado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        int(iteracoes),
    ).hex()

    return hmac.compare_digest(hash_calculado, hash_armazenado)
