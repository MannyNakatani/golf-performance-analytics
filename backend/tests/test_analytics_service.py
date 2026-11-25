from decimal import Decimal

import pytest

from analytics import summarize_scores


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        ([72, 75, 68, 73, 70], (5, "71.60", 68, 75, 7)),
        ([72], (1, "72.00", 72, 72, 0)),
        ([71, 71, 71], (3, "71.00", 71, 71, 0)),
        ([70, 70, 71], (3, "70.33", 70, 71, 1)),
        ([70] * 7 + [71], (8, "70.12", 70, 71, 1)),
        ([70] * 5 + [71] * 3, (8, "70.38", 70, 71, 1)),
    ],
)
def test_summarize_scores(
    scores: list[int], expected: tuple[int, str, int, int, int]
) -> None:
    count, average, best, worst, score_range = expected
    summary = summarize_scores(scores)

    assert summary.round_count == count
    assert summary.scoring_average == Decimal(average)
    assert summary.best_score == best
    assert summary.worst_score == worst
    assert summary.score_range == score_range
