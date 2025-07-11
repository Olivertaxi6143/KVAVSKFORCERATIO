#!/usr/bin/env python3
"""
Test CLI para verificar KPIs por estilo de trading
Verifica la selección automática de KPIs y el análisis del asesor financiero
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_kpis_por_estilo():
    """Test CLI para verificar KPIs por estilo de trading."""
    
    print("🧪 TEST CLI - KPIs POR ESTILO DE TRADING")
    print("=" * 60)
    
    try:
        # Importar módulos necesarios
        print("📦 Importando módulos...")
        from gui_enhanced_rank import EnhancedRankGUI
        from asesor_financiero_inteligente import AsesorFinancieroInteligente
        
        # Crear instancia de GUI para acceder a la lógica de KPIs
        print("🔧 Inicializando GUI para acceder a la lógica de KPIs...")
        gui = EnhancedRankGUI()
        
        # Estilos de trading disponibles
        estilos_trading = ["Intradía", "Swing", "Tendencial", "Reversión a la media", "Breakout"]
        
        # Resultados del test
        resultados_test = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estilos_probadps": [],
            "resumen_general": {}
        }
        
        print(f"\n📊 Probando {len(estilos_trading)} estilos de trading...")
        
        for estilo in estilos_trading:
            print(f"\n🎯 Probando estilo: {estilo}")
            print("-" * 40)
            
            # Cambiar estilo de trading
            gui.var_style.set(estilo)
            gui._restore_kpis()
            
            # Obtener KPIs seleccionados (extra)
            kpis_extra = [key for key, var in gui.metric_vars.items() if var.get()]
            
            # Detectar automáticamente todos los KPIs numéricos del archivo real
            try:
                from src.data_manager import DataManager
                dm = DataManager()
                dm.load_kpis_data("DatabankExport_M1.csv")
                
                # Obtener todos los KPIs numéricos del archivo real
                kpis_numericos_reales = []
                if dm.kpis_data is not None:
                    for col in dm.kpis_data.columns:
                        if pd.api.types.is_numeric_dtype(dm.kpis_data[col]):
                            # Excluir columnas de identificación
                            if col not in ['Strategy_Name', 'TimeFrame', 'Filters_result', 'Strategy Name']:
                                kpis_numericos_reales.append(col)
                
                kpis_base = kpis_numericos_reales
                print(f"🔍 Detectados {len(kpis_base)} KPIs numéricos del archivo real")
                
            except Exception as e:
                print(f"⚠️ Error cargando archivo real, usando KPIs base predefinidos: {e}")
                # Fallback a KPIs base predefinidos
                kpis_base = [
                    'Profit_factor', 'Net_profit', 'CAGR', 'RecoveryFactor',  # Rentabilidad
                    'Max_DD_%', 'VaR_95%', 'CVaR_95%', 'Ulcer_Index_%',      # Riesgo
                    'Sharpe_Ratio', 'Sortino_Ratio', 'CalmarRatio', 'Winning_Percent'  # Consistencia
                ]
            
            # Total de KPIs utilizados = KPIs base + KPIs extra
            kpis_totales = kpis_base + kpis_extra
            
            print(f"📊 KPIs base (por defecto): {len(kpis_base)}")
            print(f"📋 KPIs base: {', '.join(kpis_base)}")
            print(f"📊 KPIs extra (estilo {estilo}): {len(kpis_extra)}")
            print(f"📋 KPIs extra: {', '.join(kpis_extra)}")
            print(f"📊 TOTAL KPIs utilizados: {len(kpis_totales)}")
            print(f"📋 Lista completa: {', '.join(kpis_totales)}")
            
            # Crear datos de prueba para el asesor
            print("🔬 Creando datos de prueba para el asesor...")
            datos_prueba = crear_datos_prueba_asesor(kpis_totales)
            
            # Simular análisis del asesor
            print("🤖 Simulando análisis del asesor financiero...")
            try:
                asesor = AsesorFinancieroInteligente(datos_prueba, kpis_totales)
                consejos = asesor.generar_consejos_completos()
                
                # Extraer información relevante
                num_estrategias_analizadas = len(datos_prueba)
                num_kpis_usados = len(kpis_totales)
                
                print(f"✅ Análisis exitoso: {num_estrategias_analizadas} estrategias, {num_kpis_usados} KPIs")
                
                # Guardar resultados del estilo
                resultado_estilo = {
                    "estilo": estilo,
                    "kpis_base": kpis_base,
                    "kpis_extra": kpis_extra,
                    "kpis_totales": kpis_totales,
                    "num_kpis_base": len(kpis_base),
                    "num_kpis_extra": len(kpis_extra),
                    "num_kpis_total": num_kpis_usados,
                    "num_estrategias_analizadas": num_estrategias_analizadas,
                    "analisis_exitoso": True,
                    "consejos_generados": len(consejos) if isinstance(consejos, list) else 1
                }
                
            except Exception as e:
                print(f"❌ Error en análisis: {str(e)}")
                resultado_estilo = {
                    "estilo": estilo,
                    "kpis_base": kpis_base,
                    "kpis_extra": kpis_extra,
                    "kpis_totales": kpis_totales,
                    "num_kpis_base": len(kpis_base),
                    "num_kpis_extra": len(kpis_extra),
                    "num_kpis_total": len(kpis_totales),
                    "num_estrategias_analizadas": 0,
                    "analisis_exitoso": False,
                    "error": str(e)
                }
            
            resultados_test["estilos_probadps"].append(resultado_estilo)
            
            # Mostrar resumen del estilo
            print(f"📊 Resumen {estilo}:")
            print(f"   • KPIs base: {resultado_estilo['num_kpis_base']}")
            print(f"   • KPIs extra: {resultado_estilo['num_kpis_extra']}")
            print(f"   • TOTAL KPIs: {resultado_estilo['num_kpis_total']}")
            print(f"   • Estrategias analizadas: {resultado_estilo['num_estrategias_analizadas']}")
            print(f"   • Análisis exitoso: {'✅' if resultado_estilo['analisis_exitoso'] else '❌'}")
        
        # Generar resumen general
        print(f"\n📈 RESUMEN GENERAL DEL TEST")
        print("=" * 60)
        
        total_estilos = len(resultados_test["estilos_probadps"])
        estilos_exitosos = sum(1 for r in resultados_test["estilos_probadps"] if r["analisis_exitoso"])
        total_kpis_base = sum(r["num_kpis_base"] for r in resultados_test["estilos_probadps"])
        total_kpis_extra = sum(r["num_kpis_extra"] for r in resultados_test["estilos_probadps"])
        total_kpis_totales = sum(r["num_kpis_total"] for r in resultados_test["estilos_probadps"])
        promedio_kpis_totales = total_kpis_totales / total_estilos if total_estilos > 0 else 0
        
        resultados_test["resumen_general"] = {
            "total_estilos": total_estilos,
            "estilos_exitosos": estilos_exitosos,
            "estilos_fallidos": total_estilos - estilos_exitosos,
            "total_kpis_base": total_kpis_base,
            "total_kpis_extra": total_kpis_extra,
            "total_kpis_totales": total_kpis_totales,
            "promedio_kpis_totales_por_estilo": promedio_kpis_totales,
            "tasa_exito": (estilos_exitosos / total_estilos) * 100 if total_estilos > 0 else 0
        }
        
        print(f"🎯 Estilos probados: {total_estilos}")
        print(f"✅ Análisis exitosos: {estilos_exitosos}")
        print(f"❌ Análisis fallidos: {total_estilos - estilos_exitosos}")
        print(f"📊 Total KPIs base: {total_kpis_base}")
        print(f"📊 Total KPIs extra: {total_kpis_extra}")
        print(f"📊 Total KPIs usados: {total_kpis_totales}")
        print(f"📈 Promedio KPIs totales por estilo: {promedio_kpis_totales:.1f}")
        print(f"🎯 Tasa de éxito: {resultados_test['resumen_general']['tasa_exito']:.1f}%")
        
        # Mostrar detalles por estilo
        print(f"\n📋 DETALLES POR ESTILO:")
        print("-" * 60)
        for resultado in resultados_test["estilos_probadps"]:
            status = "✅" if resultado["analisis_exitoso"] else "❌"
            print(f"{status} {resultado['estilo']}: {resultado['num_kpis_base']} base + {resultado['num_kpis_extra']} extra = {resultado['num_kpis_total']} total, {resultado['num_estrategias_analizadas']} estrategias")
        
        # Guardar resultados en archivo JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_resultados = f"test_kpis_por_estilo_{timestamp}.json"
        
        with open(archivo_resultados, 'w', encoding='utf-8') as f:
            json.dump(resultados_test, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {archivo_resultados}")
        
        # Crear reporte ejecutivo
        crear_reporte_ejecutivo(resultados_test, archivo_resultados)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test CLI: {str(e)}")
        return False

def crear_datos_prueba_asesor(kpis_seleccionados):
    """Crea datos de prueba para el asesor financiero."""
    # Crear DataFrame con estrategias de prueba
    num_estrategias = 50  # Número razonable para pruebas
    
    datos = {}
    
    # Agregar columnas básicas
    datos['Strategy_Name'] = [f"Strategy_{i:03d}" for i in range(num_estrategias)]
    datos['Quality_Category'] = np.random.choice(['Excelente', 'Muy Bueno', 'Bueno', 'Regular', 'Pobre'], num_estrategias)
    datos['Unified_Score'] = np.random.uniform(0.1, 0.9, num_estrategias)
    
    # Agregar KPIs seleccionados con datos realistas
    for kpi in kpis_seleccionados:
        if 'CAGR' in kpi:
            datos[kpi] = np.random.uniform(5, 50, num_estrategias)
        elif 'Profit' in kpi or 'factor' in kpi.lower():
            datos[kpi] = np.random.uniform(0.8, 3.0, num_estrategias)
        elif 'Sharpe' in kpi:
            datos[kpi] = np.random.uniform(0.5, 2.5, num_estrategias)
        elif 'Drawdown' in kpi:
            datos[kpi] = np.random.uniform(5, 30, num_estrategias)
        elif 'Winning' in kpi or 'Percent' in kpi:
            datos[kpi] = np.random.uniform(30, 80, num_estrategias)
        elif 'SQN' in kpi:
            datos[kpi] = np.random.uniform(0.5, 3.0, num_estrategias)
        elif 'Exposure' in kpi:
            datos[kpi] = np.random.uniform(20, 80, num_estrategias)
        elif 'Duration' in kpi:
            datos[kpi] = np.random.uniform(1, 12, num_estrategias)
        elif 'Ratio' in kpi:
            datos[kpi] = np.random.uniform(0.5, 2.5, num_estrategias)
        else:
            # Valor por defecto para KPIs no específicos
            datos[kpi] = np.random.uniform(0, 100, num_estrategias)
    
    return pd.DataFrame(datos)

def crear_reporte_ejecutivo(resultados_test, archivo_json):
    """Crea un reporte ejecutivo en formato texto."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_reporte = f"reporte_ejecutivo_kpis_{timestamp}.txt"
    
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write("REPORTE EJECUTIVO - TEST KPIs POR ESTILO DE TRADING\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Fecha: {resultados_test['fecha']}\n")
        f.write(f"Archivo de datos: {archivo_json}\n\n")
        
        # Resumen general
        resumen = resultados_test['resumen_general']
        f.write("RESUMEN GENERAL:\n")
        f.write("-" * 20 + "\n")
        f.write(f"• Estilos probados: {resumen['total_estilos']}\n")
        f.write(f"• Análisis exitosos: {resumen['estilos_exitosos']}\n")
        f.write(f"• Análisis fallidos: {resumen['estilos_fallidos']}\n")
        f.write(f"• Tasa de éxito: {resumen['tasa_exito']:.1f}%\n")
        f.write(f"• Total KPIs usados: {resumen['total_kpis_usados']}\n")
        f.write(f"• Promedio KPIs por estilo: {resumen['promedio_kpis_por_estilo']:.1f}\n\n")
        
        # Detalles por estilo
        f.write("DETALLES POR ESTILO:\n")
        f.write("-" * 20 + "\n")
        for resultado in resultados_test['estilos_probadps']:
            status = "✅" if resultado['analisis_exitoso'] else "❌"
            f.write(f"{status} {resultado['estilo']}:\n")
            f.write(f"   • KPIs seleccionados: {resultado['num_kpis']}\n")
            f.write(f"   • Estrategias analizadas: {resultado['num_estrategias_analizadas']}\n")
            f.write(f"   • KPIs: {', '.join(resultado['kpis_seleccionados'])}\n")
            if not resultado['analisis_exitoso']:
                f.write(f"   • Error: {resultado.get('error', 'Desconocido')}\n")
            f.write("\n")
        
        # Recomendaciones
        f.write("RECOMENDACIONES:\n")
        f.write("-" * 20 + "\n")
        if resumen['tasa_exito'] == 100:
            f.write("✅ Todos los estilos funcionan correctamente\n")
        else:
            f.write("⚠️ Algunos estilos necesitan revisión\n")
        
        if resumen['promedio_kpis_por_estilo'] < 5:
            f.write("⚠️ Pocos KPIs por estilo - considerar aumentar la selección\n")
        elif resumen['promedio_kpis_por_estilo'] > 15:
            f.write("⚠️ Muchos KPIs por estilo - considerar optimizar la selección\n")
        else:
            f.write("✅ Número de KPIs por estilo es óptimo\n")
    
    print(f"📄 Reporte ejecutivo guardado en: {archivo_reporte}")

if __name__ == "__main__":
    print("🚀 Iniciando test CLI de KPIs por estilo de trading...")
    exito = test_kpis_por_estilo()
    
    if exito:
        print("\n✅ Test CLI completado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Test CLI falló")
        sys.exit(1) 