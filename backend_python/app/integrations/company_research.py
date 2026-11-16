import logging
import math
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import urlparse

from google import genai
from google.genai import types
from google.genai._interactions import APIError as InteractionsAPIError
from google.genai.errors import APIError as LegacyAPIError
from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings

logger = logging.getLogger(__name__)
MAX_429_RETRIES = 1
MAX_AUTOMATIC_RETRY_DELAY_SECONDS = 60


class CompanyResearchError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 502,
        retry_after_seconds: Optional[int] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after_seconds = retry_after_seconds


class CompanyResearchFields(BaseModel):
    responsible_name: Optional[str] = Field(
        default=None,
        description="Nome do responsável quando confirmado em fonte pública.",
    )
    responsible_role: Optional[str] = Field(
        default=None,
        description="Cargo do responsável, por exemplo proprietário ou diretor.",
    )
    public_business_phone: Optional[str] = Field(
        default=None,
        description="Telefone comercial publicado pela própria empresa.",
    )
    opening_date: Optional[str] = Field(
        default=None,
        description="Data ou ano de abertura, conforme registrado por fonte pública.",
    )


class CompanyResearchIntegration:
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.model = model or settings.GEMINI_MODEL
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )

    def search_company(self, name: str, address: str) -> dict:
        interaction = self._create_interaction(name, address)
        output_text = interaction.output_text
        if not output_text:
            raise CompanyResearchError("O Gemini não retornou dados para esta empresa.")

        try:
            research = CompanyResearchFields.model_validate_json(output_text)
        except ValidationError as err:
            raise CompanyResearchError("O Gemini retornou dados em formato inválido.") from err

        return {
            **research.model_dump(),
            "sources": self._extract_sources(interaction),
        }

    def _create_interaction(self, name: str, address: str):
        input_text = (
            f"Pesquise informações públicas desta empresa:\n"
            f"Nome: {name}\n"
            f"Endereço: {address or 'Não informado'}"
        )
        system_instruction = (
            "Você pesquisa informações empresariais apenas em fontes públicas na internet. "
            "Identifique o responsável (proprietário, diretor ou equivalente), seu cargo, "
            "o telefone comercial publicado pela própria empresa e a data ou ano de abertura. "
            "Não procure nem retorne telefone pessoal, privado ou não publicado como contato "
            "comercial. Não deduza nem invente informações. Se um dado não puder ser confirmado, "
            "retorne null. Use fontes oficiais sempre que disponíveis."
        )

        for attempt in range(MAX_429_RETRIES + 1):
            try:
                return self.client.interactions.create(
                    model=self.model,
                    input=input_text,
                    system_instruction=system_instruction,
                    tools=[{"type": "google_search"}],
                    generation_config={
                        "max_output_tokens": 4096,
                        "thinking_level": "high",
                    },
                    response_format={
                        "type": "text",
                        "mime_type": "application/json",
                        "schema": CompanyResearchFields.model_json_schema(),
                    },
                    store=False,
                )
            except (LegacyAPIError, InteractionsAPIError) as err:
                status_code = getattr(err, "status_code", None) or getattr(err, "code", None)
                if status_code != 429:
                    logger.warning(
                        "Gemini API retornou erro na busca empresarial (HTTP %s, %s)",
                        status_code,
                        getattr(err, "status", None),
                    )
                    raise CompanyResearchError(
                        f"Não foi possível concluir a pesquisa no Gemini (HTTP {status_code})."
                    ) from err

                retry_after = self._retry_after_seconds(err)
                if self._is_quota_exhausted(err) and (
                    retry_after is None
                    or retry_after > MAX_AUTOMATIC_RETRY_DELAY_SECONDS
                ):
                    logger.warning("Gemini recusou a busca por cota esgotada (HTTP 429)")
                    raise CompanyResearchError(
                        self._rate_limit_message(retry_after),
                        status_code=429,
                        retry_after_seconds=retry_after,
                    ) from err

                if (
                    attempt == MAX_429_RETRIES
                    or (
                        retry_after is not None
                        and retry_after > MAX_AUTOMATIC_RETRY_DELAY_SECONDS
                    )
                ):
                    logger.warning(
                        "Gemini limitou a busca empresarial (HTTP 429, %s)",
                        getattr(err, "status", None),
                    )
                    raise CompanyResearchError(
                        self._rate_limit_message(retry_after),
                        status_code=429,
                        retry_after_seconds=retry_after,
                    ) from err

                delay = retry_after if retry_after is not None else 2**attempt
                logger.warning(
                    "Gemini retornou HTTP 429; nova tentativa %s/%s em %.1fs",
                    attempt + 1,
                    MAX_429_RETRIES,
                    delay,
                )
                time.sleep(delay)

        raise CompanyResearchError("Não foi possível concluir a pesquisa no Gemini.")

    @classmethod
    def _retry_after_seconds(cls, error: Exception) -> Optional[int]:
        headers = getattr(getattr(error, "response", None), "headers", None)
        if headers:
            delay = cls._parse_retry_delay(headers.get("Retry-After"))
            if delay is not None:
                return delay
            retry_after_ms = headers.get("retry-after-ms")
            if retry_after_ms is not None:
                try:
                    return max(0, math.ceil(float(retry_after_ms) / 1000))
                except (TypeError, ValueError):
                    pass

        details = getattr(error, "details", None)
        if details is None:
            details = getattr(error, "body", None)
        pending = [details]
        while pending:
            value = pending.pop()
            if isinstance(value, dict):
                for key, nested in value.items():
                    if key.lower() in {"retrydelay", "retry_after", "retry-after"}:
                        delay = cls._parse_retry_delay(nested)
                        if delay is not None:
                            return delay
                    if isinstance(nested, (dict, list)):
                        pending.append(nested)
            elif isinstance(value, list):
                pending.extend(value)
        return None

    @staticmethod
    def _is_quota_exhausted(error: Exception) -> bool:
        body = getattr(error, "body", None)
        error_text = f"{body or ''} {error}".lower()
        return (
            "exceeded your current quota" in error_text
            or "check your plan and billing details" in error_text
        )

    @staticmethod
    def _parse_retry_delay(value) -> Optional[int]:
        if value is None:
            return None
        match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*s?\s*", str(value), re.IGNORECASE)
        if match:
            return max(0, round(float(match.group(1))))
        try:
            retry_at = parsedate_to_datetime(str(value))
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return max(0, round((retry_at - datetime.now(timezone.utc)).total_seconds()))

    @staticmethod
    def _rate_limit_message(retry_after: Optional[int]) -> str:
        message = (
            "O Gemini limitou as requisições (HTTP 429). Aguarde antes de tentar novamente "
            "e confira as cotas do modelo e do projeto vinculado à chave; uma chave paga "
            "também está sujeita a limites."
        )
        if retry_after:
            message += f" O provedor recomenda aguardar {retry_after} segundos."
        return message

    @staticmethod
    def _extract_sources(interaction) -> list[dict[str, str]]:
        sources = []
        seen_urls = set()

        for step in interaction.steps or []:
            if step.type != "model_output":
                continue
            for content_block in step.content or []:
                if content_block.type != "text":
                    continue
                for annotation in content_block.annotations or []:
                    if annotation.type != "url_citation" or not annotation.url:
                        continue
                    parsed_url = urlparse(annotation.url)
                    if parsed_url.scheme not in {"http", "https"} or annotation.url in seen_urls:
                        continue
                    seen_urls.add(annotation.url)
                    sources.append({
                        "title": annotation.title or annotation.url,
                        "url": annotation.url,
                    })

        return sources
