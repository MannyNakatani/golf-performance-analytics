from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, WithJsonSchema

Score = Annotated[int, Field(strict=True, gt=0)]


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    service: Literal["golf-performance-api"]


class ScoreSummaryRequest(BaseModel):
    scores: list[Score] = Field(min_length=1, max_length=100)


class ScoreSummaryResponse(BaseModel):
    round_count: int
    scoring_average: Annotated[Decimal, WithJsonSchema({"type": "number"})]
    best_score: int
    worst_score: int
    score_range: int
