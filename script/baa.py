import pandas as pd
import quantstats as qs

from core.data_loader import YahooFinanceDataLoader
from core.strategy import BAA


if __name__ == "__main__":

    tickers_canary = ["SPY", "EFA", "EEM", "AGG"]
    tickers_risk_g4 = ["QQQ", "EFA", "EEM", "AGG"]
    tickers_risk_g12 = ["SPY", "QQQ", "IWM", "VGK", "EWJ", "EEM", "VNQ", "DBC", "GLD", "TLT", "HYG", "LQD"]
    tickers_safe = ["TIP", "DBC", "BIL", "IEF", "TLT", "LQD", "AGG"]
    n_risk_g4 = 1
    n_risk_g12 = 6
    n_safe = 3

    day = 1
    start = None
    end = None

    data_loader = YahooFinanceDataLoader()
    baa_g4 = BAA(tickers_canary, tickers_risk_g4, tickers_safe, n_risk=n_risk_g4, n_safe=n_safe)
    baa_g4_result = baa_g4.run(data_loader, day=day, start=start, end=end)
    baa_g12 = BAA(tickers_canary, tickers_risk_g12, tickers_safe, n_risk=n_risk_g12, n_safe=n_safe)
    baa_g12_result = baa_g12.run(data_loader, day=day, start=start, end=end)

    print("******** BAA G4 Result ********")
    print(baa_g4_result[baa_g4_result > 0].iloc[-1][baa_g4.tickers_buy].dropna())
    print()

    print("******** BAA G12 Result ********")
    print(baa_g12_result[baa_g12_result > 0].iloc[-1][baa_g12.tickers_buy].dropna())
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
