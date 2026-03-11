#!/usr/bin/env python3
"""
Exportador de Archivos .SQX
===========================

Módulo profesional para:
- Exportación de estrategias a archivos .sqx
- Ranking por percentiles (top 20%)
- Filtros de calidad
- Integración con flujo de trabajo

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
"""

import json
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
import warnings

# Configurar warnings
warnings.filterwarnings("ignore")

# Configurar logging
logger = logging.getLogger(__name__)

# Ruta por defecto del archivo de configuración
_CONFIG_PATH = Path(__file__).parents[2] / "config" / "trading_config.json"

# Criterios por defecto (se usan si no existe el archivo de configuración)
_DEFAULT_QUALITY_CRITERIA = {
    'min_cagr': 0.10,
    'min_sharpe': 0.8,
    'max_drawdown': 0.25,
    'min_trades': 50,
}


def _cargar_config_sqx() -> Dict[str, Any]:
    """Carga la sección sqx_export de trading_config.json."""
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg.get("sqx_export", {})
    except Exception:
        return {}


class SQXExporter:
    """Exportador profesional de archivos .sqx."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializar exportador .sqx.

        Los criterios de calidad y percentil se leen de ``trading_config.json``.
        Se puede pasar una ruta alternativa de configuración.

        Args:
            config_path: Ruta opcional a un archivo JSON de configuración
                         alternativo a ``config/trading_config.json``.
        """
        self.logger = logging.getLogger(__name__)

        # Cargar configuración externa
        cfg_path = config_path or _CONFIG_PATH
        sqx_cfg: Dict[str, Any] = {}
        try:
            with open(cfg_path, encoding="utf-8") as f:
                sqx_cfg = json.load(f).get("sqx_export", {})
        except Exception as exc:
            self.logger.warning(
                "No se pudo leer configuración SQX desde %s: %s — usando valores por defecto",
                cfg_path, exc,
            )

        # Criterios de calidad (configurables)
        criteria = sqx_cfg.get("quality_criteria", _DEFAULT_QUALITY_CRITERIA)
        self.quality_criteria = {
            'min_cagr': float(criteria.get('min_cagr', 0.10)),
            'min_sharpe': float(criteria.get('min_sharpe', 0.8)),
            'max_drawdown': float(criteria.get('max_drawdown', 0.25)),
            'min_trades': int(criteria.get('min_trades', 50)),
        }
        self.percentile_threshold: float = float(
            sqx_cfg.get("percentile_threshold", 0.8)
        )
        self.ranking_column: str = sqx_cfg.get("ranking_column", "CAGR")
        self.logger.info("📁 Exportador .sqx inicializado (config: %s)", cfg_path)
    
    def apply_quality_filters(self, strategies_data: pd.DataFrame) -> pd.DataFrame:
        """Aplicar filtros de calidad a las estrategias."""
        self.logger.info("🔍 Aplicando filtros de calidad")
        
        try:
            filtered_data = strategies_data.copy()
            
            # Filtro por CAGR mínimo
            if 'CAGR' in filtered_data.columns:
                filtered_data = filtered_data[filtered_data['CAGR'] >= self.quality_criteria['min_cagr']]
                self.logger.info(f"✅ Filtro CAGR: {len(filtered_data)} estrategias")
            
            # Filtro por Sharpe Ratio mínimo
            if 'Sharpe_Ratio' in filtered_data.columns:
                filtered_data = filtered_data[filtered_data['Sharpe_Ratio'] >= self.quality_criteria['min_sharpe']]
                self.logger.info(f"✅ Filtro Sharpe: {len(filtered_data)} estrategias")
            
            # Filtro por Max Drawdown máximo
            if 'Max_Drawdown' in filtered_data.columns:
                filtered_data = filtered_data[filtered_data['Max_Drawdown'] <= self.quality_criteria['max_drawdown']]
                self.logger.info(f"✅ Filtro Drawdown: {len(filtered_data)} estrategias")
            
            # Filtro por número mínimo de trades
            if 'Total_Trades' in filtered_data.columns:
                filtered_data = filtered_data[filtered_data['Total_Trades'] >= self.quality_criteria['min_trades']]
                self.logger.info(f"✅ Filtro Trades: {len(filtered_data)} estrategias")
            
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"❌ Error en filtros de calidad: {e}")
            raise
    
    def rank_by_percentiles(self, strategies_data: pd.DataFrame, 
                           ranking_column: str = 'CAGR') -> pd.DataFrame:
        """Ranking de estrategias por percentiles."""
        self.logger.info(f"📊 Ranking por percentiles usando {ranking_column}")
        
        try:
            if ranking_column not in strategies_data.columns:
                self.logger.warning(f"⚠️ Columna {ranking_column} no encontrada, usando CAGR")
                ranking_column = 'CAGR'
            
            if ranking_column in strategies_data.columns:
                # Calcular percentil threshold
                percentile_value = strategies_data[ranking_column].quantile(self.percentile_threshold)
                
                # Filtrar top percentil
                top_strategies = strategies_data[strategies_data[ranking_column] >= percentile_value]
                
                # Ordenar por ranking_column descendente
                top_strategies = top_strategies.sort_values(ranking_column, ascending=False)
                
                self.logger.info(f"✅ Top {int((1-self.percentile_threshold)*100)}%: {len(top_strategies)} estrategias")
                return top_strategies
            else:
                self.logger.warning("⚠️ No se encontró columna de ranking válida")
                return strategies_data
                
        except Exception as e:
            self.logger.error(f"❌ Error en ranking por percentiles: {e}")
            raise
    
    def create_sqx_content(self, strategy_data: pd.Series) -> str:
        """Crear contenido XML para archivo .sqx."""
        try:
            # Crear estructura XML
            strategy = ET.Element("Strategy")
            
            # Nombre de la estrategia
            name_elem = ET.SubElement(strategy, "Name")
            name_elem.text = str(strategy_data.get('Strategy_Name', 'Unknown'))
            
            # Parámetros
            parameters = ET.SubElement(strategy, "Parameters")
            
            # CAGR
            cagr_elem = ET.SubElement(parameters, "CAGR")
            cagr_elem.text = f"{strategy_data.get('CAGR', 0.0):.4f}"
            
            # Sharpe Ratio
            sharpe_elem = ET.SubElement(parameters, "SharpeRatio")
            sharpe_elem.text = f"{strategy_data.get('Sharpe_Ratio', 0.0):.4f}"
            
            # Max Drawdown
            drawdown_elem = ET.SubElement(parameters, "MaxDrawdown")
            drawdown_elem.text = f"{strategy_data.get('Max_Drawdown', 0.0):.4f}"
            
            # Total Trades
            trades_elem = ET.SubElement(parameters, "TotalTrades")
            trades_elem.text = str(strategy_data.get('Total_Trades', 0))
            
            # Profit Factor
            if 'Profit_Factor' in strategy_data:
                pf_elem = ET.SubElement(parameters, "ProfitFactor")
                pf_elem.text = f"{strategy_data.get('Profit_Factor', 0.0):.4f}"
            
            # Win Rate
            if 'Win_Rate' in strategy_data:
                wr_elem = ET.SubElement(parameters, "WinRate")
                wr_elem.text = f"{strategy_data.get('Win_Rate', 0.0):.4f}"
            
            # Factor K (si existe)
            if 'Factor_K' in strategy_data:
                fk_elem = ET.SubElement(parameters, "FactorK")
                fk_elem.text = f"{strategy_data.get('Factor_K', 0.0):.4f}"
            
            # QVA Score (si existe)
            if 'QVA_Score' in strategy_data:
                qva_elem = ET.SubElement(parameters, "QVAScore")
                qva_elem.text = f"{strategy_data.get('QVA_Score', 0.0):.4f}"
            
            # Formatear XML
            rough_string = ET.tostring(strategy, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            formatted_xml = reparsed.toprettyxml(indent="  ")
            
            return formatted_xml
            
        except Exception as e:
            self.logger.error(f"❌ Error creando contenido .sqx: {e}")
            raise
    
    def export_strategies_to_sqx(self, strategies_data: pd.DataFrame, 
                                output_dir: Path) -> List[Path]:
        """Exportar estrategias a archivos .sqx."""
        self.logger.info(f"📁 Exportando {len(strategies_data)} estrategias a {output_dir}")
        
        try:
            # Convertir a Path si es string
            if isinstance(output_dir, str):
                output_dir = Path(output_dir)
            
            # Crear directorio si no existe
            output_dir.mkdir(parents=True, exist_ok=True)
            
            exported_files = []
            
            for idx, strategy_data in strategies_data.iterrows():
                try:
                    # Obtener nombre de estrategia
                    strategy_name = strategy_data.get('Strategy_Name', f'Strategy_{idx}')
                    
                    # Limpiar nombre para archivo
                    safe_name = "".join(c for c in strategy_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_name = safe_name.replace(' ', '_')
                    
                    # Crear archivo .sqx
                    sqx_file_path = output_dir / f"{safe_name}.sqx"
                    
                    # Generar contenido XML
                    sqx_content = self.create_sqx_content(strategy_data)
                    
                    # Escribir archivo
                    with open(sqx_file_path, 'w', encoding='utf-8') as f:
                        f.write(sqx_content)
                    
                    exported_files.append(sqx_file_path)
                    self.logger.debug(f"✅ Exportado: {sqx_file_path.name}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error exportando estrategia {idx}: {e}")
                    continue
            
            self.logger.info(f"✅ Exportación completada: {len(exported_files)} archivos .sqx")
            return exported_files
            
        except Exception as e:
            self.logger.error(f"❌ Error en exportación .sqx: {e}")
            raise
    
    def complete_sqx_workflow(self, strategies_data: pd.DataFrame, 
                             output_dir: Path,
                             ranking_column: str = 'CAGR') -> Dict[str, Any]:
        """Flujo de trabajo completo para exportación .sqx."""
        self.logger.info("🚀 Iniciando flujo de trabajo completo .sqx")
        
        try:
            results = {
                'total_strategies': len(strategies_data),
                'quality_filtered': 0,
                'percentile_filtered': 0,
                'exported_files': [],
                'output_directory': str(output_dir)
            }
            
            # Paso 1: Aplicar filtros de calidad
            quality_strategies = self.apply_quality_filters(strategies_data)
            results['quality_filtered'] = len(quality_strategies)
            
            if len(quality_strategies) == 0:
                self.logger.warning("⚠️ No hay estrategias que cumplan los criterios de calidad")
                return results
            
            # Paso 2: Ranking por percentiles
            top_strategies = self.rank_by_percentiles(quality_strategies, ranking_column)
            results['percentile_filtered'] = len(top_strategies)
            
            if len(top_strategies) == 0:
                self.logger.warning("⚠️ No hay estrategias en el percentil superior")
                return results
            
            # Paso 3: Exportar archivos .sqx
            exported_files = self.export_strategies_to_sqx(top_strategies, output_dir)
            results['exported_files'] = [str(f) for f in exported_files]
            
            # Resumen final
            self.logger.info(f"✅ Flujo completado:")
            self.logger.info(f"   - Total estrategias: {results['total_strategies']}")
            self.logger.info(f"   - Después de filtros de calidad: {results['quality_filtered']}")
            self.logger.info(f"   - Top {int((1-self.percentile_threshold)*100)}%: {results['percentile_filtered']}")
            self.logger.info(f"   - Archivos exportados: {len(results['exported_files'])}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error en flujo de trabajo .sqx: {e}")
            raise
    
    def validate_sqx_file(self, sqx_file_path: Path) -> bool:
        """Validar archivo .sqx generado."""
        try:
            if not sqx_file_path.exists():
                return False
            
            # Leer y parsear XML
            with open(sqx_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar estructura básica
            if '<Strategy>' not in content or '<Name>' not in content:
                return False
            
            # Intentar parsear XML
            ET.fromstring(content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validando archivo .sqx: {e}")
            return False
    
    def get_export_summary(self, results: Dict[str, Any]) -> str:
        """Generar resumen de exportación."""
        summary = f"""
📊 RESUMEN DE EXPORTACIÓN .SQX
==============================

📈 Estrategias procesadas:
   - Total inicial: {results['total_strategies']}
   - Después de filtros de calidad: {results['quality_filtered']}
   - Top {int((1-self.percentile_threshold)*100)}% seleccionadas: {results['percentile_filtered']}

📁 Archivos generados:
   - Cantidad: {len(results['exported_files'])}
   - Directorio: {results['output_directory']}

✅ Exportación completada exitosamente
"""
        return summary 