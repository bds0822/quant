from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Ticker:
    symbol: str
    name: str = None
    desc: str = None
    currency: str = "USD"
    data_source: str = "yahoo"

    def __str__(self):
        return self.name if self.name is not None and self.name != "" else self.symbol

    def __lt__(self, other):
        return str(self) < str(other)


def get_symbols(tickers: list[Ticker]):
    return [t.symbol for t in tickers]


def get_display_name(tickers: list[Ticker]):
    return [str(t) for t in tickers]


PRICE_ATTRIBUTES = ["Close", "High", "Low", "Open"]

# US ETFs
SCHD = Ticker("SCHD", desc="Schwab US Dividend Equity ETF")
SPY = Ticker("SPY", desc="SPDR S&P 500 Trust ETF")
QQQ = Ticker("QQQ", desc="Invesco QQQ Trust Series 1")
IWM = Ticker("IWM", desc="iShares Russell 2000 ETF")
EFA = Ticker("EFA", desc="iShares MSCI EAFE ETF")
EEM = Ticker("EEM", desc="iShares MSCI Emerging Markets ETF")
VGK = Ticker("VGK", desc="Vanguard European Stock Index Fund ETF")
EWJ = Ticker("EWJ", desc="iShares MSCI Japan ETF")
VNQ = Ticker("VNQ", desc="Vanguard Real Estate Index Fund ETF")
TLT = Ticker("TLT", desc="iShares 20 Plus Year Treasury Bond ETF")
IEF = Ticker("IEF", desc="iShares 7-10 Year Treasury Bond ETF")
AGG = Ticker("AGG", desc="iShares Core US Aggregate Bond ETF")
TIP = Ticker("TIP", desc="iShares TIPS Bond ETF")
HYG = Ticker("HYG", desc="iShares iBoxx $ High Yield Corporate Bond ETF")
LQD = Ticker("LQD", desc="iShares iBoxx $ Inv Grade Corporate Bond ETF")
BIL = Ticker("BIL", desc="SPDR Bloomberg 1-3 Month T-Bill ETF")
GLD = Ticker("GLD", desc="SPDR Gold Shares")
DBC = Ticker("DBC", desc="Invesco DB Commodity Index Tracking Fund")
EWY = Ticker("EWY", desc="iShares MSCI South Korea ETF")
KRW = Ticker("KRW=X", name="KRW", desc="USD/KRW", currency="KRW")

# Hedged ETFs
EFA_H = Ticker("EFA", name="EFA_H", desc="iShares MSCI EAFE ETF(H)", currency="KRW")
EEM_H = Ticker("EEM", name="EEM_H", desc="iShares MSCI Emerging Markets ETF(H)", currency="KRW")
TLT_H = Ticker("TLT", name="TLT_H", desc="iShares 20 Plus Year Treasury Bond ETF(H)", currency="KRW")
IEF_H = Ticker("IEF", name="IEF_H", desc="iShares 7-10 Year Treasury Bond ETF(H)", currency="KRW")
AGG_H = Ticker("EEM", name="AGG_H", desc="iShares Core US Aggregate Bond ETF(H)", currency="KRW")
TIP_H = Ticker("TIP", name="TIP_H", desc="iShares TIPS Bond ETF(H)", currency="KRW")
LQD_H = Ticker("LQD", name="LQD_H", desc="iShares iBoxx $ Inv Grade Corporate Bond ETF(H)", currency="KRW")
BIL_H = Ticker("BIL", name="BIL_H", desc="SPDR Bloomberg 1-3 Month T-Bill ETF(H)", currency="KRW")
DBC_H = Ticker("DBC", name="DBC_H", desc="Invesco DB Commodity Index Tracking Fund(H)", currency="KRW")

# K-ETFs
TIGER_SNP_500 = Ticker("360750", name="TIGER S&P 500", currency="KRW", data_source="naver")
TIGER_NASDAQ_100 = Ticker("133690", name="TIGER NASDAQ 100", currency="KRW", data_source="naver")
TIGER_200 = Ticker("102110", name="TIGER 200", currency="KRW", data_source="naver")
KODEX_200 = Ticker("069500", name="KODEX 200", currency="KRW", data_source="naver")
KODEX_200_US_NOTE = Ticker("284430", name="KODEX 200 US Note", desc="KODEX 200 US Treasury Notes Balanced", currency="KRW", data_source="naver")
ARIRANG_EFA_H = Ticker("195970", name="ARIRANG EFA(H)", desc="ARIRANG MSCI EAFE(H)", currency="KRW", data_source="naver")
ARIRANG_EEM_H = Ticker("195980", name="ARIRANG EEM(H)", desc="ARIRANG MSCI Emerging Markets(H)", currency="KRW", data_source="naver")
ARIRANG_LQD = Ticker("332620", name="ARIRANG LQD", desc="ARIRANG 15+ Year AAA A US Corporate Bond", currency="KRW", data_source="naver")
KODEX_AGG_H = Ticker("437080", name="KODEX AGG(H)", desc="KODEX AGG SRI Active(H)", currency="KRW", data_source="naver")
KBSTAR_US_BOND_F_H = Ticker("267440", name="KBSTAR US Bonds(20+y)(H)", desc="KBSTAR US 20+ Year Treasury Bonds Future(H)", currency="KRW", data_source="naver")
ACE_US_BOND_H = Ticker("453850", name="ACE US Bonds(20+y)(H)", desc="ACE US 20+ Year Treasury Bonds Active(H)", currency="KRW", data_source="naver")
TIGER_US_NOTE_F = Ticker("305080", name="TIGER US Bonds(10y)", desc="TIGER US 10 Year Treasury Bonds Future", currency="KRW", data_source="naver")
TIGER_US_BIL = Ticker("329750", name="TIGER US Bills", desc="TIGER US Treasury Bills Active", currency="KRW", data_source="naver")
TIGER_KR_MSB = Ticker("157450", name="TIGER KR MSB", desc="TIGER Monetary Stabilization Bonds", currency="KRW", data_source="naver")
TIGER_KR_BIL = Ticker("272580", name="TIGER KR Bills", desc="TIGER Treasury Bills Active", currency="KRW", data_source="naver")
KOSEF_KR_NOTE = Ticker("148070", name="KOSEF KR Bonds(10y)", desc="KOSEF 10 Year Treasury Bonds", currency="KRW", data_source="naver")
ACE_GLD = Ticker("411060", name="ACE KRX Gold", currency="KRW", data_source="naver")
KODEX_OIL_F_H = Ticker("261220", name="KODEX WTI(H)", desc="KODEX WTI Future(H)", currency="KRW", data_source="naver")
TIGER_OIL_F_H = Ticker("130680", name="TIGER CRUDE OIL(H)", desc="TIGER Crude Oil Future Enhanced(H)", currency="KRW", data_source="naver")
