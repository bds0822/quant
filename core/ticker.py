from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Ticker:
    symbol: str
    index: str = None

    @property
    def data(self):
        return self.symbol if self.index is None else self.index


def get_symbols(tickers: list[Ticker]):
    return [t.symbol for t in tickers]


SPY = Ticker("SPY", "^GSPC")
QQQ = Ticker("QQQ", "^NDX")
IWM = Ticker("IWM")
EFA = Ticker("EFA")
EEM = Ticker("EEM")
VGK = Ticker("VGK")
EWJ = Ticker("EWJ")

VNQ = Ticker("VNQ")

DBC = Ticker("DBC")
GLD = Ticker("GLD")

TLT = Ticker("TLT")
IEF = Ticker("IEF")
AGG = Ticker("AGG")
TIP = Ticker("TIP")
HYG = Ticker("HYG")
LQD = Ticker("LQD")
BIL = Ticker("BIL")
