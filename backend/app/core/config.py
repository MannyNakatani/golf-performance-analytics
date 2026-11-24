from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import AfterValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def validate_origin(value: str) -> str:
    origin = urlsplit(value)
    if (
        origin.scheme not in {"http", "https"}
        or not origin.hostname
        or "*" in value
        or value != f"{origin.scheme}://{origin.netloc}"
        or origin.username is not None
        or any(char.isspace() for char in value)
    ):
        raise ValueError("Use an explicit HTTP(S) origin, such as http://localhost:5173")
    return value


Origin = Annotated[str, AfterValidator(validate_origin)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        validate_default=True,
    )

    cors_origins: list[Origin] = ["http://localhost:5173", "http://127.0.0.1:5173"]
