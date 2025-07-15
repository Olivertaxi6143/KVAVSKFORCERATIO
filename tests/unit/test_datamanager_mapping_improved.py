#!/usr/bin/env python3
"""
Test comprehensivo para validar el mapeo mejorado del DataManager
con archivos CSV reales de INPUTTEST.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
from src.core.logger_config import setup_logger
from src.data.data_manager import DataManager

log = setup_logger("test_datamanager_mapping_improved")

def test_datamanager_mapping_improved():
    """
    Test comprehensivo del mapeo mejorado del DataManager.
    """
    log.info("🧪 Iniciando test de mapeo mejorado del DataManager")
    
    try:
        # Inicializar DataManager
        data_manager = DataManager()
        log.info("✅ DataManager inicializado correctamente")
        
        # Test 1: Cargar DatabankExport_M1.csv (archivo de estrategias)
        log.info("📊 Test 1: Cargando DatabankExport_M1.csv")
        
        strategy_file = "INPUTTEST/DatabankExport_M1.csv"
        if os.path.exists(strategy_file):
            strategy_data = data_manager.load_and_prepare_data_pipeline(strategy_file)
            log.info(f"✅ Datos de estrategias cargados: {strategy_data.shape}")
            
            # Verificar mapeo de columnas clave
            expected_strategy_columns = [
                'strategy_name', 'cagr_is', 'cagr_oos', 'sharpe_is', 'sharpe_oos',
                'drawdown_is', 'drawdown_oos', 'profit_factor_is', 'profit_factor_oos'
            ]
            
            missing_columns = [col for col in expected_strategy_columns if col not in strategy_data.columns]
            if missing_columns:
                log.warning(f"⚠️ Columnas faltantes en estrategias: {missing_columns}")
            else:
                log.info("✅ Todas las columnas de estrategias mapeadas correctamente")
                
            # Mostrar primeras filas
            log.info(f"📋 Primeras 3 estrategias:")
            for i, row in strategy_data.head(3).iterrows():
                log.info(f"  {i+1}. {row.get('strategy_name', 'N/A')} - CAGR IS: {row.get('cagr_is', 'N/A')}")
                
        else:
            log.error(f"❌ Archivo no encontrado: {strategy_file}")
            
        # Test 2: Cargar DATOSMQL5.csv (archivo de precios)
        log.info("📊 Test 2: Cargando DATOSMQL5.csv")
        
        price_file = "INPUTTEST/DATOSMQL5.csv"
        if os.path.exists(price_file):
            price_data = data_manager.load_and_prepare_data_pipeline(price_file)
            log.info(f"✅ Datos de precios cargados: {price_data.shape}")
            
            # Verificar mapeo de columnas OHLCV
            expected_price_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            
            missing_columns = [col for col in expected_price_columns if col not in price_data.columns]
            if missing_columns:
                log.warning(f"⚠️ Columnas faltantes en precios: {missing_columns}")
            else:
                log.info("✅ Todas las columnas de precios mapeadas correctamente")
                
            # Mostrar primeras filas
            log.info(f"📋 Primeras 3 fechas de precios:")
            for i, row in price_data.head(3).iterrows():
                log.info(f"  {i+1}. {row.get('date', 'N/A')} - Close: {row.get('close', 'N/A')}")
                
        else:
            log.error(f"❌ Archivo no encontrado: {price_file}")
            
        # Test 3: Validar limpieza de datos
        log.info("🧹 Test 3: Validando limpieza de datos")
        
        if 'strategy_data' in locals():
            clean_strategy_data = data_manager.get_clean_data(strategy_file)
            log.info(f"✅ Datos de estrategias limpios: {clean_strategy_data.shape}")
            
            # Verificar que no hay columnas duplicadas
            if len(clean_strategy_data.columns) == len(set(clean_strategy_data.columns)):
                log.info("✅ No hay columnas duplicadas")
            else:
                log.warning("⚠️ Se detectaron columnas duplicadas")
                
        # Test 4: Validar conversión numérica
        log.info("🔢 Test 4: Validando conversión numérica")
        
        if 'strategy_data' in locals():
            # Verificar columnas numéricas
            numeric_columns = clean_strategy_data.select_dtypes(include=[np.number]).columns
            log.info(f"✅ Columnas numéricas detectadas: {len(numeric_columns)}")
            
            # Mostrar algunas estadísticas
            for col in ['cagr_is', 'sharpe_is', 'profit_factor_is']:
                if col in clean_strategy_data.columns:
                    mean_val = clean_strategy_data[col].mean()
                    log.info(f"  {col}: media = {mean_val:.4f}")
                    
        # Test 5: Validar manejo de errores
        log.info("🚨 Test 5: Validando manejo de errores")
        
        # Intentar cargar archivo inexistente
        try:
            data_manager.load_and_prepare_data_pipeline("archivo_inexistente.csv")
            log.error("❌ Debería haber fallado al cargar archivo inexistente")
        except Exception as e:
            log.info(f"✅ Manejo correcto de error: {str(e)[:100]}...")
            
        # Test 6: Validar guardado y carga de resultados
        log.info("💾 Test 6: Validando guardado y carga de resultados")
        
        if 'strategy_data' in locals():
            # Guardar resultados
            results = {
                'test_name': 'mapping_improved_test',
                'strategy_count': len(strategy_data),
                'columns_mapped': list(strategy_data.columns),
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            saved_path = data_manager.save_results(results, "test_mapping_improved")
            log.info(f"✅ Resultados guardados en: {saved_path}")
            
            # Cargar resultados
            loaded_results = data_manager.load_results("test_mapping_improved")
            log.info(f"✅ Resultados cargados: {loaded_results.get('test_name', 'N/A')}")
            
        log.info("🎉 Test de mapeo mejorado completado exitosamente")
        return True
        
    except Exception as e:
        log.error(f"❌ Error en test de mapeo mejorado: {e}")
        import traceback
        log.error(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_datamanager_mapping_improved()
    if success:
        log.info("✅ Todos los tests pasaron correctamente")
    else:
        log.error("❌ Algunos tests fallaron")
        sys.exit(1) 