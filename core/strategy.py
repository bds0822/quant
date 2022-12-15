import abc

import pandas as pd

from core.data_loader import DataLoader


class Strategy(abc.ABC):

    @abc.abstractmethod
    def run(self, data_loader: DataLoader) -> pd.DataFrame:
        ...


class BAA(Strategy):

    def __init__(self, tickers_canary, tickers_risk, tickers_safe, n_risk=1, n_safe=3):
        self.tickers_canary = tickers_canary
        self.tickers_risk = tickers_risk
        self.tickers_safe = tickers_safe
        self.tickers_buy = list(set(tickers_risk + tickers_safe))
        self.tickers_all = list(set(self.tickers_canary + self.tickers_buy))
        self.n_risk = n_risk
        self.n_safe = n_safe

    def run(self, data_loader: DataLoader, **kwargs) -> pd.DataFrame:
        # load data
        data = data_loader.get_data(self.tickers_all, **kwargs)
        # data for canary assets
        data_canary = data[self.tickers_canary]
        # data for risk and safe assets
        data_buy = data[self.tickers_buy]

        # 13612W score for canary assets
        score_13612W = self.__get_score_13612W(data_canary)
        score_SMA12 = self.__get_score_SMA12(data_buy)
        score_SMA12["buy_safe"] = (score_13612W < 0).any(axis=1)

        # buy assets and caluclate profit
        buy = score_SMA12.apply(self.__buy_assets, axis=1, result_type='expand')
        profit = (data_buy.pct_change() * buy.shift(periods=1)).sum(axis=1)
        total_return = (1 + profit).cumprod() * 100
        buy["total_return"] = total_return
        return buy

    def __get_score_13612W(self, data: pd.DataFrame) -> pd.DataFrame:
        m1 = data.pct_change(periods=1)
        m3 = data.pct_change(periods=3)
        m6 = data.pct_change(periods=6)
        m12 = data.pct_change(periods=12)
        score = (12 * m1 + 4 * m3 + 2 * m6 + 1 * m12).dropna(axis=0)
        return score

    def __get_score_SMA12(self, data: pd.DataFrame) -> pd.DataFrame:
        score = (data / data.rolling(window=13).mean() - 1).dropna(axis=0)
        return score

    def __buy_assets(self, score):
        buy = dict.fromkeys(self.tickers_buy, 0)
        if score["buy_safe"]:
            n = self.n_safe
            tickers = self.tickers_safe
        else:
            n = self.n_risk
            tickers = self.tickers_risk

        top_assets = score[tickers].sort_values(ascending=False).head(n)
        top_assets = list(top_assets.index)
        if "BIL" in top_assets:
            index = top_assets.index("BIL")
            top_assets[index:] = ["BIL"] * (len(top_assets) - index)

        for ticker in top_assets:
            buy[ticker] += 1/n
        return buy
