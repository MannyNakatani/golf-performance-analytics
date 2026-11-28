from pathlib import Path
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict

#from analytics import summarize_scores
#from schemas import ScoreSummaryRequest, ScoreSummaryResponse
from schemas import HealthResponse, RoundCreate, RoundResponse
import database
from contextlib import asynccontextmanager

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).with_name(".env"),
        env_file_encoding="utf-8",
        validate_default=True,
    )

    # default CORS origins
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield

app = FastAPI(title="Golf Performance API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)

@app.get("/api/v1/health", response_model=HealthResponse, tags=["system"])
def get_health() -> HealthResponse:
    return HealthResponse(status="healthy", service="golf-performance-api")

@app.post("/api/v1/rounds", response_model=RoundResponse,tags=["rounds"], status_code=201)
def create_round(new_round: RoundCreate) -> RoundResponse:
    return database.create_round(new_round)

@app.get("/api/v1/rounds", response_model=list[RoundResponse], tags=["rounds"])
def get_rounds() -> list[RoundResponse]:
    return database.get_rounds()

@app.get("/api/v1/rounds/{round_id}", response_model=RoundResponse,  tags=["rounds"])
def get_round(round_id: int) -> RoundResponse:
    retrieved_round = database.get_round(round_id)
    if retrieved_round is None:
        raise HTTPException(status_code=404, detail="Round not found")
    return retrieved_round

@app.put("/api/v1/rounds/{round_id}", response_model=RoundResponse, tags=["rounds"])
def update_round(round_id: int, updated_round: RoundCreate) -> RoundResponse:
    new_round = database.update_round(round_id, updated_round)
    if new_round is None:
        raise HTTPException(status_code=404, detail="Round not found")
    return new_round

@app.delete("/api/v1/rounds/{round_id}", tags=["rounds"], status_code=204)
def delete_round(round_id: int) -> Response:
    deleted = database.delete_round(round_id)
    if deleted is False:
        raise HTTPException(status_code=404, detail="Round not found")
    return Response(status_code=204)

# @app.post(
#     "/api/v1/analytics/score-summary",
#     response_model=ScoreSummaryResponse,
#     tags=["analytics"],
#     summary="Summarize golf scores",
#     description=(
#         "Calculate the round count, scoring average rounded to two decimal places "
#         "using ties-to-even rounding, best score, worst score, and score range "
#         "for 1 to 100 positive integer scores. Scores are processed in memory."
#     ),
# )
# async def get_score_summary(request: ScoreSummaryRequest) -> Response:
#     summary = summarize_scores(request.scores)
#     # Pydantic encodes Decimal as a string. Write the average as a JSON number
#     # directly to preserve its precision without converting to float.
#     other_fields = summary.model_dump_json(exclude={"scoring_average"})
#     average = format(summary.scoring_average, "f").rstrip("0").rstrip(".")
#     return Response(
#         content=f'{other_fields[:-1]},"scoring_average":{average}',
#         media_type="application/json",
#     )