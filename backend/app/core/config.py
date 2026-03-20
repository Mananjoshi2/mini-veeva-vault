from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/miniveeva"

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24h

    # Allowed frontend origins for CORS. Override via env as a JSON list, e.g.:
    # CORS_ORIGINS='["http://localhost:5173","https://your-domain.com"]'
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    SEED_ON_STARTUP: bool = True
    SEED_USER_PASSWORD: str = "Password123!"

    # Safety guard: prevent role escalation during signup unless explicitly enabled.
    ROLE_ASSIGNMENT_ON_SIGNUP: bool = False

