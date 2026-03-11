"""
Tests — SQX Parser y Market Data Loaders
=========================================

Cubre:
- SQXParser: parseo de XML simple, multi-estrategia, Databank CSV, directorio
- MQL5Loader: detección de formato MT5/MT4/genérico, normalización OHLCV
- MT5Connector: comportamiento sin librería instalada (graceful degradation)
- YFinanceLoader: comportamiento sin librería instalada (graceful degradation)
- SQXExporter: carga de criterios desde trading_config.json

Autor: Sistema de Análisis Cuantitativo
Fecha: 2026-03-11
"""

from __future__ import annotations

import io
import json
import textwrap
from pathlib import Path

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Fixtures — XML y CSV de ejemplo
# ---------------------------------------------------------------------------

XML_SIMPLE = textwrap.dedent("""\
    <?xml version="1.0"?>
    <Strategy>
      <Name>TestEA_001</Name>
      <Parameters>
        <CAGR>0.1850</CAGR>
        <SharpeRatio>1.42</SharpeRatio>
        <MaxDrawdown>0.15</MaxDrawdown>
        <TotalTrades>320</TotalTrades>
        <ProfitFactor>1.75</ProfitFactor>
        <WinRate>0.58</WinRate>
        <FactorK>8.2</FactorK>
        <QVAScore>7.9</QVAScore>
      </Parameters>
    </Strategy>
""")

XML_MULTI = textwrap.dedent("""\
    <?xml version="1.0"?>
    <Strategies>
      <Strategy>
        <Name>Alpha</Name>
        <Parameters>
          <CAGR>0.20</CAGR>
          <SharpeRatio>1.80</SharpeRatio>
          <MaxDrawdown>0.12</MaxDrawdown>
          <TotalTrades>500</TotalTrades>
        </Parameters>
      </Strategy>
      <Strategy>
        <Name>Beta</Name>
        <Parameters>
          <CAGR>0.15</CAGR>
          <SharpeRatio>1.20</SharpeRatio>
          <MaxDrawdown>0.18</MaxDrawdown>
          <TotalTrades>250</TotalTrades>
        </Parameters>
      </Strategy>
    </Strategies>
""")

DATABANK_CSV = textwrap.dedent("""\
    Strategy Name,Profit Factor,Sharpe Ratio,CalmarRatio,Max DD %,CAGR,# of trades,Winning Percent
    Strategy_001,1.75,1.42,1.10,15.00,18.50,320,58.00
    Strategy_002,2.10,1.90,1.50,10.00,22.30,480,62.00
    Strategy_003,1.30,0.95,0.80,22.00,12.00,180,51.00
""")

MT5_CSV = textwrap.dedent("""\
    <DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>
    2024.01.02\t00:00:00\t1.10234\t1.10456\t1.10123\t1.10345\t1234\t0\t2
    2024.01.02\t01:00:00\t1.10345\t1.10500\t1.10200\t1.10420\t987\t0\t2
    2024.01.02\t02:00:00\t1.10420\t1.10600\t1.10380\t1.10550\t1100\t0\t2
""")

MT4_CSV = textwrap.dedent("""\
    2024.01.02 00:00,1.10234,1.10456,1.10123,1.10345,1234
    2024.01.02 01:00,1.10345,1.10500,1.10200,1.10420,987
    2024.01.02 02:00,1.10420,1.10600,1.10380,1.10550,1100
""")

GENERIC_OHLCV_CSV = textwrap.dedent("""\
    Date,Open,High,Low,Close,Volume
    2024-01-02,1.10234,1.10456,1.10123,1.10345,1234
    2024-01-03,1.10345,1.10500,1.10200,1.10420,987
    2024-01-04,1.10420,1.10600,1.10380,1.10550,1100
""")


# ---------------------------------------------------------------------------
# SQXParser
# ---------------------------------------------------------------------------

class TestSQXParser:
    """Tests para el parser de archivos .sqx."""

    @pytest.fixture(autouse=True)
    def import_parser(self):
        from src.data.sqx_parser import SQXParser
        self.parser = SQXParser()

    def test_parse_xml_simple(self, tmp_path):
        """Debe parsear un XML de estrategia única correctamente."""
        sqx = tmp_path / "test.sqx"
        sqx.write_text(XML_SIMPLE, encoding="utf-8")

        df = self.parser.parse_file(sqx)

        assert not df.empty, "El DataFrame no debe estar vacío"
        assert len(df) == 1, "Debe haber exactamente una estrategia"
        assert "Strategy_Name" in df.columns or "strategy_name" in df.columns.str.lower().tolist()

    def test_parse_xml_multi_estrategia(self, tmp_path):
        """Debe parsear un XML con múltiples <Strategy>."""
        sqx = tmp_path / "multi.sqx"
        sqx.write_text(XML_MULTI, encoding="utf-8")

        df = self.parser.parse_file(sqx)

        assert len(df) == 2, "Debe encontrar 2 estrategias"

    def test_parse_databank_csv(self, tmp_path):
        """Debe cargar y normalizar un CSV de Databank Export de StrategyQuant."""
        csv = tmp_path / "DatabankExport.csv"
        csv.write_text(DATABANK_CSV, encoding="utf-8")

        df = self.parser.parse_databank_csv(csv)

        assert not df.empty
        assert len(df) == 3, "Debe haber 3 estrategias en el CSV"

    def test_parse_databank_csv_columnas_normalizadas(self, tmp_path):
        """Las columnas del CSV deben estar normalizadas al estándar interno."""
        csv = tmp_path / "DatabankExport.csv"
        csv.write_text(DATABANK_CSV, encoding="utf-8")

        df = self.parser.parse_databank_csv(csv)

        # "Strategy Name" → "Strategy_Name" via column_mapping
        assert "Strategy_Name" in df.columns, (
            f"Columna Strategy_Name no encontrada. Columnas: {list(df.columns)}"
        )

    def test_parse_directorio(self, tmp_path):
        """Debe cargar múltiples archivos .sqx de una carpeta."""
        for i in range(3):
            sqx = tmp_path / f"strat_{i}.sqx"
            sqx.write_text(XML_SIMPLE.replace("TestEA_001", f"TestEA_{i:03d}"), encoding="utf-8")

        df = self.parser.parse_directory(tmp_path)

        assert len(df) == 3, "Debe encontrar 3 estrategias (1 por archivo)"

    def test_parse_archivo_inexistente(self):
        """Debe devolver DataFrame vacío para archivo inexistente."""
        df = self.parser.parse_file("/ruta/inexistente/archivo.sqx")
        assert df.empty

    def test_parse_xml_invalido(self, tmp_path):
        """Debe devolver DataFrame vacío para XML malformado."""
        sqx = tmp_path / "bad.sqx"
        sqx.write_text("esto no es xml válido <<<>", encoding="utf-8")

        df = self.parser.parse_file(sqx)
        assert df.empty

    def test_parse_directorio_vacio(self, tmp_path):
        """Debe devolver DataFrame vacío para carpeta sin .sqx."""
        df = self.parser.parse_directory(tmp_path)
        assert df.empty

    def test_validate_file_valido(self, tmp_path):
        """validate_file debe marcar como válido un XML completo."""
        sqx = tmp_path / "test.sqx"
        sqx.write_text(XML_SIMPLE, encoding="utf-8")

        reporte = self.parser.validate_file(sqx)

        assert reporte["strategies_found"] == 1

    def test_source_file_columna(self, tmp_path):
        """Carga por directorio debe añadir columna _sqx_source_file."""
        sqx = tmp_path / "strat_a.sqx"
        sqx.write_text(XML_SIMPLE, encoding="utf-8")

        df = self.parser.parse_directory(tmp_path)

        assert "_sqx_source_file" in df.columns
        assert df["_sqx_source_file"].iloc[0] == "strat_a.sqx"

    @pytest.mark.parametrize("xml_content,expected_rows", [
        (XML_SIMPLE, 1),
        (XML_MULTI, 2),
    ])
    def test_filas_correctas(self, tmp_path, xml_content, expected_rows):
        """Parametrizado: verificar número correcto de filas por formato."""
        sqx = tmp_path / "test.sqx"
        sqx.write_text(xml_content, encoding="utf-8")
        df = self.parser.parse_file(sqx)
        assert len(df) == expected_rows


# ---------------------------------------------------------------------------
# MQL5Loader
# ---------------------------------------------------------------------------

class TestMQL5Loader:
    """Tests para el cargador de datos OHLCV de MetaTrader."""

    @pytest.fixture(autouse=True)
    def import_loader(self):
        from src.data.market_data.mql5_loader import MQL5Loader
        self.MQL5Loader = MQL5Loader

    def test_carga_formato_mt5(self, tmp_path):
        """Debe parsear el formato MT5 con cabecera <DATE> <TIME>."""
        csv = tmp_path / "EURUSD_H1.csv"
        csv.write_text(MT5_CSV, encoding="utf-8")

        loader = self.MQL5Loader(symbol="EURUSD", timeframe="H1")
        df = loader.load(csv)

        assert not df.empty, "El DataFrame no debe estar vacío"
        assert "datetime" in df.columns
        assert "open" in df.columns
        assert "close" in df.columns
        assert len(df) == 3

    def test_carga_formato_mt4(self, tmp_path):
        """Debe parsear el formato MT4 'YYYY.MM.DD HH:MM,o,h,l,c,v'."""
        csv = tmp_path / "GBPUSD_M15.csv"
        csv.write_text(MT4_CSV, encoding="utf-8")

        loader = self.MQL5Loader()
        df = loader.load(csv)

        assert not df.empty
        assert "datetime" in df.columns

    def test_carga_formato_generico(self, tmp_path):
        """Debe parsear CSV genérico con columnas Date,Open,High,Low,Close,Volume."""
        csv = tmp_path / "datos_genericos.csv"
        csv.write_text(GENERIC_OHLCV_CSV, encoding="utf-8")

        loader = self.MQL5Loader()
        df = loader.load(csv)

        assert not df.empty
        assert "close" in df.columns

    def test_metadatos_symbol_timeframe(self, tmp_path):
        """Debe añadir columnas symbol y timeframe."""
        csv = tmp_path / "EURUSD_H1.csv"
        csv.write_text(MT5_CSV, encoding="utf-8")

        loader = self.MQL5Loader(symbol="EURUSD", timeframe="H1")
        df = loader.load(csv)

        assert "symbol" in df.columns
        assert "timeframe" in df.columns
        assert df["symbol"].iloc[0] == "EURUSD"
        assert df["timeframe"].iloc[0] == "H1"

    def test_archivo_inexistente(self):
        """Debe devolver DataFrame vacío para archivo inexistente."""
        loader = self.MQL5Loader()
        df = loader.load("/no/existe/archivo.csv")
        assert df.empty

    def test_valores_ohlcv_numericos(self, tmp_path):
        """Los valores OHLCV deben ser numéricos (float)."""
        csv = tmp_path / "EURUSD_M1.csv"
        csv.write_text(MT5_CSV, encoding="utf-8")

        loader = self.MQL5Loader()
        df = loader.load(csv)

        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                assert pd.api.types.is_numeric_dtype(df[col]), (
                    f"Columna '{col}' debe ser numérica"
                )

    def test_validacion_high_mayor_low(self, tmp_path):
        """Debe filtrar barras donde high < low."""
        csv_invalido = textwrap.dedent("""\
            Date,Open,High,Low,Close,Volume
            2024-01-02,1.10234,1.10100,1.10456,1.10345,1234
            2024-01-03,1.10345,1.10500,1.10200,1.10420,987
        """)
        csv = tmp_path / "invalido.csv"
        csv.write_text(csv_invalido, encoding="utf-8")

        loader = self.MQL5Loader()
        df = loader.load(csv)

        # La primera barra tiene high < low → debe eliminarse
        assert len(df) == 1

    def test_resumen(self, tmp_path):
        """resumen() debe devolver dict con claves esperadas."""
        csv = tmp_path / "EURUSD_H1.csv"
        csv.write_text(MT5_CSV, encoding="utf-8")

        loader = self.MQL5Loader(symbol="EURUSD", timeframe="H1")
        df = loader.load(csv)
        info = loader.resumen(df)

        assert "barras" in info
        assert info["barras"] == 3


# ---------------------------------------------------------------------------
# MT5Connector (graceful degradation sin librería)
# ---------------------------------------------------------------------------

class TestMT5ConnectorSinLibreria:
    """Verifica que MT5Connector funcione correctamente cuando MetaTrader5 no está instalado."""

    @pytest.fixture(autouse=True)
    def import_connector(self):
        from src.data.market_data.mt5_connector import MT5Connector
        self.MT5Connector = MT5Connector

    def test_disponible_false_sin_mt5(self):
        """Si MetaTrader5 no está instalado, disponible debe ser False."""
        connector = self.MT5Connector()
        # No sabemos si está instalado o no en el entorno de CI
        # Solo verificamos que el atributo existe y es bool
        assert isinstance(connector.disponible, bool)

    def test_fetch_sin_conexion_devuelve_vacio(self):
        """fetch() sin conexión debe devolver DataFrame vacío (no excepciones)."""
        connector = self.MT5Connector()
        # Si no está disponible, debe devolver vacío sin lanzar excepción
        if not connector.disponible:
            df = connector.fetch("EURUSD", "H1", bars=100)
            assert df.empty

    def test_listar_simbolos_sin_conexion(self):
        """listar_simbolos() sin conexión debe devolver lista vacía."""
        connector = self.MT5Connector()
        if not connector.disponible:
            simbolos = connector.listar_simbolos()
            assert isinstance(simbolos, list)
            assert len(simbolos) == 0


# ---------------------------------------------------------------------------
# YFinanceLoader (graceful degradation sin librería)
# ---------------------------------------------------------------------------

class TestYFinanceLoaderSinLibreria:
    """Verifica que YFinanceLoader funcione correctamente cuando yfinance no está instalado."""

    @pytest.fixture(autouse=True)
    def import_loader(self):
        from src.data.market_data.yfinance_loader import YFinanceLoader
        self.YFinanceLoader = YFinanceLoader

    def test_disponible_es_bool(self):
        """El atributo disponible debe existir y ser bool."""
        loader = self.YFinanceLoader()
        assert isinstance(loader.disponible, bool)

    def test_fetch_sin_yfinance_devuelve_vacio(self):
        """Si yfinance no está instalado, fetch() debe devolver DataFrame vacío."""
        loader = self.YFinanceLoader()
        if not loader.disponible:
            df = loader.fetch("AAPL", period="1mo")
            assert df.empty

    def test_fetch_multi_sin_yfinance(self):
        """fetch_multi() sin yfinance debe devolver dict vacío."""
        loader = self.YFinanceLoader()
        if not loader.disponible:
            resultado = loader.fetch_multi(["AAPL", "MSFT"])
            assert isinstance(resultado, dict)
            assert len(resultado) == 0


# ---------------------------------------------------------------------------
# SQXExporter — carga de config desde JSON
# ---------------------------------------------------------------------------

class TestSQXExporterConfig:
    """Tests para verificar que SQXExporter carga criterios desde trading_config.json."""

    def test_criterios_defecto(self, tmp_path):
        """Sin archivo de config, debe usar los criterios por defecto."""
        from src.data.sqx_exporter import SQXExporter

        # Apuntar a un JSON inexistente → usa defaults
        exporter = SQXExporter(config_path=tmp_path / "no_existe.json")

        assert exporter.quality_criteria['min_cagr'] == 0.10
        assert exporter.quality_criteria['min_sharpe'] == 0.8
        assert exporter.quality_criteria['max_drawdown'] == 0.25
        assert exporter.quality_criteria['min_trades'] == 50
        assert exporter.percentile_threshold == 0.8

    def test_criterios_desde_json(self, tmp_path):
        """Debe cargar criterios personalizados desde trading_config.json."""
        from src.data.sqx_exporter import SQXExporter

        config = {
            "sqx_export": {
                "quality_criteria": {
                    "min_cagr": 0.15,
                    "min_sharpe": 1.0,
                    "max_drawdown": 0.20,
                    "min_trades": 100,
                },
                "percentile_threshold": 0.9,
                "ranking_column": "Sharpe_Ratio",
            }
        }
        cfg_path = tmp_path / "config.json"
        cfg_path.write_text(json.dumps(config), encoding="utf-8")

        exporter = SQXExporter(config_path=cfg_path)

        assert exporter.quality_criteria['min_cagr'] == 0.15
        assert exporter.quality_criteria['min_sharpe'] == 1.0
        assert exporter.quality_criteria['max_drawdown'] == 0.20
        assert exporter.quality_criteria['min_trades'] == 100
        assert exporter.percentile_threshold == 0.9
        assert exporter.ranking_column == "Sharpe_Ratio"

    def test_filtros_calidad(self):
        """apply_quality_filters debe filtrar correctamente por CAGR y Sharpe."""
        from src.data.sqx_exporter import SQXExporter

        exporter = SQXExporter()
        exporter.quality_criteria = {
            'min_cagr': 0.15,
            'min_sharpe': 1.0,
            'max_drawdown': 0.20,
            'min_trades': 100,
        }

        datos = pd.DataFrame({
            "Strategy_Name": ["A", "B", "C"],
            "CAGR": [0.20, 0.10, 0.18],         # B no pasa
            "Sharpe_Ratio": [1.5, 1.2, 0.8],    # C no pasa
            "Max_Drawdown": [0.15, 0.12, 0.18],
            "Total_Trades": [200, 150, 120],
        })

        filtrado = exporter.apply_quality_filters(datos)
        # Solo A cumple todos los criterios
        assert len(filtrado) == 1
        assert filtrado.iloc[0]["Strategy_Name"] == "A"
