from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AfterValidator
from pydantic_settings import BaseSettings, SettingsConfigDict

from analytics import summarize_scores
from schemas import HealthResponse, ScoreSummaryRequest, ScoreSummaryResponse


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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).with_name(".env"),
        env_file_encoding="utf-8",
        validate_default=True,
    )

    cors_origins: list[Annotated[str, AfterValidator(validate_origin)]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
app = FastAPI(title="Golf Performance API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
)


@app.get("/api/v1/health", response_model=HealthResponse, tags=["health"])
async def get_health() -> HealthResponse:
    return HealthResponse(status="healthy", service="golf-performance-api")


@app.post(
    "/api/v1/analytics/score-summary",
    response_model=ScoreSummaryResponse,
    tags=["analytics"],
    summary="Summarize golf scores",
    description=(
        "Calculate the round count, scoring average rounded to two decimal places "
        "using ties-to-even rounding, best score, worst score, and score range "
        "for 1 to 100 positive integer scores. Scores are processed in memory."
    ),
)
async def get_score_summary(request: ScoreSummaryRequest) -> Response:
    summary = summarize_scores(request.scores)
    # Pydantic encodes Decimal as a string. Write the average as a JSON number
    # directly to preserve its precision without converting to float.
    other_fields = summary.model_dump_json(exclude={"scoring_average"})
    average = format(summary.scoring_average, "f").rstrip("0").rstrip(".")
    return Response(
        content=f'{other_fields[:-1]},"scoring_average":{average}}}',
        media_type="application/json",
    )
