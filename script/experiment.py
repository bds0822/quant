import os
from typing import List, Tuple

import pandas as pd
import quantstats as qs

from core.strategy import *
from core.ticker import *


def analyze_strategies(strategies: List[Strategy],
                       trading_day="end", trading_price="Close", start=None, end=None, in_krw=True,
                       **kwargs):
    result = {}
    for st in strategies:
        rtn = st.analyze(trading_day=trading_day,
                         trading_price=trading_price,
                         start=start,
                         end=end,
                         in_krw=in_krw,
                         **kwargs)
        result[st] = rtn
    return result


def quantstats_reports(result, targets: List[Tuple[Strategy, Strategy]],
                       file_dir="D:/workspace/quant/results",
                       file_tag="KRW"):
    # validity check
    targets_valid = []
    for st, bm in targets:
        if st not in result:
            print(f"Could not found Strategy[{st}]. Skip ({st}, {bm})")
            continue
        if bm not in result:
            print(f"Could not found Strategy[{bm}]. Skip ({st}, {bm})")
            continue
        targets_valid.append((st, bm))

    all_strategies = set()
    for st, bm in targets_valid:
        all_strategies.add(st)
        all_strategies.add(bm)

    all_tr = pd.DataFrame()
    for st in all_strategies:
        st_tr = pd.DataFrame(result[st]["total_return"]).rename(columns={"total_return": st})
        all_tr = pd.concat((all_tr, st_tr), axis=1)

    for st, bm in targets_valid:
        tr = all_tr[[st, bm]].dropna()
        file_name = "__".join([f"{st}", f"{bm}", file_tag]) + ".html"
        file = os.path.join(file_dir, file_name)
        qs.reports.html(tr[st], tr[bm],
                        title=f"{st}",
                        benchmark_title=f"{bm}",
                        output="",
                        download_filename=file)
        print(f"Saved result of Strategy[{st}] with Benchmark[{bm}] at {file}")


def print_result(result, history=True):
    for k, v in result.items():
        print(f"******** {k} Result ********")
        if history:
            print(v[v["is_trading_day"]])
        else:
            print(v[v["is_trading_day"]].tail(5))
        print()


if __name__ == "__main__":
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

    trading_day = "end"
    # start = "2019-09-01"
    start = None
    # end = "2022-06-30"
    end = None
    in_krw = True

    qqq = SAA("QQQ", [QQQ], [100])
    spy = SAA("SPY", [SPY], [100])
    schd = SAA("SCHD", [SCHD], [100])
    baa_g4 = BAA("BAA_G4",
                 tickers_canary, tickers_risk_g4, tickers_safe,
                 n_risk=n_risk_g4, n_safe=n_safe)
    baa_g12 = BAA("BAA_G12",
                  tickers_canary, tickers_risk_g12, tickers_safe,
                  n_risk=n_risk_g12, n_safe=n_safe)

    k_baa_g4 = BAA("K_BAA_G4",
                   tickers_canary, tickers_risk_g4, [TLT_H, IEF_H, AGG, TIP, LQD, BIL, DBC],
                   n_risk=n_risk_g4, n_safe=n_safe)
    k_baa = BAA("K_BAA",
                tickers_canary, [QQQ], [TLT_H, IEF, TIP, LQD, BIL, DBC_H],  # need K-IEF_H and K-DBC
                n_risk=n_risk_g4, n_safe=n_safe)
    k_baa_psa = BAA("K_BAA_PSA",
                    tickers_canary,
                    [KODEX_NASDAQ_100],
                    [ACE_US_BOND_H, KODEX_US_NOTE_F, KODEX_TIP, KODEX_LQD, KODEX_US_SOFR_BIL, TIGER_OIL_F_H],
                    ticker_bill=KODEX_US_SOFR_BIL,
                    n_risk=n_risk_g4, n_safe=n_safe)

    # haa = HAA("HAA",
    #           [TIP], [SPY, IWM, EFA, EEM, VNQ, DBC, TLT, IEF], [IEF, BIL],
    #           n_risk=4, n_safe=1)
    haa = HAA("HAA",
              [TIP, SPY], [SPY, QQQ, IWM, EFA, EEM, IYR, DBC, TLT, IEF, GLD], [IEF, BIL, LQD],
              n_risk=4, n_safe=1)
    k_haa = HAA("K_HAA",
                [TIP, SPY], [SPY, QQQ, IYR_H, DBC_H, TLT_H, IEF, GLD], [IEF, BIL, LQD],
                n_risk=4, n_safe=1)
    k_haa_psa = HAA("K_HAA_PSA",
                    [TIP, SPY],
                    [KODEX_SNP_500, KODEX_NASDAQ_100, KODEX_IYR_H, TIGER_OIL_F_H, ACE_US_BOND_H, KODEX_US_NOTE_F, ACE_GLD],
                    [KODEX_US_NOTE_F, KODEX_US_SOFR_BIL, KODEX_LQD],
                    ticker_bil=KODEX_US_SOFR_BIL,
                    n_risk=4, n_safe=1)

    all_weather = SAA("ALL_WEATHER",
                      [SPY, TLT, IEF, GLD, DBC],
                      [30, 40, 15, 7.5, 7.5])
    k_all_weather = SAA("K_ALL_WEATHER",
                        [SPY, TLT_H, IEF, GLD, DBC_H],    # need K-TLT and K-DBC
                        [30, 40, 15, 7.5, 7.5])
    k_all_weather_psa = SAA("K_ALL_WEATHER_PSA",
                            [TIGER_SNP_500, RISE_US_BOND_F_H, TIGER_US_NOTE_F, ACE_GLD, TIGER_OIL_F_H],
                            [30, 40, 15, 7.5, 7.5])
    # richgo1 = SAA("RICHGO_1",
    #               [SPY, KODEX_200, IEF, TLT_H, LQD, KOSEF_KR_NOTE, GLD],
    #               [50, 8, 12, 10, 10, 0, 10])
    # richgo2 = SAA("RICHGO_2",
    #               [SPY, KODEX_200, IEF, TLT_H, LQD, KOSEF_KR_NOTE, GLD],
    #               [25, 25, 10, 20, 10, 0, 10])
    # richgo3 = SAA("RICHGO_3",
    #               [SPY, KODEX_200, IEF, TLT_H, LQD, KOSEF_KR_NOTE, GLD],
    #               [25, 25, 10, 10, 10, 0, 20])
    # richgo4 = SAA("RICHGO_4",
    #               [SPY, KODEX_200, IEF, TLT_H, LQD, KOSEF_KR_NOTE, GLD],
    #               [25, 25, 10, 10, 10, 10, 10])
    richgo = SAA("RICHGO",
                 [SPY, KODEX_200, IEF, TLT_H, KOSEF_KR_NOTE, GLD],
                 [25, 23, 12, 10, 10, 20])
    richgo_irp = SAA("RICHGO_IRP",
                     [TIGER_SNP_500, KODEX_200, KODEX_200_US_NOTE, RISE_US_BOND_F_H, KOSEF_KR_NOTE, ACE_GLD],
                     [25, 15, 20, 10, 10, 20])

    strategies = [
        qqq,
        spy,
        schd,
        baa_g4,
        baa_g12,
        k_baa_g4,
        k_baa,
        k_baa_psa,
        haa,
        k_haa,
        k_haa_psa,
        all_weather,
        k_all_weather,
        k_all_weather_psa,
        richgo,
        richgo_irp,
    ]
    result = analyze_strategies(strategies,
                                trading_day=trading_day,
                                start=start,
                                end=end,
                                in_krw=in_krw)
    print_result(result, history=True)

    targets = [
        (qqq, spy),
        (schd, spy),

        (baa_g4, spy),
        (baa_g12, spy),
        (baa_g4, baa_g12),
        (k_baa, baa_g4),
        (k_baa_psa, spy),
        (k_baa_psa, k_baa),

        (haa, baa_g4),
        (k_haa, haa),
        (k_haa, k_baa),
        (k_haa_psa, k_haa),
        (k_haa_psa, k_baa_psa),

        (all_weather, spy),
        (k_all_weather, all_weather),
        (k_all_weather, k_baa),
        (k_all_weather_psa, k_all_weather),

        (richgo, k_baa),
        (richgo, k_all_weather),
        (richgo_irp, richgo),
    ]
    file_tag = "KRW" if in_krw else "USD"
    quantstats_reports(result, targets, file_tag=file_tag)
