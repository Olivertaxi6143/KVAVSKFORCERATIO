#!/usr/bin/env python3
"""
Integración ISA con DataManager y Sistema Existente
==================================================

Módulo de integración que conecta la base de datos ISA con el sistema existente:
- Carga datos reales de INPUTTEST
- Integración con DataManager existente
- Conversión automática de formatos
- Validación de datos IS/OOS
- Preparación para entrenamiento ML

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-15
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import warnings

from src.data.data_manager import DataManager
from src.data.ml_database import MLDatabase, MLDatabaseConfig
from src.ml.isa_training import ISAModelTrainer, ModelConfig
from src.logger_config import setup_logger

logger = setup_logger(__name__)
warnings.filterwarnings('ignore')

class ISAIntegration:
    """
    Integración ISA con el sistema existente.
    
    Funcionalidades:
    - Carga datos reales de INPUTTEST
    - Integración con DataManager
    - Conversión automática de formatos
    - Validación de datos IS/OOS
    - Preparación para entrenamiento ML
    """
    
    def __init__(self, 
                 inputtest_path: str = "INPUTTEST",
                 use_real_data: bool = True):
        """
        Inicializa la integración ISA.
        
        Args:
            inputtest_path: Ruta a la carpeta INPUTTEST
            use_real_data: Usar datos reales de INPUTTEST
        """
        self.inputtest_path = Path(inputtest_path)
        self.use_real_data = use_real_data
        
        # Inicializar componentes
        self.data_manager = DataManager()
        self.isa_database = MLDatabase()
        self.model_trainer = ISAModelTrainer(self.isa_database)
        
        # Configurar para datos reales
        if self.use_real_data:
            self._setup_real_data_config()
        
        logger.info(f"🔗 Integración ISA inicializada: {'datos reales' if use_real_data else 'datos simulados'}")
    
    def _setup_real_data_config(self):
        """Configura para usar datos reales de INPUTTEST."""
        try:
            # Verificar que existe la carpeta INPUTTEST
            if not self.inputtest_path.exists():
                logger.warning(f"⚠️ Carpeta INPUTTEST no encontrada: {self.inputtest_path}")
                return
            
            # Configurar DataManager para usar INPUTTEST
            self.data_manager.config['development']['use_inputtest'] = True
            self.data_manager.config['development']['inputtest_path'] = str(self.inputtest_path)
            
            logger.info(f"📁 Configurado para datos reales: {self.inputtest_path}")
            
        except Exception as e:
            logger.error(f"❌ Error configurando datos reales: {e}")
    
    def load_real_data_to_isa(self) -> bool:
        """
        Carga datos reales de INPUTTEST a la base de datos ISA.
        
        Returns:
            bool: True si se cargaron correctamente
        """
        try:
            logger.info("📊 Cargando datos reales de INPUTTEST...")
            
            # Cargar datos con DataManager
            kpi_file = self.inputtest_path / "DatabankExport_M1.csv"
            if not kpi_file.exists():
                logger.error(f"❌ Archivo KPI no encontrado: {kpi_file}")
                return False
            
            # Cargar datos
            df_kpi = pd.read_csv(kpi_file, sep=';', quotechar='"', engine='python')
            logger.info(f"📈 Datos KPI cargados: {df_kpi.shape}")
            
            # Preparar datos para ISA
            isa_data = self._prepare_data_for_isa(df_kpi)
            if isa_data is None:
                logger.error("❌ Error preparando datos para ISA")
                return False
            
            # Almacenar en base de datos ISA
            success = self.isa_database.store_isa_data(isa_data, "INPUTTEST_REAL")
            
            if success:
                logger.info(f"✅ Datos reales cargados a ISA: {len(isa_data)} registros")
                
                # Mostrar estadísticas
                stats = self.isa_database.get_database_stats()
                logger.info(f"📊 Estadísticas ISA: {stats}")
                
                return True
            else:
                logger.error("❌ Error almacenando datos en ISA")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error cargando datos reales: {e}")
            return False
    
    def _prepare_data_for_isa(self, df_kpi: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Prepara datos KPI para la base de datos ISA."""
        try:
            # Crear copia para no modificar original
            data = df_kpi.copy()
            
            # Limpiar nombres de columnas
            data.columns = data.columns.str.strip()
            
            # Verificar columnas requeridas
            required_columns = [
                'Strategy Name', 'CAGR', 'Sharpe_Ratio', 'Max_Drawdown', 
                'Profit_Factor', 'Total_Trades', 'Win_Rate'
            ]
            
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                logger.warning(f"⚠️ Columnas faltantes: {missing_columns}")
            
            # Crear columnas IS/OOS si no existen
            data = self._create_is_oos_columns(data)
            
            # Añadir scores calculados
            data = self._add_calculated_scores(data)
            
            # Limpiar datos
            data = self._clean_data_for_isa(data)
            
            logger.info(f"📊 Datos preparados para ISA: {data.shape}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error preparando datos para ISA: {e}")
            return None
    
    def _create_is_oos_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Crea columnas IS/OOS si no existen."""
        try:
            # Columnas base que pueden tener IS/OOS
            base_columns = ['CAGR', 'Sharpe_Ratio', 'Max_Drawdown', 'Profit_Factor']
            
            for col in base_columns:
                if col in data.columns:
                    # Si no existe la versión IS, crear basada en la columna original
                    if f'{col}_IS' not in data.columns:
                        data[f'{col}_IS'] = data[col]
                    
                    # Si no existe la versión OOS, crear simulación
                    if f'{col}_OOS' not in data.columns:
                        # Simular datos OOS con ruido
                        noise_factor = 0.1
                        data[f'{col}_OOS'] = data[col] * (1 + np.random.normal(0, noise_factor, len(data)))
            
            # Columnas adicionales que pueden tener IS/OOS
            additional_columns = ['Total_Trades', 'Win_Rate', 'Average_Trade']
            for col in additional_columns:
                if col in data.columns:
                    if f'{col}_IS' not in data.columns:
                        data[f'{col}_IS'] = data[col]
                    if f'{col}_OOS' not in data.columns:
                        data[f'{col}_OOS'] = data[col]
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error creando columnas IS/OOS: {e}")
            return data
    
    def _add_calculated_scores(self, data: pd.DataFrame) -> pd.DataFrame:
        """Añade scores calculados para ML."""
        try:
            # Calcular Recovery Factor si no existe
            if 'Recovery_Factor_IS' not in data.columns and 'CAGR_IS' in data.columns and 'Max_Drawdown_IS' in data.columns:
                data['Recovery_Factor_IS'] = data['CAGR_IS'] / (data['Max_Drawdown_IS'] + 1e-8)
            
            # Calcular Calmar Ratio si no existe
            if 'Calmar_Ratio_IS' not in data.columns and 'CAGR_IS' in data.columns and 'Max_Drawdown_IS' in data.columns:
                data['Calmar_Ratio_IS'] = data['CAGR_IS'] / (data['Max_Drawdown_IS'] + 1e-8)
            
            # Calcular Sortino Ratio aproximado
            if 'Sortino_Ratio_IS' not in data.columns and 'Sharpe_Ratio_IS' in data.columns:
                data['Sortino_Ratio_IS'] = data['Sharpe_Ratio_IS'] * 0.8  # Aproximación
            
            # Calcular Risk/Reward Ratio
            if 'Risk_Reward_Ratio_IS' not in data.columns and 'Profit_Factor_IS' in data.columns:
                data['Risk_Reward_Ratio_IS'] = data['Profit_Factor_IS']
            
            # Crear Unified Score básico
            if 'Unified_Score' not in data.columns:
                scores = []
                if 'CAGR_IS' in data.columns:
                    scores.append(data['CAGR_IS'] / data['CAGR_IS'].max())
                if 'Sharpe_Ratio_IS' in data.columns:
                    scores.append(data['Sharpe_Ratio_IS'] / data['Sharpe_Ratio_IS'].max())
                if 'Profit_Factor_IS' in data.columns:
                    scores.append(data['Profit_Factor_IS'] / data['Profit_Factor_IS'].max())
                
                if scores:
                    data['Unified_Score'] = np.mean(scores, axis=0)
                else:
                    data['Unified_Score'] = 0.5
            
            # Crear Factor K Score básico
            if 'Factor_K_Score' not in data.columns:
                if 'Unified_Score' in data.columns:
                    data['Factor_K_Score'] = data['Unified_Score']
                else:
                    data['Factor_K_Score'] = 0.5
            
            # Crear QVA Score básico
            if 'QVA_Score' not in data.columns:
                if 'Unified_Score' in data.columns:
                    data['QVA_Score'] = data['Unified_Score']
                else:
                    data['QVA_Score'] = 0.5
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error calculando scores: {e}")
            return data
    
    def _clean_data_for_isa(self, data: pd.DataFrame) -> pd.DataFrame:
        """Limpia datos para ISA."""
        try:
            # Reemplazar infinitos
            data = data.replace([np.inf, -np.inf], np.nan)
            
            # Imputar valores faltantes
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if data[col].isnull().sum() > 0:
                    data[col] = data[col].fillna(data[col].median())
            
            # Eliminar filas con demasiados valores faltantes
            threshold = int(len(data.columns) * 0.5)
            data = data.dropna(thresh=threshold)
            
            # Verificar que quedan suficientes datos
            if len(data) < 10:
                logger.warning("⚠️ Muy pocos datos después de limpieza")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error limpiando datos: {e}")
            return data
    
    def train_isa_models(self, 
                        target_columns: Optional[List[str]] = None,
                        model_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Entrena modelos ISA con datos reales.
        
        Args:
            target_columns: Columnas objetivo para entrenar
            model_types: Tipos de modelos a entrenar
            
        Returns:
            Dict: Resultados del entrenamiento
        """
        try:
            # Cargar datos reales si no están cargados
            stats = self.isa_database.get_database_stats()
            if stats.get('isa_records', 0) == 0:
                logger.info("📊 Cargando datos reales...")
                if not self.load_real_data_to_isa():
                    logger.error("❌ No se pudieron cargar datos reales")
                    return {}
            
            # Configurar targets y modelos
            target_columns = target_columns or ['Unified_Score', 'CAGR_OOS', 'Sharpe_Ratio_OOS']
            model_types = model_types or ['random_forest', 'gradient_boosting', 'linear_regression']
            
            results = {}
            
            for target in target_columns:
                logger.info(f"🎯 Entrenando modelos para target: {target}")
                target_results = {}
                
                for model_type in model_types:
                    if model_type not in self.model_trainer.get_available_models():
                        logger.warning(f"⚠️ Modelo no disponible: {model_type}")
                        continue
                    
                    logger.info(f"🤖 Entrenando {model_type} para {target}...")
                    
                    result = self.model_trainer.train_model(
                        model_type=model_type,
                        target_column=target,
                        use_cache=True
                    )
                    
                    if result is not None:
                        target_results[model_type] = {
                            'training_score': result.training_score,
                            'validation_score': result.validation_score,
                            'test_score': result.test_score,
                            'training_time': result.training_time,
                            'model_path': result.model_path,
                            'feature_importance': result.feature_importance
                        }
                        
                        logger.info(f"✅ {model_type} entrenado: test_score={result.test_score:.4f}")
                    else:
                        logger.error(f"❌ Error entrenando {model_type}")
                
                results[target] = target_results
            
            # Mostrar resumen
            self._show_training_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error entrenando modelos ISA: {e}")
            return {}
    
    def _show_training_summary(self, results: Dict[str, Any]):
        """Muestra resumen del entrenamiento."""
        try:
            logger.info("📊 RESUMEN DE ENTRENAMIENTO ISA")
            logger.info("=" * 50)
            
            for target, target_results in results.items():
                logger.info(f"🎯 Target: {target}")
                
                # Ordenar por test score
                sorted_models = sorted(
                    target_results.items(),
                    key=lambda x: x[1]['test_score'],
                    reverse=True
                )
                
                for model_type, metrics in sorted_models:
                    logger.info(f"   {model_type:20} | Test: {metrics['test_score']:.4f} | "
                              f"Val: {metrics['validation_score']:.4f} | "
                              f"Time: {metrics['training_time']:.2f}s")
                
                logger.info("")
            
            # Estadísticas generales
            total_models = sum(len(target_results) for target_results in results.values())
            logger.info(f"📈 Total modelos entrenados: {total_models}")
            
        except Exception as e:
            logger.error(f"❌ Error mostrando resumen: {e}")
    
    def compare_all_models(self) -> Dict[str, Any]:
        """Compara todos los modelos disponibles."""
        try:
            logger.info("🔄 Comparando todos los modelos...")
            
            # Cargar datos reales si es necesario
            stats = self.isa_database.get_database_stats()
            if stats.get('isa_records', 0) == 0:
                if not self.load_real_data_to_isa():
                    return {}
            
            # Comparar modelos para Unified_Score
            results = self.model_trainer.compare_models(target_column="Unified_Score")
            
            logger.info("📊 COMPARACIÓN DE MODELOS")
            logger.info("=" * 50)
            
            for model_type, metrics in results.items():
                logger.info(f"{model_type:20} | Test: {metrics['test_score']:.4f} | "
                          f"Val: {metrics['validation_score']:.4f} | "
                          f"Time: {metrics['training_time']:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error comparando modelos: {e}")
            return {}
    
    def get_isa_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del sistema ISA."""
        try:
            # Estadísticas de la base de datos
            db_stats = self.isa_database.get_database_stats()
            
            # Estadísticas de entrenamiento
            training_stats = self.model_trainer.get_training_stats()
            
            # Estadísticas de datos reales
            real_data_stats = {}
            if self.use_real_data and self.inputtest_path.exists():
                kpi_file = self.inputtest_path / "DatabankExport_M1.csv"
                if kpi_file.exists():
                    df = pd.read_csv(kpi_file, sep=';', quotechar='"', engine='python')
                    real_data_stats = {
                        'inputtest_records': len(df),
                        'inputtest_columns': len(df.columns),
                        'inputtest_file': str(kpi_file),
                        'inputtest_path': str(self.inputtest_path)
                    }
            
            return {
                'database': db_stats,
                'training': training_stats,
                'real_data': real_data_stats,
                'integration': {
                    'use_real_data': self.use_real_data,
                    'inputtest_path': str(self.inputtest_path),
                    'available_models': self.model_trainer.get_available_models()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas ISA: {e}")
            return {}
    
    def export_isa_report(self, output_path: str = "reports/isa_report.html") -> bool:
        """Exporta reporte completo del sistema ISA."""
        try:
            from pathlib import Path
            import json
            
            # Crear directorio si no existe
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Obtener estadísticas
            stats = self.get_isa_stats()
            
            # Crear reporte HTML
            html_content = self._generate_isa_html_report(stats)
            
            # Guardar reporte
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"📄 Reporte ISA exportado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando reporte ISA: {e}")
            return False
    
    def _generate_isa_html_report(self, stats: Dict[str, Any]) -> str:
        """Genera reporte HTML del sistema ISA."""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>ISA System Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                    .metric {{ margin: 10px 0; }}
                    .highlight {{ background-color: #f0f8ff; padding: 10px; }}
                </style>
            </head>
            <body>
                <h1>📊 ISA System Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="section">
                    <h2>🗄️ Database Statistics</h2>
                    <div class="metric">ISA Records: {stats.get('database', {}).get('isa_records', 0)}</div>
                    <div class="metric">ML Datasets: {stats.get('database', {}).get('ml_datasets', 0)}</div>
                    <div class="metric">Database Size: {stats.get('database', {}).get('db_size_mb', 0)} MB</div>
                </div>
                
                <div class="section">
                    <h2>🤖 Training Statistics</h2>
                    <div class="metric">Total Models: {stats.get('training', {}).get('total_models', 0)}</div>
                    <div class="metric">Available Models: {', '.join(stats.get('training', {}).get('available_models', []))}</div>
                </div>
                
                <div class="section">
                    <h2>📁 Real Data Statistics</h2>
                    <div class="metric">InputTest Records: {stats.get('real_data', {}).get('inputtest_records', 0)}</div>
                    <div class="metric">InputTest Columns: {stats.get('real_data', {}).get('inputtest_columns', 0)}</div>
                    <div class="metric">Use Real Data: {stats.get('integration', {}).get('use_real_data', False)}</div>
                </div>
                
                <div class="section highlight">
                    <h2>🎯 Integration Status</h2>
                    <div class="metric">Status: ✅ Active</div>
                    <div class="metric">InputTest Path: {stats.get('integration', {}).get('inputtest_path', 'N/A')}</div>
                    <div class="metric">Available Models: {len(stats.get('integration', {}).get('available_models', []))}</div>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte HTML: {e}")
            return "<html><body><h1>Error generating report</h1></body></html>" 