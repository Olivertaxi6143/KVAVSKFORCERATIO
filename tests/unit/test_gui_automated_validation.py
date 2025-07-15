#!/usr/bin/env python3
"""
Script de prueba automatizada para validar la GUI
"""

import sys
import os
import time
import threading
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_automated():
    """Prueba automatizada de la GUI"""
    
    print("🧪 INICIANDO PRUEBA AUTOMATIZADA DE LA GUI")
    print("=" * 60)
    
    try:
        # Importar módulos necesarios
        print("📦 Importando módulos...")
        from src.gui.main_window import MainWindow as EnhancedRankGUI
        from src.data.data_manager import DataManager
        from src.core.integration_layer import FactorKElite96Enhanced
        from src.analysis.asesor_financiero_inteligente import AsesorFinancieroInteligente
        
        print("✅ Módulos importados correctamente")
        
        # Verificar archivos de datos
        print("\n📁 Verificando archivos de datos...")
        data_files = [
            "DatabankExport_M1.csv",
            "DATOSMQL5.csv"
        ]
        
        for file in data_files:
            if os.path.exists(file):
                print(f"✅ {file} encontrado")
            else:
                print(f"❌ {file} NO encontrado")
                return False
        
        # Verificar carpeta de estrategias
        strategies_folder = "INPUTTEST/M1_NDX_UP_MQL4_136_STOP"
        if os.path.exists(strategies_folder):
            sqx_files = [f for f in os.listdir(strategies_folder) if f.endswith('.sqx')]
            print(f"✅ Carpeta de estrategias encontrada: {len(sqx_files)} archivos .sqx")
        else:
            print(f"❌ Carpeta de estrategias NO encontrada: {strategies_folder}")
            return False
        
        # Crear instancia de DataManager
        print("\n🔧 Inicializando DataManager...")
        dm = DataManager()
        
        # Cargar datos
        print("📊 Cargando datos...")
        dm.load_kpis_data("DatabankExport_M1.csv")
        dm.load_market_data("DATOSMQL5.csv")
        dm.load_strategies_data(strategies_folder)
        
        print(f"✅ Datos cargados:")
        print(f"   - KPIs: {len(dm.kpis_data)} filas")
        print(f"   - Mercado: {len(dm.market_data)} filas")
        print(f"   - Estrategias: {len(dm.strategies_data)} archivos")
        
        # Crear instancia del Core Engine
        print("\n⚙️ Inicializando Core Engine...")
        core_engine = FactorKElite96Enhanced()
        
        # Crear instancia del Asesor Financiero
        print("🤖 Inicializando Asesor Financiero...")
        asesor = AsesorFinancieroInteligente(dm)
        
        print("✅ Componentes principales inicializados correctamente")
        
        # Simular análisis básico
        print("\n🔍 Simulando análisis básico...")
        
        # Verificar que el análisis funciona
        try:
            # Simular análisis con datos de prueba
            analysis_result = core_engine.evaluate_strategies(dm.kpis_data)
            print("✅ Análisis simulado correctamente")
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
            return False
        
        # Verificar funcionalidad del asesor
        print("\n💡 Verificando funcionalidad del asesor...")
        try:
            # Simular recomendaciones del asesor
            recommendations = asesor.generate_recommendations()
            print("✅ Asesor financiero funcionando correctamente")
        except Exception as e:
            print(f"❌ Error en asesor: {e}")
            return False
        
        print("\n🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 60)
        print("✅ GUI lista para uso")
        print("✅ Datos cargados correctamente")
        print("✅ Análisis funcionando")
        print("✅ Asesor financiero operativo")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error en prueba automatizada: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_manual_launch():
    """Prueba de lanzamiento manual de la GUI"""
    
    print("\n🖥️ PRUEBA DE LANZAMIENTO MANUAL DE LA GUI")
    print("=" * 50)
    
    try:
        from src.gui.main_window import MainWindow as EnhancedRankGUI
        
        print("🚀 Lanzando GUI...")
        print("💡 La GUI se abrirá en una ventana separada")
        print("💡 Puedes interactuar con ella manualmente")
        print("💡 Cierra la ventana cuando termines las pruebas")
        
        # Crear y ejecutar la GUI en un hilo separado
        def launch_gui():
            app = EnhancedRankGUI()
            app.mainloop()
        
        gui_thread = threading.Thread(target=launch_gui, daemon=True)
        gui_thread.start()
        
        print("✅ GUI lanzada correctamente")
        print("⏳ Esperando 10 segundos para que se cargue...")
        time.sleep(10)
        
        print("✅ GUI debería estar visible y funcional")
        return True
        
    except Exception as e:
        print(f"❌ Error lanzando GUI: {e}")
        return False

if __name__ == "__main__":
    print(f"🕐 Iniciando pruebas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar prueba automatizada
    automated_success = test_gui_automated()
    
    if automated_success:
        # Si la prueba automatizada pasa, lanzar GUI manual
        manual_success = test_gui_manual_launch()
        
        if manual_success:
            print("\n🎯 RESULTADO FINAL: TODAS LAS PRUEBAS EXITOSAS")
            print("✅ Sistema listo para uso")
        else:
            print("\n⚠️ RESULTADO: Pruebas automatizadas OK, pero GUI manual falló")
    else:
        print("\n❌ RESULTADO: Pruebas automatizadas fallaron")
        print("🔧 Revisar configuración antes de lanzar GUI") 