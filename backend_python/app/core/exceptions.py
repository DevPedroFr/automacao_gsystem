class IntegrationBaseException(Exception):
    """Base exception for all external API integration errors."""

    def __init__(self, message: str, provider: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.status_code = status_code


class ProviderUnavailableException(IntegrationBaseException):
    """Raised when an external provider service is unreachable or down."""

    def __init__(self, provider: str, details: str = ""):
        super().__init__(
            message=f"Provedor '{provider}' indisponível. {details}".strip(),
            provider=provider,
            status_code=503,
        )


class RateLimitExceededException(IntegrationBaseException):
    """Raised when an external provider quota or rate limit is hit."""

    def __init__(self, provider: str):
        super().__init__(
            message=f"Limite de requisições excedido para o provedor '{provider}'.",
            provider=provider,
            status_code=429,
        )


class InvalidCredentialsException(IntegrationBaseException):
    """Raised when API keys or tokens are missing or rejected."""

    def __init__(self, provider: str):
        super().__init__(
            message=f"Chave de API/Credenciais inválidas para o provedor '{provider}'.",
            provider=provider,
            status_code=401,
        )
