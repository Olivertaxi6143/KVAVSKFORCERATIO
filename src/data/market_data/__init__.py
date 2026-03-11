"""
market_data — Proveedores de Datos de Mercado OHLCV
=====================================================

Submódulo para carga de datos históricos de mercado desde múltiples fuentes:

- ``mql5_loader``:   Archivos CSV exportados desde MetaTrader 4/5 (MQL4/MQL5)
- ``mt5_connector``: Conexión en vivo vía librería ``MetaTrader5`` (opcional)
- ``yfinance_loader``: Datos históricos via yfinance (opcional)

Todos los loaders devuelven un ``pd.DataFrame`` con columnas estandarizadas:
    datetime, open, high, low, close, volume, symbol, timeframe

Uso::

    from src.data.market_data import MQL5Loader, MT5Connector, YFinanceLoader

    loader = MQL5Loader()
    df = loader.load("DATOSMQL5.csv")

    connector = MT5Connector()
    df = connector.fetch("EURUSD", "M15", bars=5000)

    yf = YFinanceLoader()
    df = yf.fetch("AAPL", period="2y", interval="1d")
"""

from .mql5_loader import MQL5Loader
from .mt5_connector import MT5Connector
from .yfinance_loader import YFinanceLoader

__all__ = ["MQL5Loader", "MT5Connector", "YFinanceLoader"]
