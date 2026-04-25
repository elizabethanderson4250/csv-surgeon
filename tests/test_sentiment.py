"""Tests for csv_surgeon.sentiment."""
import pytest
from csv_surgeon.sentiment import _score_text, _label, score_sentiment


# ---------------------------------------------------------------------------
# _score_text
# ---------------------------------------------------------------------------

def test_score_all_positive_words():
    assert _score_text("good great amazing") == 3


def test_score_all_negative_words():
    assert _score_text("bad terrible awful") == -3


def test_score_mixed_words():
    assert _score_text("good bad") == 0


def test_score_neutral_text():
    assert _score_text("the cat sat on the mat") == 0


def test_score_empty_string():
    assert _score_text("") == 0


def test_score_strips_punctuation():
    # "great!" should still match "great"
    assert _score_text("great!") == 1


def test_score_case_insensitive():
    assert _score_text("GOOD TERRIBLE") == 0


# ---------------------------------------------------------------------------
# _label
# ---------------------------------------------------------------------------

def test_label_positive():
    assert _label(2, 1, -1) == "positive"


def test_label_negative():
    assert _label(-2, 1, -1) == "negative"


def test_label_neutral_zero():
    assert _label(0, 1, -1) == "neutral"


def test_label_at_positive_threshold():
    assert _label(1, 1, -1) == "positive"


def test_label_at_negative_threshold():
    assert _label(-1, 1, -1) == "negative"


# ---------------------------------------------------------------------------
# score_sentiment (integration)
# ---------------------------------------------------------------------------

def make_rows(*texts):
    return [{"id": str(i), "review": t} for i, t in enumerate(texts)]


def test_score_sentiment_adds_score_column():
    rows = make_rows("good product")
    result = list(score_sentiment(rows, column="review"))
    assert "sentiment_score" in result[0]


def test_score_sentiment_adds_label_column():
    rows = make_rows("good product")
    result = list(score_sentiment(rows, column="review"))
    assert "sentiment_label" in result[0]


def test_score_sentiment_positive_row():
    rows = make_rows("amazing wonderful great")
    result = list(score_sentiment(rows, column="review"))
    assert result[0]["sentiment_label"] == "positive"
    assert int(result[0]["sentiment_score"]) == 3


def test_score_sentiment_negative_row():
    rows = make_rows("bad awful terrible")
    result = list(score_sentiment(rows, column="review"))
    assert result[0]["sentiment_label"] == "negative"
    assert int(result[0]["sentiment_score"]) == -3


def test_score_sentiment_neutral_row():
    rows = make_rows("the cat sat on the mat")
    result = list(score_sentiment(rows, column="review"))
    assert result[0]["sentiment_label"] == "neutral"
    assert int(result[0]["sentiment_score"]) == 0


def test_score_sentiment_custom_column_names():
    rows = make_rows("great")
    result = list(
        score_sentiment(rows, column="review", score_column="sc", label_column="lc")
    )
    assert "sc" in result[0]
    assert "lc" in result[0]


def test_score_sentiment_missing_column_treated_as_empty():
    rows = [{"id": "1"}]  # no 'review' key
    result = list(score_sentiment(rows, column="review"))
    assert result[0]["sentiment_label"] == "neutral"
    assert int(result[0]["sentiment_score"]) == 0


def test_score_sentiment_preserves_other_columns():
    rows = make_rows("good")
    result = list(score_sentiment(rows, column="review"))
    assert result[0]["id"] == "0"


def test_score_sentiment_multiple_rows():
    rows = make_rows("great", "bad", "just ok")
    result = list(score_sentiment(rows, column="review"))
    assert len(result) == 3
    labels = [r["sentiment_label"] for r in result]
    assert labels == ["positive", "negative", "neutral"]


def test_score_sentiment_custom_thresholds():
    rows = make_rows("good")  # score == 1
    # Raise bar so score=1 is still neutral
    result = list(
        score_sentiment(rows, column="review", pos_threshold=2, neg_threshold=-2)
    )
    assert result[0]["sentiment_label"] == "neutral"
