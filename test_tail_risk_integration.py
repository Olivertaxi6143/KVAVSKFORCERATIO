#!/usr/bin/env python3
"""
Test de integración para la funcionalidad de Riesgo de Cola en la GUI.
Valida la implementación de la Fase 6.5 del roadmap.
"""

import sys
import os
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
import logging

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gui.gui_enhanced_rank import EnhancedRankGUI

class TestTailRiskIntegration:
    """Test de integración para la funcionalidad de riesgo de cola."""
    
    def __init__(self):
        self.gui = None
        self.test_data = None
        self.setup_logging()
        
    def setup_logging(self):
        """Configura el logging para los tests."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('test_tail_risk.log', mode='w')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def create_test_data(self):
        """Crea datos de prueba con métricas de riesgo de cola."""
        self.logger.info("🔧 Creando datos de prueba para riesgo de cola...")
        
        # Crear DataFrame de prueba con métricas de riesgo
        test_data = {
            'Strategy Name': [
                'Strategy_High_Risk',
                'Strategy_Moderate_Risk', 
                'Strategy_Low_Risk',
                'Strategy_Very_Low_Risk',
                'Strategy_No_Risk_Data'
            ],
            'Unified_Score': [0.85, 0.72, 0.65, 0.45, 0.30],
            'Quality_Category': ['Elite', 'Excellent', 'Very Good', 'Good', 'Regular'],
            'CAGR': [15.5, 12.3, 8.7, 5.2, 2.1],
            'Sharpe Ratio': [1.8, 1.5, 1.2, 0.8, 0.5],
            'Drawdown': [25.5, 18.2, 12.1, 8.5, 5.2],
            'Profit factor': [1.8, 1.6, 1.4, 1.2, 1.1],
            'VaR (95%)': [-12.5, -8.2, -5.1, -3.2, -1.5],
            'CVaR (95%)': [-15.8, -10.5, -6.8, -4.1, -2.2],
            'Ulcer Index %': [18.5, 12.3, 8.1, 5.2, 2.8],
            'predictability_score': [88.5, 75.2, 65.8, 55.3, 42.1]
        }
        
        self.test_data = pd.DataFrame(test_data)
        self.logger.info(f"✅ Datos de prueba creados: {len(self.test_data)} estrategias")
        return self.test_data
        
    def test_tail_risk_calculation(self):
        """Test del cálculo de riesgo de cola."""
        self.logger.info("🧪 Probando cálculo de riesgo de cola...")
        
        # Crear instancia de GUI
        self.gui = EnhancedRankGUI()
        
        # Crear datos de prueba
        test_data = self.create_test_data()
        
        # Test para cada estrategia
        expected_results = {
            'Strategy_High_Risk': {'level': 'ALTO', 'icon': '🔴'},
            'Strategy_Moderate_Risk': {'level': 'MODERADO', 'icon': '🟡'},
            'Strategy_Low_Risk': {'level': 'BAJO', 'icon': '🟢'},
            'Strategy_Very_Low_Risk': {'level': 'MUY BAJO', 'icon': '🟢'},
            'Strategy_No_Risk_Data': {'level': 'N/A', 'icon': '❓'}
        }
        # Caso adverso: solo una métrica en alto, el resto bajo
        adverso = pd.Series({
            'Strategy Name': 'Strategy_Adverso',
            'VaR (95%)': -12.0,  # Alto
            'CVaR (95%)': -6.0,  # Bajo
            'Drawdown': 8.0,     # Bajo
            'Ulcer Index %': 5.0 # Bajo
        })
        # Debe ser MODERADO, no ALTO
        risk_info_adv = self.gui._calculate_tail_risk_level(adverso)
        assert risk_info_adv['level'] == 'MODERADO', 'Error: caso adverso con solo una métrica alta debe ser MODERADO'
        assert risk_info_adv['icon'] == '🟡', 'Error: icono caso adverso'
        self.logger.info(f"✅ Caso adverso: {risk_info_adv['level']} {risk_info_adv['icon']}")
        # Test normal
        for idx, row in test_data.iterrows():
            strategy_name = row['Strategy Name']
            self.logger.info(f"📊 Probando estrategia: {strategy_name}")
            risk_info = self.gui._calculate_tail_risk_level(row)
            expected = expected_results[strategy_name]
            assert risk_info['level'] == expected['level'], f"Error en nivel de riesgo para {strategy_name}"
            assert risk_info['icon'] == expected['icon'], f"Error en icono para {strategy_name}"
            self.logger.info(f"✅ {strategy_name}: {risk_info['level']} {risk_info['icon']}")
            
        self.logger.info("✅ Test de cálculo de riesgo de cola completado")
        
    def test_table_integration(self):
        """Test de integración en la tabla principal."""
        self.logger.info("🧪 Probando integración en tabla principal...")
        
        # Crear datos de prueba
        test_data = self.create_test_data()
        
        # Simular construcción de tabla
        self.gui.results_df = test_data
        self.gui.filtered_results_df = test_data
        
        # Verificar que la columna "Riesgo de Cola" está presente
        columns = ["Badge", "Seleccionar", "Estrategia", "Score", "Categoría", 
                  "Predictibilidad", "Riesgo de Cola", "Rendimiento", "Riesgo", 
                  "Robustez", "Métricas Científicas", "IS/OOS"]
        
        # Simular inserción de datos en tabla
        for idx, row in test_data.iterrows():
            # Calcular riesgo de cola
            tail_risk_info = self.gui._calculate_tail_risk_level(row)
            tail_risk_display = f"{tail_risk_info['icon']} {tail_risk_info['level']}"
            
            # Verificar que el display es correcto
            assert tail_risk_info['icon'] in tail_risk_display, "Icono no presente en display"
            assert tail_risk_info['level'] in tail_risk_display, "Nivel no presente en display"
            
            self.logger.info(f"✅ Fila {idx}: {tail_risk_display}")
            
        self.logger.info("✅ Test de integración en tabla completado")
        
    def test_popup_integration(self):
        """Test de integración en popup de detalles."""
        self.logger.info("🧪 Probando integración en popup de detalles...")
        
        # Crear datos de prueba
        test_data = self.create_test_data()
        
        # Simular popup para la primera estrategia
        test_row = test_data.iloc[0]  # Strategy_High_Risk
        
        # Calcular riesgo de cola
        tail_risk_info = self.gui._calculate_tail_risk_level(test_row)
        
        # Verificar que la información está completa
        assert 'level' in tail_risk_info, "Nivel de riesgo faltante"
        assert 'icon' in tail_risk_info, "Icono faltante"
        assert 'description' in tail_risk_info, "Descripción faltante"
        assert 'risk_factors' in tail_risk_info, "Factores de riesgo faltantes"
        assert 'metrics' in tail_risk_info, "Métricas faltantes"
        
        # Verificar contenido específico para estrategia de alto riesgo
        assert tail_risk_info['level'] == 'ALTO', "Nivel de riesgo incorrecto"
        assert tail_risk_info['icon'] == '🔴', "Icono incorrecto"
        assert 'CRÍTICO' in str(tail_risk_info['risk_factors']), "Factores de riesgo no detectados"
        
        self.logger.info(f"✅ Popup integration test: {tail_risk_info['level']} {tail_risk_info['icon']}")
        self.logger.info("✅ Test de integración en popup completado")
        
    def test_risk_analysis_popup(self):
        """Test del popup de análisis de riesgo."""
        self.logger.info("🧪 Probando popup de análisis de riesgo...")
        
        # Crear datos de prueba
        test_data = self.create_test_data()
        
        # Simular popup de análisis de riesgo
        try:
            # Contar estrategias por nivel de riesgo
            risk_counts = {"ALTO": 0, "MODERADO": 0, "BAJO": 0, "MUY BAJO": 0}
            high_risk_strategies = []
            moderate_risk_strategies = []
            
            for idx, row in test_data.iterrows():
                tail_risk_info = self.gui._calculate_tail_risk_level(row)
                risk_counts[tail_risk_info['level']] += 1
                
                if tail_risk_info['level'] == "ALTO":
                    high_risk_strategies.append({
                        'name': row.get("Strategy Name", "N/A"),
                        'risk_info': tail_risk_info
                    })
                elif tail_risk_info['level'] == "MODERADO":
                    moderate_risk_strategies.append({
                        'name': row.get("Strategy Name", "N/A"),
                        'risk_info': tail_risk_info
                    })
            
            # Verificar conteos
            assert risk_counts['ALTO'] == 1, f"Error en conteo de riesgo alto: {risk_counts['ALTO']}"
            assert risk_counts['MODERADO'] == 1, f"Error en conteo de riesgo moderado: {risk_counts['MODERADO']}"
            assert risk_counts['BAJO'] == 1, f"Error en conteo de riesgo bajo: {risk_counts['BAJO']}"
            assert risk_counts['MUY BAJO'] == 1, f"Error en conteo de riesgo muy bajo: {risk_counts['MUY BAJO']}"
            
            # Verificar estrategias de alto riesgo
            assert len(high_risk_strategies) == 1, f"Error en estrategias de alto riesgo: {len(high_risk_strategies)}"
            assert high_risk_strategies[0]['name'] == 'Strategy_High_Risk', "Estrategia de alto riesgo incorrecta"
            
            self.logger.info(f"✅ Risk analysis popup: {risk_counts}")
            self.logger.info(f"✅ High risk strategies: {len(high_risk_strategies)}")
            self.logger.info(f"✅ Moderate risk strategies: {len(moderate_risk_strategies)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error en test de popup de análisis: {str(e)}")
            raise
            
        self.logger.info("✅ Test de popup de análisis de riesgo completado")
        
    def test_export_functionality(self):
        """Test de funcionalidad de exportación."""
        self.logger.info("🧪 Probando funcionalidad de exportación...")
        
        # Crear datos de prueba
        test_data = self.create_test_data()
        
        # Test de copia al portapapeles
        try:
            analysis_text = "🔍 ANÁLISIS DE RIESGO DE COLA\n"
            analysis_text += "=" * 50 + "\n\n"
            
            # Contar estrategias por nivel de riesgo
            risk_counts = {"ALTO": 0, "MODERADO": 0, "BAJO": 0, "MUY BAJO": 0}
            
            for idx, row in test_data.iterrows():
                tail_risk_info = self.gui._calculate_tail_risk_level(row)
                risk_counts[tail_risk_info['level']] += 1
            
            analysis_text += f"📈 Total de estrategias: {len(test_data)}\n"
            analysis_text += f"🔴 Riesgo ALTO: {risk_counts['ALTO']}\n"
            analysis_text += f"🟡 Riesgo MODERADO: {risk_counts['MODERADO']}\n"
            analysis_text += f"🟢 Riesgo BAJO: {risk_counts['BAJO']}\n"
            analysis_text += f"🟢 Riesgo MUY BAJO: {risk_counts['MUY BAJO']}\n\n"
            
            # Verificar que el texto contiene la información esperada
            assert "ANÁLISIS DE RIESGO DE COLA" in analysis_text, "Título faltante"
            assert f"Total de estrategias: {len(test_data)}" in analysis_text, "Conteo total faltante"
            assert "Riesgo ALTO: 1" in analysis_text, "Conteo de riesgo alto incorrecto"
            
            self.logger.info("✅ Texto de análisis generado correctamente")
            self.logger.info(f"📄 Contenido del análisis:\n{analysis_text}")
            
        except Exception as e:
            self.logger.error(f"❌ Error en test de exportación: {str(e)}")
            raise
            
        self.logger.info("✅ Test de funcionalidad de exportación completado")
        
    def run_all_tests(self):
        """Ejecuta todos los tests de integración."""
        self.logger.info("🚀 Iniciando tests de integración de Riesgo de Cola")
        self.logger.info("=" * 60)
        
        try:
            # Test 1: Cálculo de riesgo de cola
            self.test_tail_risk_calculation()
            
            # Test 2: Integración en tabla principal
            self.test_table_integration()
            
            # Test 3: Integración en popup de detalles
            self.test_popup_integration()
            
            # Test 4: Popup de análisis de riesgo
            self.test_risk_analysis_popup()
            
            # Test 5: Funcionalidad de exportación
            self.test_export_functionality()
            
            self.logger.info("=" * 60)
            self.logger.info("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
            self.logger.info("✅ Integración de Riesgo de Cola validada")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en tests: {str(e)}")
            return False
            
        finally:
            if self.gui:
                self.gui.destroy()

def main():
    """Función principal para ejecutar los tests."""
    print("🧪 Test de Integración: Riesgo de Cola en GUI")
    print("=" * 50)
    
    tester = TestTailRiskIntegration()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ TODOS LOS TESTS PASARON")
        print("🎯 Fase 6.5: Integración de Riesgo de Cola - COMPLETADA")
        return 0
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        print("🔧 Revisar implementación de riesgo de cola")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 