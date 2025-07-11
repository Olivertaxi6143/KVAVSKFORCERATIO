#!/usr/bin/env python3
"""
Test específico para verificar que las métricas científicas aparecen correctamente en la GUI.
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core_engine_enhanced import FactorKElite96Enhanced
from src.data_manager import DataManager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_metricas_cientificas():
    """Test para verificar que las métricas científicas se calculan y muestran correctamente."""
    
    logger.info("🧪 Iniciando test de métricas científicas...")
    
    try:
        # 1. Cargar datos de prueba
        logger.info("📊 Cargando datos de prueba...")
        data_manager = DataManager()
        data_manager.switch_to_development_mode()
        
        # Usar datos de INPUTTEST
        kpis_file = "INPUTTEST/DatabankExport_M1.csv"
        if not os.path.exists(kpis_file):
            logger.error(f"❌ Archivo de KPIs no encontrado: {kpis_file}")
            return False
        
        # Cargar datos
        df = data_manager.load_kpis_data(kpis_file)
        if df is None:
            logger.error("❌ No se pudieron cargar los datos de KPIs")
            return False
        
        # Verificar que es un DataFrame
        if not isinstance(df, pd.DataFrame):
            logger.error(f"❌ Tipo de datos inesperado: {type(df)}")
            return False
        
        if df.empty:
            logger.error("❌ DataFrame vacío")
            return False
        
        logger.info(f"✅ Datos cargados: {len(df)} estrategias")
        
        # 2. Crear instancia del core engine
        logger.info("🔧 Inicializando core engine...")
        core_engine = FactorKElite96Enhanced()
        
        # 3. Ejecutar análisis
        logger.info("🚀 Ejecutando análisis con métricas científicas...")
        results = core_engine.evaluate_strategies(df)
        
        if results is None or results.empty:
            logger.error("❌ No se obtuvieron resultados del análisis")
            return False
        
        logger.info(f"✅ Análisis completado: {len(results)} estrategias procesadas")
        
        # 4. Verificar que las métricas científicas están presentes
        logger.info("🔍 Verificando métricas científicas...")
        
        required_columns = [
            'Unified_Score_Scientific',
            'Unified_Score_Enhanced'
        ]
        
        missing_columns = []
        for col in required_columns:
            if col not in results.columns:
                missing_columns.append(col)
        
        if missing_columns:
            logger.error(f"❌ Columnas científicas faltantes: {missing_columns}")
            logger.info(f"📊 Columnas disponibles: {list(results.columns)}")
            return False
        
        logger.info("✅ Todas las métricas científicas están presentes")
        
        # 5. Verificar que las métricas tienen valores válidos
        logger.info("🔍 Verificando valores de métricas científicas...")
        
        for col in required_columns:
            if col in results.columns:
                # Verificar que no son NaN
                nan_count = results[col].isna().sum()
                if nan_count > 0:
                    logger.warning(f"⚠️ {col}: {nan_count} valores NaN encontrados")
                
                # Verificar que no son infinitos
                inf_count = np.isinf(results[col]).sum()
                if inf_count > 0:
                    logger.warning(f"⚠️ {col}: {inf_count} valores infinitos encontrados")
                
                # Mostrar estadísticas
                stats = results[col].describe()
                logger.info(f"📊 {col} - Media: {stats['mean']:.4f}, Std: {stats['std']:.4f}")
        
        # 6. Verificar que las métricas son diferentes del Unified_Score original
        if 'Unified_Score' in results.columns:
            scientific_scores = results['Unified_Score_Scientific']
            original_scores = results['Unified_Score']
            
            # Verificar que no son idénticos
            if np.allclose(scientific_scores, original_scores, rtol=1e-10):
                logger.warning("⚠️ Unified_Score_Scientific es idéntico a Unified_Score")
            else:
                logger.info("✅ Unified_Score_Scientific es diferente del Unified_Score original")
        
        # 7. Mostrar resumen de resultados
        logger.info("📊 Resumen de métricas científicas:")
        for col in required_columns:
            if col in results.columns:
                stats = results[col].describe()
                logger.info(f"   {col}:")
                logger.info(f"     - Media: {stats['mean']:.4f}")
                logger.info(f"     - Mediana: {stats['50%']:.4f}")
                logger.info(f"     - Min: {stats['min']:.4f}")
                logger.info(f"     - Max: {stats['max']:.4f}")
                logger.info(f"     - Std: {stats['std']:.4f}")
        
        # 8. Verificar que las métricas están en el rango esperado
        logger.info("🔍 Verificando rangos de métricas...")
        
        for col in required_columns:
            if col in results.columns:
                min_val = results[col].min()
                max_val = results[col].max()
                
                if min_val < 0 or max_val > 10:
                    logger.warning(f"⚠️ {col}: Rango inesperado [{min_val:.4f}, {max_val:.4f}]")
                else:
                    logger.info(f"✅ {col}: Rango válido [{min_val:.4f}, {max_val:.4f}]")
        
        logger.info("🎉 Test de métricas científicas completado exitosamente!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de métricas científicas: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Función principal del test."""
    logger.info("🚀 Iniciando test completo de métricas científicas...")
    
    success = test_metricas_cientificas()
    
    if success:
        logger.info("✅ Test completado exitosamente")
        return 0
    else:
        logger.error("❌ Test falló")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 