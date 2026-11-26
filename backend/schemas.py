from decimal import Decimal
from typing import Annotated, Literal, Self
from datetime import date
from pydantic import BaseModel, Field, WithJsonSchema, model_validator

Holes = Annotated[int, Field(strict=True, ge=0, le=18)]
PositiveInt = Annotated[int, Field(strict=True, gt=0)]
UnsignedInt = Annotated[int, Field(strict=True, ge=0)]
Name = Annotated[str, Field(min_length=1)]

class HealthResponse(BaseModel):
    status: Literal["healthy"]
    service: Literal["golf-performance-api"]

class RoundCreate(BaseModel):
    date: date
    course_name: Name
    par: PositiveInt
    score: PositiveInt
    putts: UnsignedInt
    fairway_hit: Holes
    fairways_possible: Holes
    gir: Holes
    penalty_strokes: UnsignedInt

    @model_validator(mode="after")
    def validate_fairway_hits(self) -> Self:
        if self.fairway_hit > self.fairways_possible:
            raise ValueError("fairway_hit cannot be more than fairways_possible")
        return self

class RoundResponse(RoundCreate):
    id: int

class ScoreSummaryRequest(BaseModel):
    scores: list[PositiveInt] = Field(min_length=1, max_length=100)

class ScoreSummaryResponse(BaseModel):
    round_count: UnsignedInt
    scoring_average: Annotated[Decimal, WithJsonSchema({"type": "number"})]
    best_score: PositiveInt
    worst_score: PositiveInt
    score_range: UnsignedInt
