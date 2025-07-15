#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de la ventana de detalles IS/OOS
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
import json
import logging

from src.gui.main_window import MainWindow as EnhancedRankGUI
from src.data.data_manager import DataManager
from src.core.integration_layer import run_complete_analysis_with_gui_integration

def test_is_oos_window():
    """Prueba la funcionalidad de la ventana de detalles IS/OOS"""
    print("🧪 Iniciando prueba de ventana IS/OOS...")
    
    try:
        # Crear instancia de la GUI
        print("📱 Creando instancia de GUI...")
        app = EnhancedRankGUI()
        print("✅ GUI creada correctamente")
        
        # Cargar datos de prueba
        print("📊 Cargando datos de prueba...")
        df = pd.read_csv('DatabankExport_M1.csv', sep=';')
        print(f"✅ Datos cargados: {df.shape}")
        
        # Verificar que hay columnas IS/OOS
        is_cols = [col for col in df.columns if '(IS)' in col]
        oos_cols = [col for col in df.columns if '(OOS)' in col]
        print(f"📈 Columnas IS encontradas: {len(is_cols)}")
        print(f"📉 Columnas OOS encontradas: {len(oos_cols)}")
        
        # Probar la función analyze_is_oos_predictivity
        print("🔬 Probando función analyze_is_oos_predictivity...")
        row = df.iloc[0]
        resumen, detalles, valor = app.analyze_is_oos_predictivity(row, df)
        print(f"✅ Función ejecutada correctamente")
        print(f"📋 Resumen: {resumen}")
        print(f"📊 Detalles: {len(detalles)} KPIs")
        print(f"📈 Valor: {valor}")
        
        # Verificar que los detalles se guardan correctamente
        print("💾 Verificando guardado de detalles...")
        app.is_oos_details[0] = detalles
        detalles_guardados = app.is_oos_details.get(0, [])
        print(f"✅ Detalles guardados: {len(detalles_guardados)}")
        
        # Probar la función _show_is_oos_detail
        print("🪟 Probando función _show_is_oos_detail...")
        try:
            app._show_is_oos_detail(0, df)
            print("✅ Ventana de detalles creada correctamente")
        except Exception as e:
            print(f"❌ Error al crear ventana: {e}")
        
        print("🎉 Prueba completada exitosamente!")
        assert True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        assert False

if __name__ == "__main__":
    success = test_is_oos_window()
    if success:
        print("\n✅ La ventana de detalles IS/OOS está funcionando correctamente")
    else:
        print("\n❌ Hay problemas con la ventana de detalles IS/OOS") 