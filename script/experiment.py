import os
from typing import List, Tuple

import pandas as pd
import quantstats as qs

from core.strategy import Strategy, SAA, BAA, Alternatives
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
                tickers_canary, [QQQ], [TLT_H, IEF, LQD, BIL, DBC_H],  # need K-TIP and K-IEF_H for safe assets
                n_risk=n_risk_g4, n_safe=n_safe)
    k_baa_psa = Alternatives("K_BAA_PSA",
                             k_baa,
                             alternatives={
                                 QQQ: TIGER_NASDAQ_100,
                                 TLT_H: KBSTAR_US_BOND_F_H,
                                 IEF: TIGER_US_NOTE_F,
                                 LQD: ARIRANG_LQD,
                                 BIL: TIGER_US_BIL,
                                 DBC_H: TIGER_OIL_F_H,
                             })

    all_weather = SAA("ALL_WEATHER",
                      [SPY, TLT, IEF, GLD, DBC],
                      [30, 40, 15, 7.5, 7.5])
    k_all_weather = SAA("K_ALL_WEATHER",
                        [SPY, TLT_H, IEF, GLD, DBC_H],    # need K-TLT and K-DBC
                        [30, 40, 15, 7.5, 7.5])
    k_all_weather_psa = SAA("K_ALL_WEATHER_PSA",
                            [TIGER_SNP_500, KBSTAR_US_BOND_F_H, TIGER_US_NOTE_F, ACE_GLD, TIGER_OIL_F_H],
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
                     [TIGER_SNP_500, KODEX_200, KODEX_200_US_NOTE, KBSTAR_US_BOND_F_H, KOSEF_KR_NOTE, ACE_GLD],
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
        (baa_g12, baa_g4),
        (k_baa_g4, spy),
        (k_baa_g4, baa_g4),
        (k_baa, spy),
        (k_baa, baa_g4),
        (k_baa, k_baa_g4),
        (all_weather, spy),
        (k_all_weather, all_weather),
        (k_all_weather, spy),
        (k_all_weather, k_baa),
        (k_all_weather_psa, k_all_weather),
        (richgo, spy),
        (richgo, k_baa),
        (richgo, k_all_weather),
        (richgo_irp, richgo),
        (k_baa_psa, spy),
        (k_baa_psa, k_baa),
    ]
    file_tag = "KRW" if in_krw else "USD"
    quantstats_reports(result, targets, file_tag=file_tag)
