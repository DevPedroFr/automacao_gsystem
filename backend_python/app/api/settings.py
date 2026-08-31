"""
Router /api/settings — Gerenciamento de configurações da aplicação.
Porta fiel das rotas do backend Node.js (routes/settings.js).
"""
import logging
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Setting

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/settings", tags=["Configurações"])


@router.get("", summary="Lista todas as configurações")
def list_settings(db: Session = Depends(get_db)):
    """GET /api/settings — Retorna todas as configurações em formato chave-valor."""
    rows = db.query(Setting).all()
    settings_dict = {row.key: row.value for row in rows}
    return {"data": settings_dict}


@router.post("", summary="Salva ou atualiza configurações")
def save_settings(body: dict[str, Any], db: Session = Depends(get_db)):
    """POST /api/settings — Grava ou atualiza configurações (upsert por chave)."""
    if not body or not isinstance(body, dict):
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": "Payload inválido"})

    for key, value in body.items():
        val_str = "" if value is None else str(value).strip()
        existing = db.query(Setting).filter(Setting.key == key).first()
        if existing:
            existing.value = val_str
        else:
            db.add(Setting(key=key, value=val_str))

    db.commit()

    rows = db.query(Setting).all()
    settings_dict = {row.key: row.value for row in rows}
    return {"data": settings_dict, "message": "Configurações salvas com sucesso"}


@router.post("/test-webhook", summary="Dispara teste de webhook")
async def test_webhook(body: dict[str, Any], db: Session = Depends(get_db)):
    """POST /api/settings/test-webhook — Envia um payload de teste para a URL de webhook configurada."""
    webhook_url = body.get("webhook_url")

    if not webhook_url:
        row = db.query(Setting).filter(Setting.key == "webhook_url").first()
        webhook_url = row.value if row else None

    if not webhook_url:
        raise HTTPException(
            status_code=400,
            detail={"error": "validation_error", "message": "Nenhuma URL de webhook configurada."},
        )

    payload = {
        "event": "test_connection",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "data": {
            "message": "Conexão de teste realizada com sucesso da plataforma CONSULTINGS APD!",
            "system": "CONSULTINGS APD Automation",
            "status": "active",
        },
    }

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            response = await client.post(webhook_url, json=payload)

        if response.is_success:
            return {"success": True, "message": "Webhook de teste enviado e aceito com sucesso pelo receptor!"}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "success": False,
                    "message": f"O receptor retornou erro (Status {response.status_code})",
                    "details": response.text,
                },
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail={"success": False, "message": "Timeout ao conectar com o webhook."})
    except Exception as err:
        raise HTTPException(status_code=500, detail={"success": False, "message": f"Falha ao conectar com o webhook: {err}"})
