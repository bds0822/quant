from datetime import datetime

import pandas as pd
import quantstats as qs

from core.datareader import YahooFinance
from core.strategy import BAA
from core.ticker import *


if __name__ == "__main__":

    tickers_canary = [SPY, EFA, EEM, AGG]
    tickers_risk_g4 = [QQQ, EFA, EEM, AGG]
    tickers_risk_g12 = [SPY, QQQ, IWM, VGK, EWJ, EEM, VNQ, DBC, GLD, TLT, HYG, LQD]
    tickers_safe = [TIP, DBC, BIL, IEF, TLT, LQD, AGG]
    n_risk_g4 = 1
    n_risk_g12 = 6
    n_safe = 3

    trading_day = "end"
    # start = "2011-05-31"
    start = None
    # end = "2022-06-30"
    end = None

    datareader = YahooFinance()
    baa_g4 = BAA(tickers_canary, tickers_risk_g4, tickers_safe, n_risk=n_risk_g4, n_safe=n_safe)
    baa_g4_result = baa_g4.analyze(datareader, trading_day=trading_day, start=start, end=end)
    baa_g12 = BAA(tickers_canary, tickers_risk_g12, tickers_safe, n_risk=n_risk_g12, n_safe=n_safe)
    baa_g12_result = baa_g12.analyze(datareader, trading_day=trading_day, start=start, end=end)

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 1000)

    print("******** BAA G4 Result ********")
    # print(baa_g4_result[baa_g4_result > 0].iloc[-1][baa_g4.tickers_trading].dropna())
    # print(baa_g4_result[baa_g4_result["is_trading_day"]])
    print(baa_g4_result.loc[datetime(2020, 9, 1):datetime(2021, 4, 30)])
    print()

    print("******** BAA G12 Result ********")
    # print(baa_g12_result[baa_g12_result > 0].iloc[-1][baa_g12.tickers_trading].dropna())
    # print(baa_g12_result[baa_g12_result["is_trading_day"]])
    print(baa_g12_result.loc[datetime(2020, 9, 1):datetime(2021, 4, 30)])
    print()

    result = pd.DataFrame()
    result["baa_g4"] = baa_g4_result["total_return"]
    result["baa_g12"] = baa_g12_result["total_return"]
    strategy = "baa_g4"
    benchmark = "baa_g12"
    download_filename = f"C:/workspace/quant/{strategy}.html"
    qs.reports.html(result[strategy], result[benchmark],
                    title=strategy,
                    output="",
                    download_filename=download_filename)
    print()
