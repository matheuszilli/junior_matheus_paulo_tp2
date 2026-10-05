import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select

from models.database import Usuario, get_session
from security.senhas import verificar_senha


CHAVE_SECRETA = os.environ.get("JWT_SECRET") or secrets.token_urlsafe(48)
if len(CHAVE_SECRETA) < 32:
    raise RuntimeError("JWT_SECRET deve possuir pelo menos 32 caracteres")
ALGORITMO = "HS256"
MINUTOS_EXPIRACAO = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def autenticar_usuario(
        username: str,
        password: str,
        session: Session,
) -> Usuario | None:

    statement = select(Usuario).where(Usuario.username == username)

    usuario = session.exec(statement).first()

    if usuario is None:
        return None

    if not verificar_senha(password, usuario.password_hash):
        return None

    return usuario


def criar_token(usuario: Usuario) -> str:
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=MINUTOS_EXPIRACAO
    )

    dados_token = {
        "sub": usuario.username,
        "user_id": usuario.id,
        "exp": expiracao,
    }

    return jwt.encode(
        dados_token,
        CHAVE_SECRETA,
        algorithm=ALGORITMO,
    )


def validar_token(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[Session, Depends(get_session)],
) -> Usuario:

    erro_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        dados_token = jwt.decode(
            token,
            CHAVE_SECRETA,
            algorithms=[ALGORITMO],
            options={"require": ["sub", "user_id", "exp"]},
        )

    except InvalidTokenError as erro:
        raise erro_credenciais from erro

    username = dados_token.get("sub")

    if username is None:
        raise erro_credenciais

    statement = select(Usuario).where(
        Usuario.username == username
    )

    usuario = session.exec(statement).first()

    if usuario is None:
        raise erro_credenciais

    if dados_token.get("user_id") != usuario.id:
        raise erro_credenciais

    return usuario
