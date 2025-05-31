import abc
from datetime import datetime

import numpy as np
import pandas as pd

from core.datareader import ReadData
from core.score import *
from core.ticker import Ticker, KRW, BIL


class Strategy(abc.ABC):
    """
    Abstract Strategy.
    """

    def __init__(self, name, tickers):
        self.name = name
        self.tickers = sorted(tickers)

    def __str__(self):
        return self.name

    def analyze(self, trading_day="end", trading_price="Close", start=None, end=None, in_krw=True, slippage=0.003,
                **kwargs) -> pd.DataFrame:
        """
        Get daily profit of the strategy.
        :param trading_day: Rebalancing day. Possible values are: 1 ~ 31 or 'end', 'ending', 'begin', 'beginning'.
        :param trading_price: Price used when rebalancing assets.
        :param start: Start date of analyzing period.
        :param end: End date of analyzing period.
        :param in_krw: If true, convert the currency of USD asset in South Korean Won.
        :param kwargs:
        :return: Daily profit of the strategy.
        """
        data, asset_weights = self.asset_weights_from_tickers(self.tickers,
                                                              trading_day, trading_price, start, end, in_krw,
                                                              **kwargs)
        profit = self.calculate_profit(data, asset_weights, in_krw, **kwargs)
        return profit

    def asset_weights_from_tickers(self, tickers: list[Ticker],
                                   trading_day="end", trading_price="Close", start=None, end=None, in_krw=True,
                                   **kwargs):
        data = self.read_data(tickers, trading_price, start, end, in_krw, **kwargs)
        trading_days = self.get_trading_days(data, trading_day, **kwargs)
        asset_weights = self.calculate_asset_weights(data, trading_days, **kwargs)
        return data, asset_weights

    @staticmethod
    def read_data(tickers: list[Ticker], trading_price="Close", start=None, end=None, in_krw=True,
                  **kwargs) -> pd.DataFrame:
        # read data
        tickers = tickers.copy()
        if in_krw:
            tickers.append(KRW)
        data = ReadData(tickers, start=start, end=end, **kwargs)
        data = data[trading_price]
        return data

    @staticmethod
    def get_trading_days(data: pd.DataFrame, trading_day, **kwargs) -> pd.Series:
        """
        Get trading days.
        :param data: Daily assets data.
        :param trading_day: Rebalancing day. Possible values are: 1 ~ 31 or 'end', 'ending', 'begin', 'beginning'.
        :param kwargs:
        :return: Trading days.
        """
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

    @abc.abstractmethod
    def calculate_asset_weights(self, data: pd.DataFrame, trading_days: pd.Series, **kwargs) -> pd.DataFrame:
        """
        Calculate asset weights under the strategy.
        :param data: Daily assets data.
        :param trading_days: Trading days.
        :param kwargs:
        :return: Asset weights.
        """
        ...

    @staticmethod
    def calculate_profit(data: pd.DataFrame, asset_weights: pd.DataFrame, in_krw=True,
                         **kwargs) -> pd.DataFrame:
        """
        Get daily profit.
        :param data: Daily assets data.
        :param asset_weights: Weights of assets trying to buy at each trading day.
        :param in_krw: If true, convert the currency of USD asset in South Korean Won.
        :param kwargs:
        :return: Daily profit.
        """
        tickers_trading = asset_weights.columns
        trading_day = asset_weights.index
        start = trading_day[0]
        data_trading = data.loc[start:, tickers_trading]
        if in_krw:
            data_trading = data_trading.apply(lambda x: x * data[KRW] if x.name.currency == "USD" else x).dropna()
        is_trading_day = data_trading.apply(lambda x: x.name in trading_day, axis=1)
        full_day = data_trading.index
        asset_weights_at_trading_day = pd.DataFrame(data=asset_weights, index=full_day).fillna(method='ffill')

        change = data_trading.pct_change().fillna(0)
        change_cum = (1 + change).cumprod()
        change_cum_at_trading_day = pd.DataFrame(data=change_cum.loc[trading_day], index=full_day)\
            .fillna(method='ffill').fillna(1)
        change_cum_from_trading_day = change_cum / change_cum_at_trading_day

        asset_weights_daily = (asset_weights_at_trading_day * change_cum_from_trading_day)\
            .apply(lambda x: x/x.sum(), axis=1)     # normalize
        asset_returned_daily = (asset_weights_daily.shift(1) * (1 + change)) \
            .apply(lambda x: x/x.sum(), axis=1)     # normalize
        asset_changed_daily = (asset_weights_daily - asset_returned_daily)\
            .apply(lambda x: x * is_trading_day)\
            .apply(np.abs)

        slippage = 0.003
        slippage_daily = asset_changed_daily.sum(axis=1) * slippage
        total_return = (1 + (asset_weights_daily.shift(1) * change).sum(axis=1) - slippage_daily).cumprod()
        profit = asset_weights_daily.apply(lambda x: x * total_return)
        profit["total_return"] = total_return
        profit["is_trading_day"] = is_trading_day
        return profit


class SAA(Strategy):
    """
    Static Asset Allocation.
    """

    def __init__(self,
                 name: str,
                 tickers: list[Ticker],
                 weights: list[float]):

        assert len(tickers) == len(weights), "number of tickers and weights must be same"
        weights = np.array(weights, dtype=np.float32) / np.sum(weights)
        super().__init__(name, tickers)
        self.weights = {t: w for t, w in zip(tickers, weights)}

    def calculate_asset_weights(self, data: pd.DataFrame, trading_days: pd.Series, **kwargs) -> pd.DataFrame:
        asset_weights = pd.DataFrame(index=trading_days, columns=self.tickers, data=[self.weights] * len(trading_days))
        return asset_weights


class BAA(Strategy):
    """
    Bold Asset Allocation.
    """

    def __init__(self,
                 name: str,
                 tickers_canary: list[Ticker],
                 tickers_risk: list[Ticker],
                 tickers_safe: list[Ticker],
                 ticker_bill=BIL,
                 n_risk=1,
                 n_safe=3):

        tickers = list(set(tickers_canary + tickers_risk + tickers_safe))
        super().__init__(name, tickers)
        self.tickers_canary = sorted(tickers_canary)
        self.tickers_risk = sorted(tickers_risk)
        self.tickers_safe = sorted(tickers_safe)
        self.tickers_trading = sorted(list(set(self.tickers_risk + self.tickers_safe)))
        self.ticker_bil = ticker_bill
        self.n_risk = n_risk
        self.n_safe = n_safe

    def calculate_asset_weights(self, data: pd.DataFrame, trading_days: pd.Series, **kwargs) -> pd.DataFrame:
        # data for scoring - data of the day before trading days
        data_scoring = data.apply(floor, decimal=4).shift(periods=1).loc[trading_days]
        # data for scoring canary assets
        data_scoring_canary = data_scoring[self.tickers_canary]
        # data for scoring risk and safe assets
        data_scoring_trading = data_scoring[self.tickers_trading]

        # 13612W score for canary assets
        canary_score = score_13612W(data_scoring_canary)
        momentum_score = score_SMA12(data_scoring_trading)

        # buy assets and calculate profit
        asset_weights = self._get_asset_weights(momentum_score, canary_score)
        return asset_weights

    def _get_asset_weights(self, momentum_score: pd.DataFrame, canary_score: pd.DataFrame) -> pd.DataFrame:
        run_to_safety = (canary_score < 0).any(axis=1)

        asset_risk_score_threshold = momentum_score[self.tickers_risk] \
            .apply(lambda x: x.sort_values(ascending=False)[self.n_risk - 1], axis=1)
        asset_safe_score_threshold = momentum_score[self.tickers_safe] \
            .apply(lambda x: x.sort_values(ascending=False)[self.n_safe - 1], axis=1)

        asset_risk_top_n = momentum_score[self.tickers_risk] \
            .apply(lambda x: x >= asset_risk_score_threshold).applymap(int)
        asset_safe_top_n = momentum_score[self.tickers_safe] \
            .apply(lambda x: x >= asset_safe_score_threshold).applymap(int)

        # calculate weights
        asset_risk_weight = asset_risk_top_n.apply(lambda x: x * (1 - run_to_safety) / self.n_risk)
        asset_safe_weight = asset_safe_top_n.apply(lambda x: x * run_to_safety / self.n_safe)

        # if a safe asset was worse than BIL, allocate that portion of the asset to BIL.
        asset_safe_worse_than_bil = momentum_score[self.tickers_safe].apply(lambda x: x < x[self.ticker_bil], axis=1).applymap(int)
        asset_safe_weight_worse_than_bil = asset_safe_weight * asset_safe_worse_than_bil
        asset_safe_weight -= asset_safe_weight_worse_than_bil
        asset_safe_weight[self.ticker_bil] += asset_safe_weight_worse_than_bil.sum(axis=1)

        asset_weights = pd.DataFrame(data=0, index=momentum_score.index, columns=self.tickers_trading)
        asset_weights[self.tickers_risk] += asset_risk_weight
        asset_weights[self.tickers_safe] += asset_safe_weight
        return asset_weights


class HAA(BAA):
    """
    Hybrid Asset Allocation.
    """

    def __init__(self,
                 name: str,
                 tickers_canary: list[Ticker],
                 tickers_risk: list[Ticker],
                 tickers_safe: list[Ticker],
                 ticker_bil=BIL,
                 n_risk=4,
                 n_safe=1):

        super().__init__(name,
                         tickers_canary,
                         tickers_risk,
                         tickers_safe,
                         ticker_bil,
                         n_risk,
                         n_safe)

    def calculate_asset_weights(self, data: pd.DataFrame, trading_days: pd.Series, **kwargs) -> pd.DataFrame:
        # data for scoring - data of the day before trading days
        data_scoring = data.apply(floor, decimal=4).shift(periods=1).loc[trading_days]
        # data for scoring canary assets
        data_scoring_canary = data_scoring[self.tickers_canary]
        # data for scoring risk and safe assets
        data_scoring_trading = data_scoring[self.tickers_trading]

        # 13612W score for canary assets
        canary_score = score_13612U(data_scoring_canary)
        momentum_score = score_13612U(data_scoring_trading)

        # buy assets and calculate profit
        asset_weights = self._get_asset_weights(momentum_score, canary_score)
        return asset_weights

    def _get_asset_weights(self, momentum_score: pd.DataFrame, canary_score: pd.DataFrame) -> pd.DataFrame:
        run_to_safety = (canary_score < 0).any(axis=1)

        asset_risk_score_threshold = momentum_score[self.tickers_risk] \
            .apply(lambda x: x.sort_values(ascending=False)[self.n_risk - 1], axis=1)
        asset_safe_score_threshold = momentum_score[self.tickers_safe] \
            .apply(lambda x: x.sort_values(ascending=False)[self.n_safe - 1], axis=1)

        asset_risk_top_n = momentum_score[self.tickers_risk] \
            .apply(lambda x: x >= asset_risk_score_threshold).applymap(int)
        asset_safe_top_n = momentum_score[self.tickers_safe] \
            .apply(lambda x: x >= asset_safe_score_threshold).applymap(int)

        # calculate weights
        asset_risk_weight = asset_risk_top_n.apply(lambda x: x * (1 - run_to_safety) / self.n_risk)
        asset_safe_weight = asset_safe_top_n.apply(lambda x: x * run_to_safety / self.n_safe)

        # if a risk asset has a negative momentum, allocate that portion of the asset to safe assets.
        asset_risk_neg_mtm = momentum_score[self.tickers_risk].apply(lambda x: x < 0, axis=1).applymap(int)
        asset_risk_weight_neg_mtm = asset_risk_weight * asset_risk_neg_mtm
        asset_risk_weight -= asset_risk_weight_neg_mtm

        asset_risk_weight_neg_mtm_reallocated = asset_safe_top_n \
            .apply(lambda x: x * np.asarray(asset_risk_weight_neg_mtm.sum(axis=1))) / self.n_safe
        asset_safe_weight += asset_risk_weight_neg_mtm_reallocated

        # if a safe asset was worse than BIL, allocate that portion of the asset to BIL.
        asset_safe_worse_than_bil = momentum_score[self.tickers_safe].apply(lambda x: x < x[self.ticker_bil], axis=1).applymap(int)
        asset_safe_weight_worse_than_bil = asset_safe_weight * asset_safe_worse_than_bil
        asset_safe_weight -= asset_safe_weight_worse_than_bil
        asset_safe_weight[self.ticker_bil] += asset_safe_weight_worse_than_bil.sum(axis=1)

        asset_weights = pd.DataFrame(data=0, index=momentum_score.index, columns=self.tickers_trading)
        asset_weights[self.tickers_risk] += asset_risk_weight
        asset_weights[self.tickers_safe] += asset_safe_weight
        return asset_weights


class Alternatives(Strategy):
    """
    Asset Allocation with alternatives trading assets.
    """

    def __init__(self,
                 name: str,
                 strategy: Strategy,
                 alternatives: dict[Ticker, Ticker] = {}):
        super().__init__(name, strategy.tickers)
        self.strategy = strategy
        self.alternatives = alternatives

    def analyze(self, trading_day="end", trading_price="Close", start=None, end=None, in_krw=True,
                **kwargs) -> pd.DataFrame:
        profit = self.strategy.analyze(trading_day, trading_price, start, end, in_krw, **kwargs)
        # switch trading assets to alternatives
        profit.rename(columns=self.alternatives, inplace=True)
        return profit

    def calculate_asset_weights(self, data: pd.DataFrame, trading_days: pd.Series, **kwargs) -> pd.DataFrame:
        # calculate asset weights by base strategy
        return self.strategy.calculate_asset_weights(data, trading_days, **kwargs)


def floor(x, decimal=4):
    pos = 10**decimal
    return np.floor(x * pos) / pos


if __name__ == '__main__':
    from core.ticker import *

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 1000)

    tickers_canary = [SPY, EFA, EEM, AGG]
    tickers_risk_g4 = [QQQ, EFA, EEM, AGG]
    tickers_risk_g12 = [SPY, QQQ, IWM, VGK, EWJ, EEM, VNQ, DBC, GLD, TLT, HYG, LQD]
    tickers_safe = [TLT, IEF, AGG, TIP, LQD, BIL, DBC]
    n_risk_g4 = 1
    n_risk_g12 = 6
    n_safe = 3

    baa_g4 = BAA("BAA_G4",
                 tickers_canary, tickers_risk_g4, tickers_safe,
                 n_risk=n_risk_g4, n_safe=n_safe)
    baa_g4.analyze(in_krw=True)
