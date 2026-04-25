"""Simple lexicon-based sentiment scoring for a text column."""
from __future__ import annotations

from typing import Iterable, Iterator

# Minimal built-in word lists so the module has zero external dependencies.
_POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "wonderful", "fantastic",
    "love", "best", "happy", "positive", "awesome", "nice", "perfect",
    "brilliant", "superb", "outstanding", "enjoy", "liked", "pleased",
    "glad", "delighted", "incredible", "beautiful", "helpful", "fast",
}

_NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "worst", "hate", "poor",
    "negative", "ugly", "broken", "slow", "useless", "disappointing",
    "annoying", "frustrating", "failed", "wrong", "sad", "angry",
    "dreadful", "mediocre", "inferior", "defective", "unpleasant",
}


def _score_text(text: str) -> int:
    """Return a raw sentiment score: positive words +1, negative words -1."""
    words = text.lower().split()
    score = 0
    for word in words:
        clean = word.strip(".,!?;:\"'()[]")
        if clean in _POSITIVE_WORDS:
            score += 1
        elif clean in _NEGATIVE_WORDS:
            score -= 1
    return score


def _label(score: int, pos_threshold: int, neg_threshold: int) -> str:
    if score >= pos_threshold:
        return "positive"
    if score <= neg_threshold:
        return "negative"
    return "neutral"


def score_sentiment(
    rows: Iterable[dict],
    column: str,
    score_column: str = "sentiment_score",
    label_column: str = "sentiment_label",
    pos_threshold: int = 1,
    neg_threshold: int = -1,
) -> Iterator[dict]:
    """Yield rows enriched with a numeric sentiment score and a text label.

    Parameters
    ----------
    rows:
        Iterable of dicts (CSV rows).
    column:
        Name of the text column to analyse.
    score_column:
        Output column for the integer score.
    label_column:
        Output column for the string label (positive / neutral / negative).
    pos_threshold:
        Minimum score to be labelled *positive*.
    neg_threshold:
        Maximum score to be labelled *negative* (should be <= 0).
    """
    for row in rows:
        new_row = dict(row)
        text = row.get(column, "") or ""
        score = _score_text(text)
        new_row[score_column] = str(score)
        new_row[label_column] = _label(score, pos_threshold, neg_threshold)
        yield new_row
