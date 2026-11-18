import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.auth import (
    AuthenticatedUser,
    UserStoreError,
    create_access_token,
    get_current_user,
    load_users,
    verify_password,
)
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=1024)


@router.post("/login", summary="Autentica um usuário")
def login(body: LoginRequest):
    if not settings.AUTH_SECRET:
        raise HTTPException(
            status_code=503,
            detail={"message": "AUTH_SECRET não está configurada no ambiente do backend."},
        )

    try:
        users = load_users()
    except UserStoreError as err:
        logger.error("Configuração do arquivo de usuários inválida: %s", err)
        raise HTTPException(status_code=503, detail={"message": str(err)}) from err

    normalized_username = body.username.strip().casefold()
    user = next(
        (
            entry for entry in users
            if entry["username"].strip().casefold() == normalized_username
        ),
        None,
    )
    if user is None or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail={"message": "Usuário ou senha incorretos."})

    token = create_access_token(user["username"].strip(), user["access_level"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user["username"].strip(),
            "access_level": user["access_level"],
        },
    }


@router.get("/me", summary="Retorna o usuário autenticado")
def current_user(user: AuthenticatedUser = Depends(get_current_user)):
    return {"data": {"username": user.username, "access_level": user.access_level}}
