#!/usr/bin/env python3
"""
Test de diagnóstico del DataManager
"""
import sys
import os
import traceback

print("=== DIAGNÓSTICO DATAMANAGER ===")

# Añadir src/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
print("✅ Path añadido")

try:
    from data.data_manager import DataManager
    print("✅ DataManager importado")
except Exception as e:
    print(f"❌ Error importando DataManager: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    dm = DataManager()
    print("✅ DataManager creado")
except Exception as e:
    print(f"❌ Error creando DataManager: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("Cargando datos...")
    df = dm.load_and_prepare_data_pipeline("INPUTTEST/DatabankExport_M1.csv")
    print(f"✅ Datos cargados: {df.shape}")
    print(f"Columnas: {list(df.columns)[:10]}...")
except Exception as e:
    print(f"❌ Error cargando datos: {e}")
    traceback.print_exc()
    sys.exit(1)

print("✅ DIAGNÓSTICO COMPLETADO") 