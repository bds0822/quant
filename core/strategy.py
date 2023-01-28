import abc
from datetime import datetime

import numpy as np
import pandas as pd

from core.datareader import DataReader
from core.ticker import Ticker, get_symbols


class Strategy(abc.ABC):

    @abc.abstractmethod
    def analyze(self, dr: DataReader,
                trading_day=1, trading_price="Close", start=None, end=None,
                **kwargs) -> pd.DataFrame:
        ...


class BAA(Strategy):

    def __init__(self,
                 tickers_canary: list[Ticker],
                 tickers_risk: list[Ticker],
                 tickers_safe: list[Ticker],
                 n_risk=1,
                 n_safe=3):

        self.tickers_all = list(set(tickers_canary + tickers_risk + tickers_safe))
        self.tickers_canary = get_symbols(tickers_canary)
        self.tickers_risk = get_symbols(tickers_risk)
        self.tickers_safe = get_symbols(tickers_safe)
        self.tickers_trading = list(set(self.tickers_risk + self.tickers_safe))
        self.n_risk = n_risk
        self.n_safe = n_safe

    def analyze(self, dr: DataReader,
                trading_day=1, trading_price="Close", start=None, end=None,
                **kwargs) -> pd.DataFrame:
        # load data
        data = dr.get_data(self.tickers_all, start=start, end=end, **kwargs)
        data = data[trading_price]

        trading_days = self.__get_trading_days(data, trading_day)

        # data for scoring - data of the day before trading days
        data_scoring = data.shift(periods=1).loc[trading_days]
        # data_scoring = data.loc[trading_days]
        # data for scoring canary assets
        data_scoring_canary = data_scoring[self.tickers_canary]
        # data for scoring risk and safe assets
        data_scoring_trading = data_scoring[self.tickers_trading]

        # 13612W score for canary assets
        score_13612W = self.__get_score_13612W(data_scoring_canary)
        score_SMA12 = self.__get_score_SMA12(data_scoring_trading)
        score_SMA12["buy_safe"] = (score_13612W < 0).any(axis=1)

        # buy assets and caluclate profit
        buy = score_SMA12.apply(self.__buy_assets, axis=1, result_type='expand')
        profit = self.__get_profit(data, buy)
        profit["is_trading_day"] = profit.apply(lambda x: x.name in buy.index, axis=1)
        return profit

    def __get_trading_days(self, data: pd.DataFrame, trading_day) -> pd.DataFrame:
        is_trading_day = pd.DataFrame()
        is_trading_day["year"] = data.index.year
        is_trading_day["month"] = data.index.month
        is_trading_day["day"] = data.index.day

        if isinstance(trading_day, int):
            is_trading_day["day_err"] = is_trading_day["day"] - trading_day + 31 * (is_trading_day["day"] < trading_day)

            group = []
            g = 0
            for i, row in enumerate(is_trading_day.itertuples()):
                if i == 0:
                    group.append(g)
                elif is_trading_day.iloc[i-1]["day_err"] > is_trading_day.iloc[i]["day_err"]:
                    g += 1
                    group.append(g)
                else:
                    group.append(g)

            is_trading_day["group"] = group
            is_trading_day = is_trading_day.groupby(["group"]).apply(lambda x: x.iloc[x["day_err"].argmin()])
        elif isinstance(trading_day, str):
            if trading_day.lower() in ["end", "ending"]:
                is_trading_day = is_trading_day.groupby(["year", "month"]).apply(lambda x: x.iloc[x["day"].argmax()])
            elif trading_day.lower() in ["begin", "beginning"]:
                is_trading_day = is_trading_day.groupby(["year", "month"]).apply(lambda x: x.iloc[x["day"].argmin()])
        else:
            raise NotImplementedError(f"trading_day[{trading_day}] is not implemented")

        trading_days = is_trading_day.apply(lambda x: datetime(x["year"], x["month"], x["day"]), axis=1)
        return trading_days

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

    def __buy_assets(self, score: pd.Series) -> dict[str, int]:
        buy = dict.fromkeys(self.tickers_trading, 0)
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

    def __get_profit(self, data: pd.DataFrame, buy: pd.DataFrame) -> pd.DataFrame:

        def __fill(r: pd.Series, buy: pd.DataFrame, prev) -> pd.Series:
            index = r.name
            changed = prev[0][buy.columns] * r
            total_return = prev[0]["total_return"] + changed.sum()

            if index in buy.index:
                result = buy.loc[index] * total_return
            else:
                result = prev[0][buy.columns] + changed

            result["total_return"] = total_return
            prev[0] = result
            return result

        start = buy.index[0]
        initial = pd.Series(np.zeros(len(buy.columns)), index=buy.columns)
        initial["total_return"] = 100
        prev = [initial]
        data_trading = data.loc[start:][self.tickers_trading]

        profit = data_trading.pct_change().apply(lambda r: __fill(r, buy, prev), axis=1)
        return profit
