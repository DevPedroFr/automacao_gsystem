import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

ACCESS_LEVELS = {"spy_car", "g_system", "diretoria"}
TENANT_ACCESS_LEVELS = {"spy_car", "g_system"}
TOKEN_LIFETIME_SECONDS = 12 * 60 * 60
USERS_FILE = Path(__file__).resolve().parents[2] / "users.json"
_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    username: str
    access_level: str


class UserStoreError(Exception):
    pass


def allowed_tenants(user: AuthenticatedUser) -> tuple[str, ...]:
    if user.access_level == "diretoria":
        return ("spy_car", "g_system")
    if user.access_level in TENANT_ACCESS_LEVELS:
        return (user.access_level,)
    raise HTTPException(status_code=403, detail={"message": "Nível de acesso inválido."})


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=64,
    )
    return f"scrypt$16384$8$1${salt.hex()}${derived_key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, n, r, p, salt_hex, key_hex = stored_hash.split("$")
        if algorithm != "scrypt":
            return False
        expected_key = bytes.fromhex(key_hex)
        actual_key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected_key),
        )
    except (AttributeError, ValueError, TypeError):
        return False
    return hmac.compare_digest(actual_key, expected_key)


def load_users() -> list[dict]:
    try:
        users = json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError as err:
        raise UserStoreError(
            f"Arquivo de usuários não encontrado: {USERS_FILE}. Crie-o como uma lista JSON."
        ) from err
    except (OSError, json.JSONDecodeError) as err:
        raise UserStoreError("Não foi possível ler o arquivo de usuários JSON.") from err

    if not isinstance(users, list):
        raise UserStoreError("O arquivo de usuários deve conter uma lista JSON.")

    seen_usernames = set()
    for user in users:
        if not isinstance(user, dict):
            raise UserStoreError("Cada usuário deve ser um objeto JSON.")
        username = user.get("username")
        password_hash = user.get("password_hash")
        access_level = user.get("access_level")
        if (
            not isinstance(username, str)
            or not username.strip()
            or not isinstance(password_hash, str)
            or not isinstance(access_level, str)
            or access_level not in ACCESS_LEVELS
        ):
            raise UserStoreError(
                "Cada usuário precisa de username, password_hash e access_level válido."
            )
        normalized_username = username.strip().casefold()
        if normalized_username in seen_usernames:
            raise UserStoreError("O arquivo contém nomes de usuário duplicados.")
        seen_usernames.add(normalized_username)

    return users


def create_access_token(username: str, access_level: str, expires_in: int = TOKEN_LIFETIME_SECONDS) -> str:
    if not settings.AUTH_SECRET:
        raise RuntimeError("AUTH_SECRET não está configurada.")
    header = _encode_segment({"alg": "HS256", "typ": "JWT"})
    payload = _encode_segment({
        "iss": "automacao-de-leads",
        "sub": username,
        "access_level": access_level,
        "exp": int(time.time()) + expires_in,
    })
    signing_input = f"{header}.{payload}"
    signature = hmac.new(
        settings.AUTH_SECRET.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_encode_bytes(signature)}"


def decode_access_token(token: str) -> AuthenticatedUser:
    if not settings.AUTH_SECRET:
        raise HTTPException(status_code=503, detail={"message": "AUTH_SECRET não está configurada."})

    try:
        header_segment, payload_segment, signature_segment = token.split(".")
        signing_input = f"{header_segment}.{payload_segment}"
        expected_signature = hmac.new(
            settings.AUTH_SECRET.encode("utf-8"),
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(_decode_segment(signature_segment), expected_signature):
            raise ValueError("Invalid token signature")

        header = _decode_json_segment(header_segment)
        payload = _decode_json_segment(payload_segment)
        if header.get("alg") != "HS256" or payload.get("iss") != "automacao-de-leads":
            raise ValueError("Invalid token claims")
        if not isinstance(payload.get("exp"), int) or payload["exp"] <= int(time.time()):
            raise ValueError("Expired token")

        username = payload.get("sub")
        access_level = payload.get("access_level")
        if not isinstance(username, str) or access_level not in ACCESS_LEVELS:
            raise ValueError("Invalid user claims")
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=401,
            detail={"message": "Sessão inválida ou expirada."},
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    return AuthenticatedUser(username=username, access_level=access_level)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={"message": "Autenticação obrigatória."},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_access_token(credentials.credentials)


def _encode_segment(value: dict) -> str:
    return _encode_bytes(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def _encode_bytes(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode_segment(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _decode_json_segment(value: str) -> dict:
    decoded = json.loads(_decode_segment(value).decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("Invalid token segment")
    return decoded
