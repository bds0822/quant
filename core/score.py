import pandas as pd


def score_13612U(data: pd.DataFrame) -> pd.DataFrame:
    m1 = data.pct_change(periods=1)
    m3 = data.pct_change(periods=3)
    m6 = data.pct_change(periods=6)
    m12 = data.pct_change(periods=12)
    score = (m1 + m3 + m6 + m12).dropna(axis=0)
    return score


def score_13612W(data: pd.DataFrame) -> pd.DataFrame:
    m1 = data.pct_change(periods=1)
    m3 = data.pct_change(periods=3)
    m6 = data.pct_change(periods=6)
    m12 = data.pct_change(periods=12)
    score = (12 * m1 + 4 * m3 + 2 * m6 + 1 * m12).dropna(axis=0)
    return score


def score_SMA12(data: pd.DataFrame) -> pd.DataFrame:
    score = (data / data.rolling(window=13).mean() - 1).dropna(axis=0)
    return score