#!/usr/bin/env python3
"""
Parser de Archivos .SQX de StrategyQuant
=========================================

Módulo profesional para:
- Importación de archivos .sqx generados por StrategyQuant X
- Soporte de XML simple (formato interno) y XML multi-estrategia
- Conversión a DataFrame normalizado compatible con el pipeline QVA
- Carga por lote desde carpeta de archivos .sqx
- Validación de estructura y campos requeridos

Formatos soportados:
  1. XML simple: un único <Strategy> por archivo (formato interno de este sistema)
  2. XML multi-estrategia: <Strategies><Strategy>...</Strategy></Strategies>
  3. CSV Databank Export de StrategyQuant (columnas en inglés estándar SQ)

Autor: Sistema de Análisis Cuantitativo
Fecha: 2026-03-11
Versión: 1.0.0
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pandas as pd

from .column_mapping import normalize_column_names

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapeo de etiquetas XML → nombre interno normalizado
# Incluye tanto el formato interno (sqx_exporter.py) como variantes SQX reales
# ---------------------------------------------------------------------------
_XML_TAG_MAP: dict[str, str] = {
    # Métricas principales
    "Name": "Strategy_Name",
    "StrategyName": "Strategy_Name",
    "CAGR": "CAGR",
    "SharpeRatio": "Sharpe_Ratio",
    "Sharpe": "Sharpe_Ratio",
    "MaxDrawdown": "Max_DD_%",
    "MaxDD": "Max_DD_%",
    "Drawdown": "Max_DD_%",
    "TotalTrades": "#_of_trades",
    "NumTrades": "#_of_trades",
    "ProfitFactor": "Profit_factor",
    "WinRate": "Winning_Percent",
    "WinPercent": "Winning_Percent",
    "NetProfit": "Net_profit",
    "Expectancy": "Expectancy",
    "SQN": "SQN",
    "RecoveryFactor": "RecoveryFactor",
    "CalmarRatio": "CalmarRatio",
    "SortinoRatio": "Sortino_Ratio",
    "RINAIndex": "RINAIndex",
    "Exposure": "Exposure",
    "Stagnation": "Stagnation",
    "UlcerIndex": "Ulcer_Index_%",
    "VaR95": "VaR_95%",
    "CVaR95": "CVaR_95%",
    "AvgBarsInTrade": "Avg_Bars_in_Trade",
    "MaxConsecLosses": "Max_Consec_Losses",
    "PayoutRatio": "Payout_ratio",
    # Scores del sistema interno
    "FactorK": "Factor_K",
    "QVAScore": "QVA_Score",
    "UnifiedScore": "Unified_Score",
    # Metadatos de mercado
    "Symbol": "Symbol",
    "Timeframe": "Timeframe",
    "DataStart": "Data_Start",
    "DataEnd": "Data_End",
    "InitialCapital": "Initial_Capital",
    "Currency": "Currency",
    # IS / OOS
    "SharpeRatioIS": "Sharpe_Ratio_IS",
    "SharpeRatioOOS": "Sharpe_Ratio_OOS",
    "ProfitFactorIS": "Profit_Factor_IS",
    "ProfitFactorOOS": "Profit_Factor_OOS",
    "CAGRIS": "CAGR_IS",
    "CAGROOS": "CAGR_OOS",
    "DrawdownIS": "Max_Drawdown_IS",
    "DrawdownOOS": "Max_Drawdown_OOS",
    "WinPercentIS": "Winning_Percent_IS",
    "WinPercentOOS": "Winning_Percent_OOS",
}

# Campos numéricos — se intentará conversión automática a float
_NUMERIC_FIELDS: set[str] = {
    "CAGR", "Sharpe_Ratio", "Max_DD_%", "#_of_trades", "Profit_factor",
    "Winning_Percent", "Net_profit", "Expectancy", "SQN", "RecoveryFactor",
    "CalmarRatio", "Sortino_Ratio", "RINAIndex", "Exposure", "Stagnation",
    "Ulcer_Index_%", "VaR_95%", "CVaR_95%", "Avg_Bars_in_Trade",
    "Max_Consec_Losses", "Payout_ratio", "Factor_K", "QVA_Score",
    "Unified_Score", "Initial_Capital",
    "Sharpe_Ratio_IS", "Sharpe_Ratio_OOS", "Profit_Factor_IS",
    "Profit_Factor_OOS", "CAGR_IS", "CAGR_OOS", "Max_Drawdown_IS",
    "Max_Drawdown_OOS", "Winning_Percent_IS", "Winning_Percent_OOS",
}


# ---------------------------------------------------------------------------
# Funciones auxiliares privadas
# ---------------------------------------------------------------------------

def _parse_element_to_dict(element: ET.Element) -> dict[str, Any]:
    """
    Convierte un elemento XML <Strategy> en diccionario normalizado.

    Busca campos tanto en hijos directos como bajo <Parameters>, <Results>,
    <Metadata> para mayor compatibilidad con variantes del formato SQX.
    """
    record: dict[str, Any] = {}

    def _visit(node: ET.Element) -> None:
        tag = node.tag
        text = (node.text or "").strip()

        if tag in ("Strategy", "Parameters", "Results", "Metadata",
                   "BacktestResults", "StrategyConfig"):
            # Contenedor — explorar hijos
            for child in node:
                _visit(child)
        else:
            mapped = _XML_TAG_MAP.get(tag, tag)
            if text:
                record[mapped] = text

    _visit(element)
    return record


def _coerce_numeric(record: dict[str, Any]) -> dict[str, Any]:
    """Convierte a float los campos numéricos conocidos."""
    for campo in _NUMERIC_FIELDS:
        if campo in record:
            try:
                record[campo] = float(str(record[campo]).replace(",", ".").replace("%", ""))
            except (ValueError, TypeError):
                pass
    return record


def _records_to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Construye DataFrame normalizado a partir de lista de registros."""
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df = normalize_column_names(df)
    return df


# ---------------------------------------------------------------------------
# Parser principal
# ---------------------------------------------------------------------------

class SQXParser:
    """
    Parser profesional para archivos .sqx de StrategyQuant.

    Soporta:
    - Un único archivo .sqx → una o múltiples estrategias
    - Carga por lote desde directorio
    - CSV Databank Export de StrategyQuant

    Uso básico::

        parser = SQXParser()
        df = parser.parse_file("strategies/mi_estrategia.sqx")
        df_batch = parser.parse_directory("strategies/")
        df_csv = parser.parse_databank_csv("DatabankExport_M1.csv")
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.info("Parser .sqx inicializado")

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def parse_file(self, file_path: str | Path) -> pd.DataFrame:
        """
        Parsea un único archivo .sqx y devuelve DataFrame normalizado.

        Args:
            file_path: Ruta al archivo .sqx

        Returns:
            DataFrame con una fila por estrategia encontrada.
            Vacío si el archivo no es válido.
        """
        path = Path(file_path)
        if not path.exists():
            self.logger.error("Archivo no encontrado: %s", path)
            return pd.DataFrame()
        if path.suffix.lower() not in (".sqx", ".xml"):
            self.logger.warning("Extensión inesperada '%s' en: %s", path.suffix, path)

        try:
            return self._parse_xml_file(path)
        except ET.ParseError as exc:
            self.logger.error("XML inválido en %s: %s", path, exc)
            return pd.DataFrame()
        except Exception as exc:
            self.logger.error("Error inesperado parseando %s: %s", path, exc)
            return pd.DataFrame()

    def parse_directory(
        self,
        folder_path: str | Path,
        pattern: str = "*.sqx",
    ) -> pd.DataFrame:
        """
        Carga por lote todos los archivos .sqx de una carpeta.

        Args:
            folder_path: Directorio que contiene los archivos .sqx
            pattern: Patrón glob (por defecto ``*.sqx``)

        Returns:
            DataFrame concatenado con todas las estrategias encontradas.
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            self.logger.error("Directorio no encontrado: %s", folder)
            return pd.DataFrame()

        sqx_files = sorted(folder.glob(pattern))
        if not sqx_files:
            self.logger.warning("No se encontraron archivos '%s' en: %s", pattern, folder)
            return pd.DataFrame()

        self.logger.info("Cargando %d archivos .sqx desde: %s", len(sqx_files), folder)

        frames: list[pd.DataFrame] = []
        errores = 0
        for sqx_file in sqx_files:
            df = self.parse_file(sqx_file)
            if not df.empty:
                # Registrar fichero origen para trazabilidad
                df["_sqx_source_file"] = sqx_file.name
                frames.append(df)
            else:
                errores += 1

        if not frames:
            self.logger.warning("Ningún archivo .sqx válido encontrado en: %s", folder)
            return pd.DataFrame()

        resultado = pd.concat(frames, ignore_index=True)
        self.logger.info(
            "Carga completada: %d estrategias de %d archivos (%d errores)",
            len(resultado),
            len(sqx_files) - errores,
            errores,
        )
        return resultado

    def parse_databank_csv(self, file_path: str | Path) -> pd.DataFrame:
        """
        Carga el CSV de Databank Export de StrategyQuant.

        El CSV tiene columnas en inglés (Strategy Name, Profit Factor, etc.)
        que se normalizan automáticamente con ``column_mapping.py``.

        Args:
            file_path: Ruta al CSV exportado desde StrategyQuant

        Returns:
            DataFrame normalizado, listo para el pipeline QVA.
        """
        path = Path(file_path)
        if not path.exists():
            self.logger.error("CSV no encontrado: %s", path)
            return pd.DataFrame()

        try:
            # Intentar separadores comunes de SQX (coma o punto y coma)
            df = self._try_read_csv(path)
            if df.empty:
                self.logger.error("CSV vacío o sin datos válidos: %s", path)
                return pd.DataFrame()

            df = normalize_column_names(df)
            self._coerce_all_numeric(df)

            self.logger.info(
                "Databank CSV cargado: %d estrategias, %d columnas — %s",
                len(df), len(df.columns), path.name,
            )
            return df

        except Exception as exc:
            self.logger.error("Error cargando Databank CSV %s: %s", path, exc)
            return pd.DataFrame()

    def validate_file(self, file_path: str | Path) -> dict[str, Any]:
        """
        Valida un archivo .sqx y devuelve informe de calidad.

        Returns:
            Diccionario con claves: ``valid``, ``strategies_found``,
            ``missing_fields``, ``warnings``.
        """
        reporte: dict[str, Any] = {
            "valid": False,
            "strategies_found": 0,
            "missing_fields": [],
            "warnings": [],
        }
        campos_requeridos = {"Strategy_Name", "CAGR", "Sharpe_Ratio", "#_of_trades"}

        df = self.parse_file(file_path)
        if df.empty:
            reporte["warnings"].append("No se pudo parsear el archivo")
            return reporte

        reporte["strategies_found"] = len(df)
        reporte["missing_fields"] = [c for c in campos_requeridos if c not in df.columns]
        reporte["valid"] = len(reporte["missing_fields"]) == 0

        if not reporte["valid"]:
            reporte["warnings"].append(
                f"Campos requeridos ausentes: {reporte['missing_fields']}"
            )
        return reporte

    # ------------------------------------------------------------------
    # Métodos privados
    # ------------------------------------------------------------------

    def _parse_xml_file(self, path: Path) -> pd.DataFrame:
        """Parsea XML y extrae estrategias independientemente del esquema raíz."""
        tree = ET.parse(path)
        root = tree.getroot()
        records: list[dict[str, Any]] = []

        root_tag = root.tag

        if root_tag == "Strategy":
            # Formato interno: un único <Strategy> por archivo
            record = _parse_element_to_dict(root)
            record = _coerce_numeric(record)
            if not record.get("Strategy_Name"):
                record["Strategy_Name"] = path.stem
            records.append(record)

        elif root_tag in ("Strategies", "StrategyList", "DataBank", "Root"):
            # Formato multi-estrategia
            for child in root.findall("Strategy"):
                record = _parse_element_to_dict(child)
                record = _coerce_numeric(record)
                if not record.get("Strategy_Name"):
                    record["Strategy_Name"] = f"{path.stem}_{len(records)}"
                records.append(record)

        else:
            # Esquema desconocido — intentar búsqueda recursiva de <Strategy>
            self.logger.warning(
                "Esquema XML desconocido (raíz: <%s>) en %s — búsqueda recursiva",
                root_tag, path.name,
            )
            for elem in root.iter("Strategy"):
                record = _parse_element_to_dict(elem)
                record = _coerce_numeric(record)
                if not record.get("Strategy_Name"):
                    record["Strategy_Name"] = f"{path.stem}_{len(records)}"
                records.append(record)

        if not records:
            self.logger.warning("Sin estrategias válidas en: %s", path.name)
            return pd.DataFrame()

        df = _records_to_dataframe(records)
        self.logger.debug("Parseado %s → %d estrategias", path.name, len(df))
        return df

    def _try_read_csv(self, path: Path) -> pd.DataFrame:
        """
        Intenta leer el CSV con separadores comunes de StrategyQuant.
        Prueba: coma, punto y coma y tabulación.
        """
        for sep in (",", ";", "\t"):
            try:
                df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", low_memory=False)
                if len(df.columns) > 2:  # Mínimo de columnas para ser válido
                    return df
            except Exception:
                continue
        # Último intento con detección automática
        try:
            return pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig",
                               low_memory=False)
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def _coerce_all_numeric(df: pd.DataFrame) -> None:
        """Convierte a numérico todas las columnas que lo permitan (in-place)."""
        for col in df.columns:
            if df[col].dtype == object:
                convertida = pd.to_numeric(
                    df[col].astype(str).str.replace(",", ".").str.replace("%", ""),
                    errors="ignore",
                )
                if convertida.dtype != object:
                    df[col] = convertida
