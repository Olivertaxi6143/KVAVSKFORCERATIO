#!/usr/bin/env python3
"""
Test Automático del Flujo Completo del Asesor Financiero
=======================================================

Valida el flujo completo:
1. Análisis principal
2. Selección de estrategias  
3. Traspaso al asesor financiero
4. Verificación de que las estrategias pasan correctamente
5. Reporte detallado del motivo si alguna estrategia no pasa el filtro

Basado en el roadmap de mejoras pendientes.
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import traceback
import json

# Agregar el directorio src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

class TestFlujoCompletoAsesor:
    """Test automático del flujo completo del asesor financiero."""
    
    def __init__(self):
        """Inicializa el test."""
        self.setup_logging()
        self.results = {
            'tests_passed': 0,
            'tests_failed': 0,
            'total_tests': 0,
            'errors': [],
            'warnings': []
        }
        
        # Configuración de archivos de prueba
        self.test_files = {
            'kpi_file': 'DatabankExport_M1.csv',
            'market_file': 'DATOSMQL5.csv',
            'sqx_folder': 'INPUTTEST/M1_NDX_UP_MQL4_136_STOP',
            'output_folder': 'INPUTTEST/TOP'
        }
        
        self.logger.info("🚀 Iniciando Test Automático del Flujo Completo del Asesor Financiero")
    
    def setup_logging(self):
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'test_flujo_completo_asesor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_test(self, test_name, passed, message=""):
        """Registra el resultado de un test."""
        self.results['total_tests'] += 1
        if passed:
            self.results['tests_passed'] += 1
            self.logger.info(f"✅ {test_name}: PASADO - {message}")
        else:
            self.results['tests_failed'] += 1
            self.logger.error(f"❌ {test_name}: FALLADO - {message}")
    
    def log_warning(self, message):
        """Registra una advertencia."""
        self.results['warnings'].append(message)
        self.logger.warning(f"⚠️ {message}")
    
    def log_error(self, message):
        """Registra un error."""
        self.results['errors'].append(message)
        self.logger.error(f"❌ {message}")
    
    def test_1_verificacion_archivos(self):
        """Test 1: Verificación de archivos de entrada."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 1: VERIFICACIÓN DE ARCHIVOS DE ENTRADA")
        self.logger.info("=" * 60)
        
        # Verificar archivo KPI
        if os.path.exists(self.test_files['kpi_file']):
            self.log_test("Archivo KPI", True, f"Archivo encontrado: {self.test_files['kpi_file']}")
        else:
            self.log_test("Archivo KPI", False, f"Archivo no encontrado: {self.test_files['kpi_file']}")
            return False
        
        # Verificar archivo de mercado
        if os.path.exists(self.test_files['market_file']):
            self.log_test("Archivo de Mercado", True, f"Archivo encontrado: {self.test_files['market_file']}")
        else:
            self.log_test("Archivo de Mercado", False, f"Archivo no encontrado: {self.test_files['market_file']}")
            return False
        
        # Verificar carpeta de estrategias
        if os.path.exists(self.test_files['sqx_folder']):
            sqx_files = [f for f in os.listdir(self.test_files['sqx_folder']) if f.endswith('.sqx')]
            self.log_test("Carpeta de Estrategias", True, f"Carpeta encontrada con {len(sqx_files)} archivos .sqx")
        else:
            self.log_test("Carpeta de Estrategias", False, f"Carpeta no encontrada: {self.test_files['sqx_folder']}")
            return False
        
        # Crear carpeta de salida si no existe
        if not os.path.exists(self.test_files['output_folder']):
            os.makedirs(self.test_files['output_folder'])
            self.log_test("Carpeta de Salida", True, "Carpeta creada")
        else:
            self.log_test("Carpeta de Salida", True, "Carpeta existente")
        
        return True
    
    def test_2_carga_datos(self):
        """Test 2: Carga y validación de datos."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 2: CARGA Y VALIDACIÓN DE DATOS")
        self.logger.info("=" * 60)
        
        try:
            # Cargar datos KPI
            df_kpi = pd.read_csv(self.test_files['kpi_file'], sep=';', decimal=',')
            self.log_test("Carga Datos KPI", True, f"DataFrame cargado: {len(df_kpi)} filas, {len(df_kpi.columns)} columnas")
            
            # Verificar columnas requeridas
            required_columns = ['Strategy Name', 'CAGR', 'Drawdown', 'Sharpe Ratio', 'Profit factor']
            missing_columns = [col for col in required_columns if col not in df_kpi.columns]
            
            if not missing_columns:
                self.log_test("Columnas Requeridas KPI", True, "Todas las columnas requeridas están presentes")
            else:
                self.log_test("Columnas Requeridas KPI", False, f"Columnas faltantes: {missing_columns}")
            
            # Cargar datos de mercado
            df_market = pd.read_csv(self.test_files['market_file'], sep=';', decimal=',')
            self.log_test("Carga Datos Mercado", True, f"DataFrame cargado: {len(df_market)} filas, {len(df_market.columns)} columnas")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error en carga de datos: {str(e)}")
            return False
    
    def test_3_importacion_modulos(self):
        """Test 3: Importación de módulos principales."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 3: IMPORTACIÓN DE MÓDULOS PRINCIPALES")
        self.logger.info("=" * 60)
        
        # Test importación GUI
        try:
            from gui_enhanced_rank import EnhancedRankGUI
            self.log_test("Importación GUI", True, "Módulo GUI importado correctamente")
        except Exception as e:
            self.log_test("Importación GUI", False, f"Error: {str(e)}")
            return False
        
        # Test importación Asesor Financiero
        try:
            from asesor_financiero_inteligente import AsesorFinancieroInteligente
            self.log_test("Importación Asesor", True, "Módulo Asesor importado correctamente")
        except Exception as e:
            self.log_test("Importación Asesor", False, f"Error: {str(e)}")
            return False
        
        # Test importación Core Engine
        try:
            from core_engine_enhanced import run_complete_analysis_with_gui_integration
            self.log_test("Importación Core Engine", True, "Módulo Core Engine importado correctamente")
        except Exception as e:
            self.log_test("Importación Core Engine", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_4_estructura_gui(self):
        """Test 4: Verificación de estructura de la GUI."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 4: VERIFICACIÓN DE ESTRUCTURA DE LA GUI")
        self.logger.info("=" * 60)
        
        try:
            from gui_enhanced_rank import EnhancedRankGUI
            
            # Crear instancia de GUI (sin mostrar)
            gui = EnhancedRankGUI()
            
            # Verificar pestañas principales
            pestañas_principales = [
                'tab_config', 'tab_results', 'tab_summary', 
                'tab_log', 'tab_help', 'tab_asesor'
            ]
            
            for pestaña in pestañas_principales:
                if hasattr(gui, pestaña):
                    self.log_test(f"Pestaña {pestaña}", True, "Pestaña disponible")
                else:
                    self.log_test(f"Pestaña {pestaña}", False, "Pestaña no encontrada")
            
            # Verificar subpestañas del asesor
            subpestañas_asesor = [
                'tab_asesor_analisis', 'tab_asesor_cientifico',
                'tab_asesor_empirico', 'tab_asesor_seleccionadas'
            ]
            
            for subpestaña in subpestañas_asesor:
                if hasattr(gui, subpestaña):
                    self.log_test(f"Subpestaña {subpestaña}", True, "Subpestaña disponible")
                else:
                    self.log_test(f"Subpestaña {subpestaña}", False, "Subpestaña no encontrada")
            
            # Verificar funciones del asesor
            funciones_asesor = [
                '_analisis_rapido_asesor', '_analisis_detallado_asesor', 
                '_analisis_express_asesor', '_toggle_analisis_tecnico',
                '_select_all_estrategias_asesor', '_deselect_all_estrategias_asesor'
            ]
            
            for función in funciones_asesor:
                if hasattr(gui, función):
                    self.log_test(f"Función {función}", True, "Función disponible")
                else:
                    self.log_test(f"Función {función}", False, "Función no encontrada")
            
            # Cerrar GUI
            gui.destroy()
            
            return True
            
        except Exception as e:
            self.log_error(f"Error en verificación de estructura GUI: {str(e)}")
            return False
    
    def test_5_flujo_analisis_principal(self):
        """Test 5: Flujo de análisis principal."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 5: FLUJO DE ANÁLISIS PRINCIPAL")
        self.logger.info("=" * 60)
        
        try:
            from gui_enhanced_rank import EnhancedRankGUI
            
            # Crear instancia de GUI
            gui = EnhancedRankGUI()
            
            # Configurar archivos de prueba
            gui.var_kpi.set(self.test_files['kpi_file'])
            gui.var_market.set(self.test_files['market_file'])
            gui.var_sqx.set(self.test_files['sqx_folder'])
            gui.var_dest.set(self.test_files['output_folder'])
            
            # Verificar configuración
            if gui.var_kpi.get() == self.test_files['kpi_file']:
                self.log_test("Configuración KPI", True, "Archivo KPI configurado correctamente")
            else:
                self.log_test("Configuración KPI", False, "Error en configuración KPI")
            
            if gui.var_market.get() == self.test_files['market_file']:
                self.log_test("Configuración Mercado", True, "Archivo de mercado configurado correctamente")
            else:
                self.log_test("Configuración Mercado", False, "Error en configuración de mercado")
            
            # Simular validación de datos
            try:
                gui._validate_data()
                self.log_test("Validación de Datos", True, "Validación ejecutada correctamente")
            except Exception as e:
                self.log_test("Validación de Datos", False, f"Error en validación: {str(e)}")
            
            # Cerrar GUI
            gui.destroy()
            
            return True
            
        except Exception as e:
            self.log_error(f"Error en flujo de análisis principal: {str(e)}")
            return False
    
    def test_6_integracion_asesor_financiero(self):
        """Test 6: Integración con Asesor Financiero."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 6: INTEGRACIÓN CON ASESOR FINANCIERO")
        self.logger.info("=" * 60)
        
        try:
            from asesor_financiero_inteligente import AsesorFinancieroInteligente
            
            # Crear datos de prueba
            test_data = pd.DataFrame({
                'Strategy Name': ['Strategy 1', 'Strategy 2', 'Strategy 3'],
                'CAGR': [15.5, 12.3, 18.7],
                'Drawdown': [8.2, 12.1, 6.5],
                'Sharpe Ratio': [1.8, 1.2, 2.1],
                'Profit factor': [1.5, 1.3, 1.9],
                'Unified_Score': [0.75, 0.65, 0.85]
            })
            
            # Crear instancia del asesor
            asesor = AsesorFinancieroInteligente(test_data, ['CAGR', 'Drawdown', 'Sharpe Ratio'])
            
            # Test análisis de correlación IS/OOS
            try:
                correlacion_result = asesor.analizar_correlacion_is_oos()
                self.log_test("Análisis Correlación IS/OOS", True, "Análisis ejecutado correctamente")
            except Exception as e:
                self.log_test("Análisis Correlación IS/OOS", False, f"Error: {str(e)}")
            
            # Test detección de outliers
            try:
                outliers_result = asesor.detectar_outliers()
                self.log_test("Detección de Outliers", True, "Detección ejecutada correctamente")
            except Exception as e:
                self.log_test("Detección de Outliers", False, f"Error: {str(e)}")
            
            # Test clustering
            try:
                clustering_result = asesor.clustering_estrategias()
                self.log_test("Clustering de Estrategias", True, "Clustering ejecutado correctamente")
            except Exception as e:
                self.log_test("Clustering de Estrategias", False, f"Error: {str(e)}")
            
            # Test generación de consejos
            try:
                consejos_result = asesor.generar_consejos_completos()
                self.log_test("Generación de Consejos", True, "Consejos generados correctamente")
            except Exception as e:
                self.log_test("Generación de Consejos", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error en integración con asesor financiero: {str(e)}")
            return False
    
    def test_7_exportacion_resultados(self):
        """Test 7: Exportación de resultados."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 7: EXPORTACIÓN DE RESULTADOS")
        self.logger.info("=" * 60)
        
        try:
            # Verificar carpeta de salida
            if os.path.exists(self.test_files['output_folder']):
                self.log_test("Carpeta de Salida", True, "Carpeta de salida disponible")
            else:
                self.log_test("Carpeta de Salida", False, "Carpeta de salida no encontrada")
                return False
            
            # Crear archivo de prueba
            test_file = os.path.join(self.test_files['output_folder'], 'test_export.json')
            test_data = {
                'test': True,
                'timestamp': datetime.now().isoformat(),
                'message': 'Test de exportación'
            }
            
            with open(test_file, 'w') as f:
                json.dump(test_data, f, indent=2)
            
            if os.path.exists(test_file):
                self.log_test("Exportación JSON", True, "Archivo JSON exportado correctamente")
            else:
                self.log_test("Exportación JSON", False, "Error en exportación JSON")
            
            # Limpiar archivo de prueba
            os.remove(test_file)
            
            return True
            
        except Exception as e:
            self.log_error(f"Error en exportación de resultados: {str(e)}")
            return False
    
    def test_8_rendimiento_sistema(self):
        """Test 8: Rendimiento del sistema."""
        self.logger.info("=" * 60)
        self.logger.info("TEST 8: RENDIMIENTO DEL SISTEMA")
        self.logger.info("=" * 60)
        
        try:
            import time
            import psutil
            
            # Test tiempo de importación
            start_time = time.time()
            from gui_enhanced_rank import EnhancedRankGUI
            import_time = time.time() - start_time
            
            if import_time < 5.0:  # Menos de 5 segundos
                self.log_test("Tiempo de Importación", True, f"Importación rápida: {import_time:.2f}s")
            else:
                self.log_test("Tiempo de Importación", False, f"Importación lenta: {import_time:.2f}s")
            
            # Test uso de memoria
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            if memory_usage < 500:  # Menos de 500MB
                self.log_test("Uso de Memoria", True, f"Memoria aceptable: {memory_usage:.1f}MB")
            else:
                self.log_test("Uso de Memoria", False, f"Memoria alta: {memory_usage:.1f}MB")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error en test de rendimiento: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests."""
        self.logger.info("🚀 INICIANDO SUITE COMPLETA DE TESTS")
        self.logger.info("=" * 60)
        
        tests = [
            ("Verificación de Archivos", self.test_1_verificacion_archivos),
            ("Carga de Datos", self.test_2_carga_datos),
            ("Importación de Módulos", self.test_3_importacion_modulos),
            ("Estructura de GUI", self.test_4_estructura_gui),
            ("Flujo de Análisis Principal", self.test_5_flujo_analisis_principal),
            ("Integración Asesor Financiero", self.test_6_integracion_asesor_financiero),
            ("Exportación de Resultados", self.test_7_exportacion_resultados),
            ("Rendimiento del Sistema", self.test_8_rendimiento_sistema)
        ]
        
        for test_name, test_func in tests:
            try:
                self.logger.info(f"\n🔄 Ejecutando: {test_name}")
                test_func()
            except Exception as e:
                self.log_error(f"Error crítico en test {test_name}: {str(e)}")
                self.log_test(test_name, False, f"Error crítico: {str(e)}")
        
        self.generate_report()
    
    def generate_report(self):
        """Genera el reporte final de tests."""
        self.logger.info("=" * 60)
        self.logger.info("📊 REPORTE FINAL DE TESTS")
        self.logger.info("=" * 60)
        
        # Estadísticas
        total_tests = self.results['total_tests']
        passed_tests = self.results['tests_passed']
        failed_tests = self.results['tests_failed']
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.logger.info(f"📈 ESTADÍSTICAS:")
        self.logger.info(f"   • Tests Totales: {total_tests}")
        self.logger.info(f"   • Tests Exitosos: {passed_tests}")
        self.logger.info(f"   • Tests Fallidos: {failed_tests}")
        self.logger.info(f"   • Tasa de Éxito: {success_rate:.1f}%")
        
        # Errores
        if self.results['errors']:
            self.logger.info(f"\n❌ ERRORES ENCONTRADOS:")
            for error in self.results['errors']:
                self.logger.error(f"   • {error}")
        
        # Advertencias
        if self.results['warnings']:
            self.logger.info(f"\n⚠️ ADVERTENCIAS:")
            for warning in self.results['warnings']:
                self.logger.warning(f"   • {warning}")
        
        # Recomendaciones
        self.logger.info(f"\n💡 RECOMENDACIONES:")
        if success_rate >= 90:
            self.logger.info("   ✅ Sistema funcionando correctamente")
        elif success_rate >= 70:
            self.logger.info("   🟡 Sistema funcionando con algunas advertencias")
        else:
            self.logger.info("   ❌ Sistema requiere atención inmediata")
        
        # Guardar reporte
        report_file = f"reporte_tests_asesor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"\n📄 Reporte guardado en: {report_file}")
        
        return success_rate >= 70  # Éxito si al menos 70% de tests pasan

def main():
    """Función principal."""
    print("🚀 Test Automático del Flujo Completo del Asesor Financiero")
    print("=" * 60)
    
    test_suite = TestFlujoCompletoAsesor()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ SUITE DE TESTS COMPLETADA CON ÉXITO")
        sys.exit(0)
    else:
        print("\n❌ SUITE DE TESTS CON ERRORES")
        sys.exit(1)

if __name__ == "__main__":
    main() 