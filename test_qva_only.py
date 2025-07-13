#!/usr/bin/env python3
"""
Test específico para el QVA Score y configuración dinámica.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import pandas as pd
from src.data_manager import DataManager
from src.core.integration_layer import QVAScorerEnhanced, ConfigManagerEnhanced

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_qva_score():
    """Test específico del QVA Score."""
    try:
        print("=== TEST QVA SCORE ===")
        
        # 1. Cargar datos
        print("1. Cargando datos...")
        dm = DataManager()
        success = dm.load_kpis_data('DatabankExport_M1.csv')
        if not success or dm.kpis_data is None:
            print("❌ Error cargando datos")
            return False
            
        df = dm.kpis_data
        print(f"   Datos cargados: {len(df)} filas")
        
        # 2. Verificar configuración
        print("2. Verificando configuración...")
        config_manager = ConfigManagerEnhanced()
        enabled_kpis = config_manager.get_enabled_kpis()
        print(f"   KPIs habilitados: {enabled_kpis}")
        
        # 3. Test QVA Score
        print("3. Probando QVA Score...")
        qva_scorer = QVAScorerEnhanced(config_manager)
        
        # Test cálculo básico
        print("   - Calculando QVA Score básico...")
        qva_scores = qva_scorer.calculate_qva_score(df)
        print(f"   - QVA Score calculado: {type(qva_scores)}, shape: {qva_scores.shape}")
        
        # Test cálculo robusto
        print("   - Calculando QVA Score robusto...")
        qva_robust = qva_scorer.compute_qva_score_robust(df)
        print(f"   - QVA Score robusto calculado: {type(qva_robust)}, shape: {qva_robust.shape}")
        
        print("✅ TEST QVA EXITOSO")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qva_score()
    sys.exit(0 if success else 1) 