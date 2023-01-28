import abc
from datetime import datetime

import numpy as np
import pandas as pd
import pandas_datareader as pdr
import yfinance as yf

from core.ticker import *


class DataReader(abc.ABC):

    @staticmethod
    def get_data(tickers: list[Ticker], **kwargs) -> pd.DataFrame:
        ...


class YahooFinance(DataReader):

    @staticmethod
    def get_data(tickers: list[Ticker], start=None, end=None,
                 actions=False, auto_adjust=True, keepna=False,
                 **kwargs) -> pd.DataFrame:

        tickers_symbol = [t.symbol for t in tickers]
        # tickers_data = [t.data for t in tickers]
        # assert len(tickers) == len(set(tickers_data)), \
        #     f"All tickers must have different data: {tickers_data}"

        df = yf.download(tickers_symbol, start=start, end=end,
                         actions=actions, auto_adjust=auto_adjust, keepna=keepna,
                         **kwargs)
        if not keepna:
            df.dropna(inplace=True)

        if len(tickers) == 1:
            columns = pd.MultiIndex.from_product([df.columns, tickers_symbol])
            df.columns = columns

        return df


class PandasDataReader(DataReader):

    @staticmethod
    def get_data(tickers: list[Ticker], start=None, end=None,
                 actions=False, auto_adjust=True, keepna=False,
                 **kwargs) -> pd.DataFrame:

        tickers_symbol = [t.symbol for t in tickers]
        # tickers_data = [t.data for t in tickers]
        # assert len(tickers) == len(set(tickers_data)), \
        #     f"All tickers must have different data: {tickers_data}"

        yf.pdr_override()
        df = pdr.data.get_data_yahoo(tickers_symbol,
                                     start=start, end=end, get_actions=actions,
                                     adjust_price=auto_adjust, adjust_dividends=auto_adjust,
                                     **kwargs)
        if not keepna:
            df.dropna(inplace=True)

        if len(tickers) == 1:
            columns = pd.MultiIndex.from_product([df.columns, tickers_symbol])
            df.columns = columns

        return df


if __name__ == "__main__":

    import matplotlib.pyplot as plt

    tickers = [SPY, QQQ, IWM, VGK, EWJ, EEM, EFA, VNQ,
               DBC, GLD, TLT, IEF, AGG, HYG, LQD, TIP, BIL]
    df = YahooFinance.get_data(tickers, keepna=True)
    # df = YahooFinance.get_data([SPY])
    print(df)
