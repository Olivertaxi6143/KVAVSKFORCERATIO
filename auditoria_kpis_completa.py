#!/usr/bin/env python3
"""
AUDITORIA_KPIS_COMPLETA.py - Auditoría y fiscalización completa de KPIs
"""

import sys
import os
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath('src'))

try:
    from src.core.integration_layer import run_complete_analysis_with_gui_integration
    from data_manager import DataManager
    from asesor_financiero_inteligente import AsesorFinancieroInteligente
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

class AuditoriaKPIs:
    """Auditoría completa de KPIs en todo el sistema."""
    
    def __init__(self):
        self.reportes = {}
        self.fecha_auditoria = datetime.now().isoformat()
        
    def auditar_csv_original(self):
        """Auditoría del CSV original."""
        print("🔍 PASO 1: Auditoría del CSV original")
        print("=" * 50)
        
        try:
            # Leer CSV original
            df_original = pd.read_csv('DatabankExport_M1.csv', sep=';', decimal=',')
            
            # Analizar columnas
            columnas_totales = len(df_original.columns)
            columnas_numericas = len(df_original.select_dtypes(include=[np.number]).columns)
            columnas_texto = len(df_original.select_dtypes(include=['object']).columns)
            
            # KPIs numéricos
            kpis_numericos = [
                col for col in df_original.columns
                if pd.api.types.is_numeric_dtype(df_original[col])
            ]
            
            # Categorizar KPIs
            kpis_categorizados = self._categorizar_kpis(kpis_numericos)
            
            # Verificar valores faltantes
            valores_faltantes = df_original[kpis_numericos].isnull().sum()
            kpis_con_faltantes = valores_faltantes[valores_faltantes > 0].to_dict()
            
            reporte = {
                'total_estrategias': len(df_original),
                'total_columnas': columnas_totales,
                'columnas_numericas': columnas_numericas,
                'columnas_texto': columnas_texto,
                'kpis_numericos': kpis_numericos,
                'kpis_categorizados': kpis_categorizados,
                'valores_faltantes': kpis_con_faltantes,
                'estadisticas_basicas': {
                    'min_values': df_original[kpis_numericos].min().to_dict(),
                    'max_values': df_original[kpis_numericos].max().to_dict(),
                    'mean_values': df_original[kpis_numericos].mean().to_dict()
                }
            }
            
            print(f"✅ CSV original auditado:")
            print(f"  • Estrategias: {len(df_original)}")
            print(f"  • Columnas totales: {columnas_totales}")
            print(f"  • KPIs numéricos: {columnas_numericas}")
            print(f"  • KPIs con valores faltantes: {len(kpis_con_faltantes)}")
            
            self.reportes['csv_original'] = reporte
            return df_original, kpis_numericos
            
        except Exception as e:
            print(f"❌ Error en auditoría CSV original: {e}")
            return None, []
    
    def auditar_datamanager(self, df_original):
        """Auditoría del DataManager."""
        print("\n🔍 PASO 2: Auditoría del DataManager")
        print("=" * 50)
        
        try:
            dm = DataManager()
            dm.load_all_data()
            
            if dm.kpis_data is None:
                print("❌ Error: DataManager no pudo cargar datos")
                return None, []
            
            # Comparar con original
            kpis_dm = [
                col for col in dm.kpis_data.columns
                if pd.api.types.is_numeric_dtype(dm.kpis_data[col])
            ]
            
            # KPIs perdidos en DataManager
            kpis_perdidos = [kpi for kpi in df_original.columns if kpi not in dm.kpis_data.columns]
            kpis_nuevos = [kpi for kpi in dm.kpis_data.columns if kpi not in df_original.columns]
            
            # Verificar normalización
            normalizacion_correcta = self._verificar_normalizacion(df_original.columns, dm.kpis_data.columns)
            
            reporte = {
                'total_estrategias': len(dm.kpis_data),
                'total_columnas': len(dm.kpis_data.columns),
                'kpis_numericos': kpis_dm,
                'kpis_perdidos': kpis_perdidos,
                'kpis_nuevos': kpis_nuevos,
                'normalizacion_correcta': normalizacion_correcta,
                'estadisticas_limpieza': {
                    'valores_infinitos': (dm.kpis_data == np.inf).sum().sum(),
                    'valores_nan': dm.kpis_data.isnull().sum().sum(),
                    'duplicados': dm.kpis_data.duplicated().sum()
                }
            }
            
            print(f"✅ DataManager auditado:")
            print(f"  • Estrategias: {len(dm.kpis_data)}")
            print(f"  • KPIs numéricos: {len(kpis_dm)}")
            print(f"  • KPIs perdidos: {len(kpis_perdidos)}")
            print(f"  • KPIs nuevos: {len(kpis_nuevos)}")
            print(f"  • Normalización: {'✅' if normalizacion_correcta else '❌'}")
            
            self.reportes['datamanager'] = reporte
            return dm.kpis_data, kpis_dm
            
        except Exception as e:
            print(f"❌ Error en auditoría DataManager: {e}")
            return None, []
    
    def auditar_core_engine(self, df_datamanager):
        """Auditoría del Core Engine."""
        print("\n🔍 PASO 3: Auditoría del Core Engine")
        print("=" * 50)
        
        try:
            # Configuración de prueba
            config = {
                'trading_style': 'balanced',
                'alpha': 0.7,
                'percentil': 90,
                'kpis_seleccionados': [
                    'CAGR (IS)', 'CAGR (OOS)', 'Sharpe Ratio (IS)', 'Sharpe Ratio (OOS)',
                    'Sortino Ratio', 'SQN Score (IS)', 'SQN Score (OOS)', 'Drawdown (IS)', 'Drawdown (OOS)',
                    'Profit factor (IS)', 'Profit factor (OOS)', 'RecoveryFactor'
                ]
            }
            
            # Ejecutar análisis principal
            resultados = run_complete_analysis_with_gui_integration(
                file_path='DatabankExport_M1.csv',
                config=config
            )
            
            if len(resultados) != 2:
                print("❌ Error: Core Engine no retornó resultados correctos")
                return None, []
            
            df_core = resultados[0]
            
            # KPIs en Core Engine
            kpis_core = [
                col for col in df_core.columns
                if pd.api.types.is_numeric_dtype(df_core[col])
            ]
            
            # KPIs perdidos vs DataManager
            kpis_perdidos = [kpi for kpi in df_datamanager.columns if kpi not in df_core.columns]
            kpis_nuevos = [kpi for kpi in df_core.columns if kpi not in df_datamanager.columns]
            
            # Verificar cálculos específicos
            calculos_verificados = self._verificar_calculos_core(df_core)
            
            reporte = {
                'total_estrategias': len(df_core),
                'total_columnas': len(df_core.columns),
                'kpis_numericos': kpis_core,
                'kpis_perdidos': kpis_perdidos,
                'kpis_nuevos': kpis_nuevos,
                'calculos_verificados': calculos_verificados,
                'configuracion_usada': config
            }
            
            print(f"✅ Core Engine auditado:")
            print(f"  • Estrategias: {len(df_core)}")
            print(f"  • KPIs numéricos: {len(kpis_core)}")
            print(f"  • KPIs perdidos: {len(kpis_perdidos)}")
            print(f"  • KPIs nuevos: {len(kpis_nuevos)}")
            print(f"  • Cálculos verificados: {len(calculos_verificados)}")
            
            self.reportes['core_engine'] = reporte
            return df_core, kpis_core
            
        except Exception as e:
            print(f"❌ Error en auditoría Core Engine: {e}")
            return None, []
    
    def auditar_asesor_financiero(self, df_core, kpis_core):
        """Auditoría del Asesor Financiero."""
        print("\n🔍 PASO 4: Auditoría del Asesor Financiero")
        print("=" * 50)
        
        try:
            # Simular filtrado por percentil
            if 'Unified_Score' in df_core.columns:
                threshold = df_core['Unified_Score'].quantile(0.9)
                df_filtrado = df_core[df_core['Unified_Score'] >= threshold]
            else:
                df_filtrado = df_core.copy()
            
            # Normalizar para asesor financiero
            from src.gui_enhanced_rank import normalizar_columnas_y_kpis
            df_normalizado, kpis_asesor = normalizar_columnas_y_kpis(df_filtrado.copy())
            
            # Verificar KPIs disponibles
            kpis_disponibles = len(kpis_asesor)
            kpis_suficientes = kpis_disponibles >= 5
            
            # Probar asesor financiero
            if kpis_suficientes:
                try:
                    asesor = AsesorFinancieroInteligente(df_normalizado, kpis_asesor)
                    resultados_asesor = asesor.generar_consejos_completos()
                    
                    consejos_generados = len(resultados_asesor.get('consejos_completos', []))
                    analisis_completos = len(resultados_asesor.get('analisis_completos', {}))
                    
                    asesor_funcionando = True
                except Exception as e:
                    print(f"❌ Error en asesor financiero: {e}")
                    consejos_generados = 0
                    analisis_completos = 0
                    asesor_funcionando = False
            else:
                consejos_generados = 0
                analisis_completos = 0
                asesor_funcionando = False
            
            reporte = {
                'estrategias_filtradas': len(df_filtrado),
                'kpis_disponibles': kpis_disponibles,
                'kpis_suficientes': kpis_suficientes,
                'kpis_asesor': kpis_asesor,
                'asesor_funcionando': asesor_funcionando,
                'consejos_generados': consejos_generados,
                'analisis_completos': analisis_completos,
                'normalizacion_aplicada': True
            }
            
            print(f"✅ Asesor Financiero auditado:")
            print(f"  • Estrategias filtradas: {len(df_filtrado)}")
            print(f"  • KPIs disponibles: {kpis_disponibles}")
            print(f"  • KPIs suficientes: {'✅' if kpis_suficientes else '❌'}")
            print(f"  • Asesor funcionando: {'✅' if asesor_funcionando else '❌'}")
            print(f"  • Consejos generados: {consejos_generados}")
            
            self.reportes['asesor_financiero'] = reporte
            return df_filtrado, kpis_asesor
            
        except Exception as e:
            print(f"❌ Error en auditoría Asesor Financiero: {e}")
            return None, []
    
    def _categorizar_kpis(self, kpis):
        """Categorizar KPIs por tipo."""
        categorias = {
            'Rendimiento': [],
            'Riesgo': [],
            'Consistencia': [],
            'Otros': []
        }
        
        for kpi in kpis:
            kpi_lower = kpi.lower()
            if any(term in kpi_lower for term in ['cagr', 'profit', 'return', 'net']):
                categorias['Rendimiento'].append(kpi)
            elif any(term in kpi_lower for term in ['drawdown', 'risk', 'var', 'cvar', 'ulcer']):
                categorias['Riesgo'].append(kpi)
            elif any(term in kpi_lower for term in ['sharpe', 'sortino', 'sqn', 'calmar', 'consistency']):
                categorias['Consistencia'].append(kpi)
            else:
                categorias['Otros'].append(kpi)
        
        return categorias
    
    def _verificar_normalizacion(self, columnas_originales, columnas_normalizadas):
        """Verificar que la normalización sea correcta."""
        # Verificar que no se perdieron columnas importantes
        columnas_importantes = ['Strategy', 'CAGR', 'Sharpe', 'Profit', 'Drawdown']
        perdidas_importantes = []
        
        for col_imp in columnas_importantes:
            if not any(col_imp.lower() in col.lower() for col in columnas_normalizadas):
                perdidas_importantes.append(col_imp)
        
        return len(perdidas_importantes) == 0
    
    def _verificar_calculos_core(self, df_core):
        """Verificar que los cálculos del core engine estén presentes."""
        calculos_esperados = [
            'Unified_Score', 'QVA_Score', 'QVA_Score_Robust',
            'FK96_Stability_Enhanced', 'FK96_Growth_Enhanced',
            'FK96_Efficiency_Enhanced', 'FK96_Consistency_Enhanced'
        ]
        
        calculos_presentes = []
        for calculo in calculos_esperados:
            if calculo in df_core.columns:
                calculos_presentes.append(calculo)
        
        return calculos_presentes
    
    def generar_reporte_final(self):
        """Generar reporte final de auditoría."""
        print("\n📊 GENERANDO REPORTE FINAL DE AUDITORÍA")
        print("=" * 60)
        
        # Resumen ejecutivo
        resumen = {
            'fecha_auditoria': self.fecha_auditoria,
            'componentes_auditados': list(self.reportes.keys()),
            'estado_general': 'COMPLETADO',
            'problemas_detectados': [],
            'recomendaciones': []
        }
        
        # Verificar problemas
        for componente, reporte in self.reportes.items():
            if componente == 'csv_original':
                if reporte['valores_faltantes']:
                    resumen['problemas_detectados'].append(f"CSV: {len(reporte['valores_faltantes'])} KPIs con valores faltantes")
            
            elif componente == 'datamanager':
                if reporte['kpis_perdidos']:
                    resumen['problemas_detectados'].append(f"DataManager: {len(reporte['kpis_perdidos'])} KPIs perdidos")
                if not reporte['normalizacion_correcta']:
                    resumen['problemas_detectados'].append("DataManager: Normalización incorrecta")
            
            elif componente == 'core_engine':
                if reporte['kpis_perdidos']:
                    resumen['problemas_detectados'].append(f"Core Engine: {len(reporte['kpis_perdidos'])} KPIs perdidos")
                if len(reporte['calculos_verificados']) < 3:
                    resumen['problemas_detectados'].append("Core Engine: Cálculos principales faltantes")
            
            elif componente == 'asesor_financiero':
                if not reporte['kpis_suficientes']:
                    resumen['problemas_detectados'].append("Asesor: KPIs insuficientes")
                if not reporte['asesor_funcionando']:
                    resumen['problemas_detectados'].append("Asesor: No funciona correctamente")
        
        # Generar recomendaciones
        if not resumen['problemas_detectados']:
            resumen['recomendaciones'].append("✅ Sistema funcionando correctamente")
        else:
            resumen['recomendaciones'].append("🔧 Revisar problemas detectados")
            resumen['recomendaciones'].append("📊 Verificar flujo de KPIs")
            resumen['recomendaciones'].append("🔍 Auditar normalización de nombres")
        
        # Guardar reporte completo
        reporte_completo = {
            'resumen_ejecutivo': resumen,
            'detalles_por_componente': self.reportes
        }
        
        with open('auditoria_kpis_completa.json', 'w', encoding='utf-8') as f:
            json.dump(reporte_completo, f, indent=2, ensure_ascii=False)
        
        # Mostrar resumen
        print(f"📊 RESUMEN EJECUTIVO:")
        print(f"  • Componentes auditados: {len(self.reportes)}")
        print(f"  • Problemas detectados: {len(resumen['problemas_detectados'])}")
        print(f"  • Estado: {resumen['estado_general']}")
        
        if resumen['problemas_detectados']:
            print(f"\n❌ PROBLEMAS DETECTADOS:")
            for problema in resumen['problemas_detectados']:
                print(f"  • {problema}")
        else:
            print(f"\n✅ SISTEMA FUNCIONANDO CORRECTAMENTE")
        
        print(f"\n💾 Reporte guardado en: auditoria_kpis_completa.json")
        
        return resumen

def ejecutar_auditoria_completa():
    """Ejecutar auditoría completa de KPIs."""
    print("🔍 AUDITORÍA COMPLETA DE KPIs - FISCALIZACIÓN")
    print("=" * 60)
    
    auditoria = AuditoriaKPIs()
    
    # Paso 1: CSV Original
    df_original, kpis_original = auditoria.auditar_csv_original()
    if df_original is None:
        print("❌ Error crítico: No se pudo auditar CSV original")
        return
    
    # Paso 2: DataManager
    df_datamanager, kpis_datamanager = auditoria.auditar_datamanager(df_original)
    if df_datamanager is None:
        print("❌ Error crítico: No se pudo auditar DataManager")
        return
    
    # Paso 3: Core Engine
    df_core, kpis_core = auditoria.auditar_core_engine(df_datamanager)
    if df_core is None:
        print("❌ Error crítico: No se pudo auditar Core Engine")
        return
    
    # Paso 4: Asesor Financiero
    df_asesor, kpis_asesor = auditoria.auditar_asesor_financiero(df_core, kpis_core)
    if df_asesor is None:
        print("❌ Error crítico: No se pudo auditar Asesor Financiero")
        return
    
    # Generar reporte final
    resumen = auditoria.generar_reporte_final()
    
    print("\n" + "=" * 60)
    print("✅ AUDITORÍA COMPLETA FINALIZADA")
    print("=" * 60)

if __name__ == "__main__":
    ejecutar_auditoria_completa() 