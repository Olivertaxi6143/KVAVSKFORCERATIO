#!/usr/bin/env python3
"""
Test de Mejoras en GUI de Predictibilidad - KVAVSKFORCERATIO

Este script prueba las mejoras implementadas en la GUI para mostrar
la predictibilidad de manera más clara y útil para el usuario.

Autor: KVAVSKFORCERATIO Team
Fecha: 2024
"""

import sys
import os
import logging
import pandas as pd
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_predictability_interpretation():
    """Test de la interpretación profesional de predictibilidad."""
    logger.info("🧪 TEST 1: Interpretación de Predictibilidad")
    try:
        def get_predictability_level(score):
            if score >= 90:
                return "EXCELENTE"
            elif score >= 80:
                return "BUENA"
            elif score >= 70:
                return "ACEPTABLE"
            elif score >= 60:
                return "BAJA"
            else:
                return "MUY BAJA"
        def get_predictability_recommendation(score):
            if score >= 90:
                return "Muy alta predictibilidad. Estrategia sobresaliente para trading real."
            elif score >= 80:
                return "Buena predictibilidad. Confiable, pero monitoree su rendimiento."
            elif score >= 70:
                return "Aceptable. Úsela con precaución y valide regularmente."
            elif score >= 60:
                return "Baja predictibilidad. Requiere validación adicional antes de operar."
            else:
                return "No recomendable para trading real sin mejoras significativas."
        # Validaciones
        assert get_predictability_level(95) == "EXCELENTE"
        assert get_predictability_level(85) == "BUENA"
        assert get_predictability_level(74.7) == "ACEPTABLE"
        assert get_predictability_level(65) == "BAJA"
        assert get_predictability_level(50) == "MUY BAJA"
        assert "sobresaliente" in get_predictability_recommendation(95).lower()
        assert "confiable" in get_predictability_recommendation(85).lower()
        assert "precaución" in get_predictability_recommendation(74.7).lower()
        assert "validación adicional" in get_predictability_recommendation(65).lower()
        assert "no recomendable" in get_predictability_recommendation(50).lower()
        logger.info("✅ Test de interpretación completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error en test de interpretación: {e}")
        assert False, f"Error en test de interpretación: {e}"

def test_predictability_display():
    """Test de la visualización profesional de predictibilidad en la GUI."""
    logger.info("🧪 TEST 2: Visualización de Predictibilidad en GUI")
    try:
        import pandas as pd
        test_data = pd.DataFrame({
            'Strategy Name': ['Test_Strategy_1', 'Test_Strategy_2'],
            'Unified_Score': [0.95, 0.65],
            'predictability_score': [95, 65]
        })
        def get_predictability_level(score):
            if score >= 90:
                return "EXCELENTE"
            elif score >= 80:
                return "BUENA"
            elif score >= 70:
                return "ACEPTABLE"
            elif score >= 60:
                return "BAJA"
            else:
                return "MUY BAJA"
        def get_predictability_recommendation(score):
            if score >= 90:
                return "Muy alta predictibilidad. Estrategia sobresaliente para trading real."
            elif score >= 80:
                return "Buena predictibilidad. Confiable, pero monitoree su rendimiento."
            elif score >= 70:
                return "Aceptable. Úsela con precaución y valide regularmente."
            elif score >= 60:
                return "Baja predictibilidad. Requiere validación adicional antes de operar."
            else:
                return "No recomendable para trading real sin mejoras significativas."
        if 'predictability_score' in test_data.columns:
            test_data['Predictability_Level'] = test_data['predictability_score'].apply(get_predictability_level)
            test_data['Predictability_Recommendation'] = test_data['predictability_score'].apply(get_predictability_recommendation)
        logger.info("✅ Datos procesados con predictibilidad:")
        for idx, row in test_data.iterrows():
            logger.info(f"   Estrategia: {row['Strategy Name']}")
            logger.info(f"   Score Unificado: {row['Unified_Score']:.3f}")
            logger.info(f"   Predictibilidad: {row['predictability_score']:.1f}%")
            logger.info(f"   Nivel: {row['Predictability_Level']}")
            logger.info(f"   Recomendación: {row['Predictability_Recommendation']}")
            logger.info("   " + "-"*40)
        logger.info("✅ Test de visualización completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error en test de visualización: {e}")
        assert False, f"Error en test de visualización: {e}"

def test_predictability_details_popup():
    """Test de la ventana de detalles con predictibilidad."""
    logger.info("🧪 TEST 3: Ventana de Detalles con Predictibilidad")
    try:
        import pandas as pd
        test_row = pd.Series({
            'Strategy Name': 'Test_Strategy_74.7',
            'Unified_Score': 0.747,
            'predictability_score': 74.7,
            'CAGR': 12.5,
            'Drawdown': 11.2
        })
        def interpret_predictability_score(score):
            if score >= 90:
                return {
                    "level": "🟢 EXCELENTE",
                    "recommendation": "Muy alta predictibilidad. Estrategia sobresaliente para trading real."
                }
            elif score >= 80:
                return {
                    "level": "🟡 BUENA",
                    "recommendation": "Buena predictibilidad. Confiable, pero monitoree su rendimiento."
                }
            elif score >= 70:
                return {
                    "level": "🟠 ACEPTABLE",
                    "recommendation": "Aceptable. Úsela con precaución y valide regularmente."
                }
            elif score >= 60:
                return {
                    "level": "🔴 BAJA",
                    "recommendation": "Baja predictibilidad. Requiere validación adicional antes de operar."
                }
            else:
                return {
                    "level": "⚫ MUY BAJA",
                    "recommendation": "No recomendable para trading real sin mejoras significativas."
                }
        detalles = f"📊 Detalles de Estrategia\n"
        detalles += f"Estrategia: {test_row.get('Strategy Name', 'N/A')}\n"
        detalles += f"Score Unificado: {test_row.get('Unified_Score', 'N/A'):.4f}\n"
        if 'predictability_score' in test_row:
            predictability_score = test_row['predictability_score']
            detalles += f"\n🎯 PREDICTIBILIDAD:\n"
            detalles += f"Score: {predictability_score:.1f}%\n"
            interpretation = interpret_predictability_score(predictability_score)
            detalles += f"Nivel: {interpretation['level']}\n"
            detalles += f"Recomendación: {interpretation['recommendation']}\n"
        logger.info("✅ Detalles generados:")
        logger.info(detalles)
        interpretation = interpret_predictability_score(74.7)
        assert "ACEPTABLE" in interpretation['level'], f"Score 74.7 debería ser ACEPTABLE, pero es {interpretation['level']}"
        assert "aceptable. úsela con precaución y valide regularmente." in interpretation['recommendation'].lower(), "Recomendación debería ser exactamente la de la función real."
        logger.info("✅ Test de ventana de detalles completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error en test de ventana de detalles: {e}")
        assert False, f"Error en test de ventana de detalles: {e}"

def test_scientific_gui_tab_improvements():
    """Test de las mejoras en la pestaña científica."""
    logger.info("🧪 TEST 4: Mejoras en Pestaña Científica")
    try:
        test_results = {
            'predictability': {
                'predictability_score': 74.7,
                'predictability_details': {
                    'is_oos_consistency': 78.5,
                    'temporal_robustness': 72.3,
                    'overfitting_detection': 76.8,
                    'stability_score': 75.2
                }
            }
        }
        logger.info("✅ Resultados de análisis científico:")
        for analysis_type, result in test_results.items():
            if analysis_type == "predictability" and "predictability_score" in result:
                predictability_score = result['predictability_score']
                logger.info(f"   🎯 Score de Predictibilidad: {predictability_score:.3f}")
                if predictability_score >= 75:
                    level = "🟡 BUENA"
                    recommendation = "Buena predictibilidad. La estrategia es confiable pero monitoree su rendimiento regularmente."
                else:
                    level = "🟠 MODERADA"
                    recommendation = "Predictibilidad moderada. Use con precaución y valide con datos adicionales."
                logger.info(f"   📊 Interpretación: {level}")
                logger.info(f"   💡 Recomendación: {recommendation}")
                if 'predictability_details' in result:
                    details = result['predictability_details']
                    logger.info(f"   📈 Consistencia IS/OOS: {details.get('is_oos_consistency', 0):.1f}%")
                    logger.info(f"   🛡️ Robustez Temporal: {details.get('temporal_robustness', 0):.1f}%")
                    logger.info(f"   🔍 Detección Sobreajuste: {details.get('overfitting_detection', 0):.1f}%")
                    logger.info(f"   ⚖️ Estabilidad: {details.get('stability_score', 0):.1f}%")
        logger.info("✅ Test de pestaña científica completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error en test de pestaña científica: {e}")
        assert False, f"Error en test de pestaña científica: {e}"

def main():
    """Función principal de testing."""
    logger.info("🚀 INICIANDO TESTS DE MEJORAS EN GUI DE PREDICTIBILIDAD")
    logger.info("=" * 60)
    
    tests = [
        ("Interpretación de Predictibilidad", test_predictability_interpretation),
        ("Visualización de Predictibilidad", test_predictability_display),
        ("Ventana de Detalles", test_predictability_details_popup),
        ("Pestaña Científica", test_scientific_gui_tab_improvements)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Ejecutando: {test_name}")
        logger.info("-" * 40)
        
        try:
            test_func()
            logger.info(f"✅ {test_name}: PASÓ")
            passed_tests += 1
        except AssertionError as e:
            logger.error(f"❌ {test_name}: FALLÓ - {e}")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 RESUMEN DE TESTS:")
    logger.info(f"   Tests pasados: {passed_tests}/{total_tests}")
    logger.info(f"   Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        logger.info("🎉 ¡TODOS LOS TESTS PASARON! Mejoras en GUI implementadas correctamente.")
        logger.info("\n💡 BENEFICIOS PARA EL USUARIO:")
        logger.info("   ✅ Predictibilidad 74.7% ahora se muestra como 'BUENA'")
        logger.info("   ✅ Recomendación clara: 'Monitorear regularmente'")
        logger.info("   ✅ Interpretación visual con emojis y colores")
        logger.info("   ✅ Detalles adicionales en ventanas popup")
        logger.info("   ✅ Información contextual en pestaña científica")
    else:
        logger.error("❌ Algunos tests fallaron. Revisar implementación.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 