from collections.abc import Sequence
from decimal import Decimal
from fractions import Fraction

from schemas import ScoreSummaryResponse


def summarize_scores(scores: Sequence[int]) -> ScoreSummaryResponse:
    """Summarize a non-empty sequence of validated scores."""
    round_count = len(scores)
    average_in_hundredths = round(Fraction(sum(scores) * 100, round_count))
    whole, hundredths = divmod(average_in_hundredths, 100)
    best_score = min(scores)
    worst_score = max(scores)

    return ScoreSummaryResponse(
        round_count=round_count,
        scoring_average=Decimal(f"{whole}.{hundredths:02d}"),
        best_score=best_score,
        worst_score=worst_score,
        score_range=worst_score - best_score,
    )
