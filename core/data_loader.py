import abc

import numpy as np
import pandas as pd
import yfinance as yf

from datetime import datetime


class DataLoader(abc.ABC):

    @staticmethod
    def get_data(tickers: list[str], **kwargs) -> pd.DataFrame:
        ...


class YahooFinanceDataLoader(DataLoader):

    @staticmethod
    def get_data(tickers: list[str], price_type="Adj Close", day=31,
                 start=None, end=None, actions=False, threads=True, ignore_tz=True,
                 group_by='column', auto_adjust=False, back_adjust=False, keepna=False,
                 progress=True, period="max", show_errors=True, interval="1d", prepost=False,
                 proxy=None, rounding=False, timeout=None,
                 **kwargs) -> pd.DataFrame:
        df = yf.download(tickers,
                         start=start, end=end, actions=actions, threads=threads, ignore_tz=ignore_tz,
                         group_by=group_by, auto_adjust=auto_adjust, back_adjust=back_adjust, keepna=keepna,
                         progress=progress, period=period, show_errors=show_errors, interval=interval, prepost=prepost,
                         proxy=proxy, rounding=rounding, timeout=timeout)
        df = df[price_type]
        df.dropna(inplace=True)

        df["year"] = df.index.year
        df["month"] = df.index.month
        df["day"] = df.index.day

        df["day_err"] = np.abs(df["day"] - day)
        df = df.groupby(["year", "month"]).apply(lambda x: x.iloc[x["day_err"].argmin()])

        datetime_index = df.apply(lambda x: datetime(int(x["year"]), int(x["month"]), int(x["day"])), axis=1)
        df.index = datetime_index
        df = df[tickers]
        return df


if __name__ == "__main__":

    tickers = ["QQQ", "SPY", "EEM", "EFA", "AGG", "IWM", "VGK", "EWJ", "VNQ",
               "DBC", "GLD", "TLT", "IEF", "HYG", "LQD", "TIP", "BIL"]
    df = YahooFinanceDataLoader.get_data(tickers, keepna=True)
    print(df)
