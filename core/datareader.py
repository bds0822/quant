import abc

import pandas as pd
import pandas_datareader as pdr
import yfinance as yf
from tqdm import tqdm

from core.ticker import *


class DataReader(abc.ABC):

    @staticmethod
    def read(tickers: list[Ticker], **kwargs) -> pd.DataFrame:
        ...


class YahooDataReader(DataReader):

    @staticmethod
    def read(tickers: list[Ticker], start=None, end=None,
             actions=False, auto_adjust=True, keepna=False,
             **kwargs) -> pd.DataFrame:

        print(f"YahooDataReader: read {[str(t) for t in tickers]}")
        tickers_symbol = get_symbols(tickers)
        df = yf.download(tickers_symbol, start=start, end=end,
                         actions=actions, auto_adjust=auto_adjust, keepna=keepna, ignore_tz=True,
                         **kwargs)
        if len(tickers) == 1:
            df.columns = pd.MultiIndex.from_product([df.columns, tickers_symbol])

        # There are possibly redundant tickers
        columns = pd.MultiIndex.from_product([df.columns.levels[0], tickers])
        data = {col: df[(col[0], col[1].symbol)].copy() for col in columns}
        df = pd.DataFrame(data=data)
        if not keepna:
            df.dropna(inplace=True)

        return df


class NaverDataReader(DataReader):

    @staticmethod
    def read(tickers: list[Ticker], start=None, end=None,
             actions=False, auto_adjust=True, keepna=False,
             **kwargs) -> pd.DataFrame:

        print(f"NaverDataReader: read {[str(t) for t in tickers]}")
        tickers_symbol = get_symbols(tickers)
        df = pd.DataFrame()
        for symbol in tqdm(tickers_symbol):
            df_symb = pdr.data.DataReader(symbol, data_source="naver", start=start, end=end)
            df_symb.columns = pd.MultiIndex.from_product([df_symb.columns, [symbol]])
            df = pd.concat((df, df_symb), axis=1)

        # There are possibly redundant tickers
        columns = pd.MultiIndex.from_product([df.columns.levels[0], tickers])
        data = {col: df[(col[0], col[1].symbol)].copy() for col in columns}
        df = pd.DataFrame(data=data)
        if not keepna:
            df.dropna(inplace=True)

        return df


def _get_data_reader(data_source: str) -> DataReader:
    if data_source == "yahoo":
        return YahooDataReader()
    elif data_source == "naver":
        return NaverDataReader()
    else:
        raise NotImplementedError(f"DataReader for DataSource[{data_source}] is not implemented.")


DEFAULT_START = "1800-01-01"


def ReadData(tickers: list[Ticker], start=None, end=None,
             actions=False, auto_adjust=True, keepna=False,
             **kwargs) -> pd.DataFrame:

    # just for safety
    if start is None:
        start = DEFAULT_START

    # align tickers with their data sources
    data_sources = {}
    for t in tickers:
        data_sources.setdefault(t.data_source, []).append(t)

    # read data from each data source and combine
    df = pd.DataFrame()
    for ds, tcks in data_sources.items():
        df_ds = _get_data_reader(ds).read(tcks, start=start, end=end,
                                          actions=actions, auto_adjust=auto_adjust, keepna=True,
                                          **kwargs)
        df = pd.concat((df, df_ds), axis=1)

    if not keepna:
        df.dropna(inplace=True)

    return df.applymap(float)


if __name__ == "__main__":

    import matplotlib.pyplot as plt

    tickers = [
        SPY,
        QQQ,
        EWY,
        EFA,
        EFA_H,
        EEM,
        EEM_H,
        LQD,
        LQD_H,
        AGG,
        AGG_H,
        TLT,
        TLT_H,
        IEF,
        IEF_H,
        BIL,
        BIL_H,
        GLD,
        DBC,
        DBC_H,
        TIGER_SNP_500,
        TIGER_NASDAQ_100,
        TIGER_200,
        KODEX_200,
        ARIRANG_EFA_H,
        ARIRANG_EEM_H,
        ARIRANG_LQD,
        KODEX_AGG_H,
        KBSTAR_US_BOND_F_H,
        ACE_US_BOND_H,
        TIGER_US_NOTE_F,
        TIGER_US_BIL,
        TIGER_KR_MSB,
        TIGER_KR_BIL,
        KOSEF_KR_NOTE,
        KODEX_200_US_NOTE,
        ACE_GLD,
        KODEX_OIL_F_H,
        TIGER_OIL_F_H,
    ]
    df = ReadData(
        tickers + [KRW],
        keepna=True,
    )
    df = df.apply(lambda x: x * df[(x.name[0], KRW)] if x.name[1].currency == "USD" else x)
    df.drop(KRW, axis=1, level=1, inplace=True)

    idxmin = pd.isna(df).idxmin()
    idxmax = pd.isna(df).iloc[::-1].idxmin()
    first_price = df[PRICE_ATTRIBUTES].apply(lambda x: x.loc[idxmin[x.name]])
    last_price = df[PRICE_ATTRIBUTES].apply(lambda x: x.loc[idxmax[x.name]])
    tr = last_price / (first_price + 1e-9)
    print(">> Total Return")
    print(tr["Close"])
    print()

    print(df)
    df.dropna(inplace=True)
    (1 + df["Close"].pct_change()).cumprod().plot.line()
    plt.show()
