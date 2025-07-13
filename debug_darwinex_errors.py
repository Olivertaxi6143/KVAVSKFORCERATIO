#!/usr/bin/env python3
"""
Script de debug para identificar errores específicos en la integración de DarwinEX
"""

import sys
import os
import traceback

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_1_import_darwinex():
    """Test 1: Importación de DarwinEXPipeline."""
    print("=" * 60)
    print("TEST 1: IMPORTACIÓN DE DARWINEX PIPELINE")
    print("=" * 60)
    
    try:
        from src.analysis.darwinex_pipeline import DarwinEXPipeline, PipelineResult
        print("✅ Importación DarwinEXPipeline: PASSED")
        
        pipeline = DarwinEXPipeline()
        print("✅ Creación de instancia: PASSED")
        
        config = pipeline.config
        print(f"✅ Configuración disponible: PASSED - {len(config)} secciones")
        
    except Exception as e:
        print(f"❌ Importación DarwinEXPipeline: FAILED - {str(e)}")
        traceback.print_exc()

def test_2_pipeline_execution():
    """Test 2: Ejecución del pipeline DarwinEX."""
    print("=" * 60)
    print("TEST 2: EJECUCIÓN DEL PIPELINE DARWINEX")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from src.analysis.darwinex_pipeline import DarwinEXPipeline
        
        # Crear datos de prueba
        np.random.seed(42)
        n_strategies = 5  # Reducir para debug
        
        data = {
            'Strategy_Name': [f'Strategy_{i+1}' for i in range(n_strategies)],
            'D_Score': np.random.uniform(50, 90, n_strategies),
            'Years_Running': np.random.uniform(0.5, 5.0, n_strategies),
            'LEA': np.random.uniform(-0.1, 0.3, n_strategies),
            'OS': np.random.uniform(-0.1, 0.3, n_strategies),
            'Correlation_6m': np.random.uniform(0.1, 0.4, n_strategies),
            'Frequency_Stability': np.random.uniform(0.2, 0.8, n_strategies),
            'DD_Correlation': np.random.uniform(0.3, 0.7, n_strategies),
            'Max_Drawdown': np.random.uniform(5, 25, n_strategies),
            'Unified_Score': np.random.uniform(0.3, 0.9, n_strategies),
            'CAGR': np.random.uniform(5, 50, n_strategies),
            'Sharpe_Ratio': np.random.uniform(0.5, 3.0, n_strategies),
            'Profit_factor': np.random.uniform(1.1, 3.0, n_strategies),
            'Drawdown': np.random.uniform(5, 25, n_strategies)
        }
        
        test_data = pd.DataFrame(data)
        print(f"✅ Creación datos de prueba: PASSED - {len(test_data)} estrategias")
        
        pipeline = DarwinEXPipeline()
        results = pipeline.run_pipeline(test_data)
        print(f"✅ Ejecución pipeline: PASSED - {len(results)} resultados")
        
        if results:
            first_result = results[0]
            required_attrs = ['strategy_name', 'passed_filters', 'failed_filters', 
                            'final_score', 'ticket_size', 'category']
            
            all_attrs_present = all(hasattr(first_result, attr) for attr in required_attrs)
            print(f"✅ Estructura de resultados: {'PASSED' if all_attrs_present else 'FAILED'}")
            
            score_valid = isinstance(first_result.final_score, (int, float))
            ticket_valid = isinstance(first_result.ticket_size, (int, float))
            print(f"✅ Tipos de datos: {'PASSED' if score_valid and ticket_valid else 'FAILED'}")
        
    except Exception as e:
        print(f"❌ Ejecución pipeline: FAILED - {str(e)}")
        traceback.print_exc()

def test_3_gui_integration():
    """Test 3: Integración en la GUI."""
    print("=" * 60)
    print("TEST 3: INTEGRACIÓN EN LA GUI")
    print("=" * 60)
    
    try:
        from src.gui.gui_enhanced_rank import EnhancedRankGUI
        
        # Crear GUI
        gui = EnhancedRankGUI()
        print("✅ Creación GUI: PASSED")
        
        # Verificar que existe la pestaña DarwinEX
        has_darwinex_tab = hasattr(gui, 'tab_darwinex')
        print(f"✅ Pestaña DarwinEX creada: {'PASSED' if has_darwinex_tab else 'FAILED'}")
        
        # Verificar métodos de DarwinEX
        required_methods = [
            '_build_darwinex_tab',
            '_run_darwinex_pipeline',
            '_show_darwinex_results_in_gui',
            '_show_darwinex_error',
            '_show_darwinex_results',
            '_build_approved_strategies_tab',
            '_build_rejected_strategies_tab',
            '_build_metrics_tab',
            '_export_darwinex_report',
            '_clear_darwinex_results'
        ]
        
        methods_present = all(hasattr(gui, method) for method in required_methods)
        print(f"✅ Métodos DarwinEX: {'PASSED' if methods_present else 'FAILED'}")
        
        # Verificar variables de DarwinEX
        has_darwinex_vars = hasattr(gui, 'darwinex_text') and hasattr(gui, 'darwinex_results_frame')
        print(f"✅ Variables DarwinEX: {'PASSED' if has_darwinex_vars else 'FAILED'}")
        
        # Verificar métodos específicos
        for method in required_methods:
            if hasattr(gui, method):
                print(f"  ✅ {method}: PRESENTE")
            else:
                print(f"  ❌ {method}: AUSENTE")
        
        gui.destroy()
        
    except Exception as e:
        print(f"❌ Integración GUI: FAILED - {str(e)}")
        traceback.print_exc()

def test_4_pipeline_report():
    """Test 4: Generación de reportes del pipeline."""
    print("=" * 60)
    print("TEST 4: GENERACIÓN DE REPORTES")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from src.analysis.darwinex_pipeline import DarwinEXPipeline
        
        # Crear datos y pipeline
        np.random.seed(42)
        n_strategies = 5
        
        data = {
            'Strategy_Name': [f'Strategy_{i+1}' for i in range(n_strategies)],
            'D_Score': np.random.uniform(50, 90, n_strategies),
            'Years_Running': np.random.uniform(0.5, 5.0, n_strategies),
            'LEA': np.random.uniform(-0.1, 0.3, n_strategies),
            'OS': np.random.uniform(-0.1, 0.3, n_strategies),
            'Correlation_6m': np.random.uniform(0.1, 0.4, n_strategies),
            'Frequency_Stability': np.random.uniform(0.2, 0.8, n_strategies),
            'DD_Correlation': np.random.uniform(0.3, 0.7, n_strategies),
            'Max_Drawdown': np.random.uniform(5, 25, n_strategies),
            'Unified_Score': np.random.uniform(0.3, 0.9, n_strategies),
            'CAGR': np.random.uniform(5, 50, n_strategies),
            'Sharpe_Ratio': np.random.uniform(0.5, 3.0, n_strategies),
            'Profit_factor': np.random.uniform(1.1, 3.0, n_strategies),
            'Drawdown': np.random.uniform(5, 25, n_strategies)
        }
        
        test_data = pd.DataFrame(data)
        pipeline = DarwinEXPipeline()
        results = pipeline.run_pipeline(test_data)
        
        # Generar reporte
        report = pipeline.generate_pipeline_report(results)
        print(f"✅ Generación de reporte: {'PASSED' if bool(report) else 'FAILED'}")
        
        # Verificar estructura del reporte
        if report:
            required_sections = ['summary', 'ticket_categories', 'top_strategies', 
                               'risk_alerts', 'recommendations']
            
            sections_present = all(section in report for section in required_sections)
            print(f"✅ Estructura del reporte: {'PASSED' if sections_present else 'FAILED'}")
            
            # Verificar contenido del resumen
            if 'summary' in report:
                summary = report['summary']
                has_total = 'total_strategies' in summary
                has_passed = 'passed_strategies' in summary
                has_rejected = 'rejected_strategies' in summary
                
                print(f"✅ Contenido del resumen: {'PASSED' if has_total and has_passed and has_rejected else 'FAILED'}")
        
    except Exception as e:
        print(f"❌ Generación de reporte: FAILED - {str(e)}")
        traceback.print_exc()

def test_5_pipeline_filters():
    """Test 5: Validación de filtros del pipeline."""
    print("=" * 60)
    print("TEST 5: VALIDACIÓN DE FILTROS")
    print("=" * 60)
    
    try:
        from src.analysis.darwinex_pipeline import DarwinEXPipeline
        
        # Crear pipeline
        pipeline = DarwinEXPipeline()
        
        # Verificar configuración de filtros
        config = pipeline.config
        filters_config = config.get('filters', {})
        
        required_filters = [
            'gold_access', 'track_record', 'lea_os_positive',
            'correlation_6m', 'discipline', 'dd_correlation'
        ]
        
        filters_present = all(filter_name in filters_config for filter_name in required_filters)
        print(f"✅ Configuración de filtros: {'PASSED' if filters_present else 'FAILED'}")
        
        # Verificar configuración de scoring
        scoring_config = config.get('scoring', {})
        weights = scoring_config.get('weights', {})
        thresholds = scoring_config.get('thresholds', {})
        
        has_weights = len(weights) > 0
        has_thresholds = len(thresholds) > 0
        
        print(f"✅ Configuración de scoring: {'PASSED' if has_weights and has_thresholds else 'FAILED'}")
        
    except Exception as e:
        print(f"❌ Validación de filtros: FAILED - {str(e)}")
        traceback.print_exc()

def main():
    """Ejecuta todos los tests de debug."""
    print("🚀 INICIANDO DEBUG DE INTEGRACIÓN DARWINEX")
    print("=" * 60)
    
    test_1_import_darwinex()
    test_2_pipeline_execution()
    test_3_gui_integration()
    test_4_pipeline_report()
    test_5_pipeline_filters()
    
    print("=" * 60)
    print("🏁 DEBUG COMPLETADO")

if __name__ == "__main__":
    main() 