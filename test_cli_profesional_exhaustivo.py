#!/usr/bin/env python3
"""
Test CLI Profesional Exhaustivo - Auditoría Completa del Sistema
Nivel: PROFESIONAL - Auditoría completa del flujo de trabajo GUI
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import time
import json
import traceback
from typing import Dict, List, Any, Optional, Tuple

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui_enhanced_rank import EnhancedRankGUI
from data_manager import DataManager
from src.core.integration_layer import FactorKElite96Enhanced, UnifiedEvaluatorEnhanced, ConfigManagerEnhanced
from asesor_financiero_inteligente import AsesorFinancieroInteligente

def setup_logging():
    """Configurar logging detallado para auditoría profesional"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"test_cli_profesional_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return log_file

class AuditoriaProfesionalCLI:
    """Auditoría profesional exhaustiva del sistema completo"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results = {
            'tests_passed': 0,
            'tests_failed': 0,
            'errors': [],
            'warnings': [],
            'performance': {},
            'auditoria_core': {},
            'configuracion_gui': {},
            'flujo_datos': {},
            'poblacion_pestanas': {},
            'integracion_cientifica': {}
        }
        
        # Componentes del sistema
        self.gui = None
        self.data_manager = None
        self.factor_k_engine = None
        self.unified_evaluator = None
        self.config_manager = None
        self.asesor = None
        
        # Datos de auditoría
        self.datos_originales = None
        self.datos_procesados = None
        self.configuracion_inicial = {}
        self.configuracion_final = {}
        
    def log_section(self, title: str):
        """Log de sección con formato profesional"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🧪 AUDITORÍA: {title}")
        self.logger.info(f"{'='*80}")
        
    def log_test(self, test_name: str, success: bool = True, details: str = ""):
        """Log de test con formato profesional"""
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        self.logger.info(f"{status} - {test_name}")
        if details:
            self.logger.info(f"   📝 {details}")
        
        if success:
            self.results['tests_passed'] += 1
        else:
            self.results['tests_failed'] += 1
            self.results['errors'].append(f"{test_name}: {details}")
    
    def test_1_auditoria_core_engine(self):
        """Test 1: Auditoría completa del Core Engine"""
        self.log_section("AUDITORÍA CORE ENGINE")
        
        try:
            # 1.1 Auditoría de componentes del Core Engine
            self.logger.info("Auditoría de componentes del Core Engine...")
            
            # Verificar que todos los componentes están disponibles
            componentes_core = {
                'FactorKElite96Enhanced': self.factor_k_engine,
                'UnifiedEvaluatorEnhanced': self.unified_evaluator,
                'ConfigManagerEnhanced': self.config_manager
            }
            
            for nombre, componente in componentes_core.items():
                if componente is not None:
                    self.log_test(f"Componente {nombre}", True, f"Componente disponible")
                else:
                    self.log_test(f"Componente {nombre}", False, f"Componente no disponible")
            
            # 1.2 Auditoría de configuración científica
            self.logger.info("Auditoría de configuración científica...")
            
            if self.factor_k_engine:
                # Verificar estado inicial de mejoras científicas
                estado_inicial = getattr(self.factor_k_engine, 'scientific_improvements_enabled', False)
                self.log_test("Estado Inicial Mejoras Científicas", True, f"Estado: {estado_inicial}")
                
                # Activar mejoras científicas
                if hasattr(self.factor_k_engine, 'enable_scientific_improvements'):
                    self.factor_k_engine.enable_scientific_improvements()
                    estado_final = getattr(self.factor_k_engine, 'scientific_improvements_enabled', False)
                    self.log_test("Activación Mejoras Científicas", estado_final, f"Estado final: {estado_final}")
                    
                    # Verificar componentes científicos habilitados
                    componentes_cientificos = [
                        'hmm_analyzer',
                        'scientific_improvements_enabled',
                        '_detect_market_regimes',
                        '_apply_hmm_analysis'
                    ]
                    
                    for componente in componentes_cientificos:
                        disponible = hasattr(self.factor_k_engine, componente)
                        self.log_test(f"Componente Científico {componente}", disponible, 
                                    f"Disponible: {disponible}")
                else:
                    self.log_test("Método enable_scientific_improvements", False, "Método no disponible")
            
            # 1.3 Auditoría de métodos de análisis
            self.logger.info("Auditoría de métodos de análisis...")
            
            if self.factor_k_engine:
                metodos_analisis = [
                    'evaluate_strategies',
                    '_validate_input_data',
                    '_calculate_factor_k_elite',
                    '_apply_scientific_improvements',
                    '_assign_quality_categories'
                ]
                
                for metodo in metodos_analisis:
                    disponible = hasattr(self.factor_k_engine, metodo)
                    self.log_test(f"Método {metodo}", disponible, f"Disponible: {disponible}")
            
            return True
            
        except Exception as e:
            self.log_test("Auditoría Core Engine", False, f"Error: {str(e)}")
            return False
    
    def test_2_configuracion_dinamica_gui(self):
        """Test 2: Auditoría de configuración dinámica de la GUI"""
        self.log_section("CONFIGURACIÓN DINÁMICA GUI")
        
        try:
            # 2.1 Auditoría de variables de configuración
            self.logger.info("Auditoría de variables de configuración...")
            
            if self.gui:
                # Verificar variables de configuración principales
                variables_config = [
                    'var_style', 'var_alpha', 'var_top_n', 'var_kpi',
                    'var_strategies', 'var_market', 'var_output'
                ]
                
                for var in variables_config:
                    if hasattr(self.gui, var):
                        valor = getattr(self.gui, var).get()
                        self.log_test(f"Variable {var}", True, f"Valor: {valor}")
                    else:
                        self.log_test(f"Variable {var}", False, "Variable no encontrada")
                
                # 2.2 Auditoría de estilos de trading
                self.logger.info("Auditoría de estilos de trading...")
                
                estilos_trading = ['CONSERVADOR', 'MODERADO', 'AGRESIVO']
                for estilo in estilos_trading:
                    # Simular cambio de estilo
                    if hasattr(self.gui, 'var_style'):
                        self.gui.var_style.set(estilo)
                        valor_actual = self.gui.var_style.get()
                        self.log_test(f"Estilo {estilo}", valor_actual == estilo, 
                                    f"Configurado: {valor_actual}")
                
                # 2.3 Auditoría de configuración de alpha
                self.logger.info("Auditoría de configuración de alpha...")
                
                valores_alpha = [10, 20, 30, 40, 50]
                for alpha in valores_alpha:
                    if hasattr(self.gui, 'var_alpha'):
                        self.gui.var_alpha.set(alpha)
                        valor_actual = self.gui.var_alpha.get()
                        self.log_test(f"Alpha {alpha}", valor_actual == alpha, 
                                    f"Configurado: {valor_actual}")
                
                # 2.4 Auditoría de configuración de Top N
                self.logger.info("Auditoría de configuración de Top N...")
                
                valores_top_n = [5, 10, 15, 20, 25]
                for top_n in valores_top_n:
                    if hasattr(self.gui, 'var_top_n'):
                        self.gui.var_top_n.set(top_n)
                        valor_actual = self.gui.var_top_n.get()
                        self.log_test(f"Top N {top_n}", valor_actual == top_n, 
                                    f"Configurado: {valor_actual}")
            
            return True
            
        except Exception as e:
            self.log_test("Configuración Dinámica GUI", False, f"Error: {str(e)}")
            return False
    
    def test_3_flujo_datos_completo(self):
        """Test 3: Auditoría del flujo de datos completo"""
        self.log_section("FLUJO DE DATOS COMPLETO")
        
        try:
            # 3.1 Auditoría de carga de datos
            self.logger.info("Auditoría de carga de datos...")
            
            if self.data_manager:
                # Cargar datos reales
                kpis_data = self.data_manager.kpis_data
                market_data = self.data_manager.market_data
                
                self.log_test("Carga KPIs", kpis_data is not None and len(kpis_data) > 0,
                            f"Registros: {len(kpis_data) if kpis_data is not None else 0}")
                
                self.log_test("Carga Mercado", market_data is not None and len(market_data) > 0,
                            f"Registros: {len(market_data) if market_data is not None else 0}")
                
                # Guardar datos originales para auditoría
                self.datos_originales = {
                    'kpis': kpis_data.copy() if kpis_data is not None else None,
                    'market': market_data.copy() if market_data is not None else None
                }
            
            # 3.2 Auditoría de procesamiento de datos
            self.logger.info("Auditoría de procesamiento de datos...")
            
            if self.unified_evaluator and self.datos_originales and self.datos_originales['kpis'] is not None:
                # Procesar datos con el evaluador unificado (que incluye mejoras científicas)
                datos_procesados = self.unified_evaluator.evaluate_strategies_unified(self.datos_originales['kpis'])
                
                self.log_test("Procesamiento Datos", datos_procesados is not None and len(datos_procesados) > 0,
                            f"Registros procesados: {len(datos_procesados) if datos_procesados is not None else 0}")
                
                # Guardar datos procesados
                self.datos_procesados = datos_procesados
                
                # 3.3 Auditoría de columnas generadas
                self.logger.info("Auditoría de columnas generadas...")
                
                if datos_procesados is not None:
                    columnas_originales = set(self.datos_originales['kpis'].columns)
                    columnas_procesadas = set(datos_procesados.columns)
                    columnas_nuevas = columnas_procesadas - columnas_originales
                    
                    self.log_test("Generación Columnas", len(columnas_nuevas) > 0,
                                f"Columnas nuevas: {len(columnas_nuevas)}")
                    
                    # Verificar columnas científicas específicas
                    columnas_cientificas = [
                        'FK96_Elite_Enhanced', 'FK96_Stability_Enhanced', 'FK96_Growth_Enhanced',
                        'FK96_Efficiency_Enhanced', 'FK96_Consistency_Enhanced', 'FK96_Risk_Enhanced',
                        'Quality_Category', 'Market_Regime', 'Regime_Score'
                    ]
                    
                    columnas_encontradas = [col for col in columnas_cientificas if col in datos_procesados.columns]
                    self.log_test("Columnas Científicas", len(columnas_encontradas) >= 3,
                                f"Encontradas: {len(columnas_encontradas)}")
                    
                    for col in columnas_encontradas:
                        self.log_test(f"Columna {col}", True, f"Presente en resultados")
                    
                    # 3.3.1 Auditoría específica de nuevas columnas científicas
                    self.logger.info("Auditoría específica de columnas científicas mejoradas...")
                    
                    nuevas_columnas_cientificas = [
                        'Unified_Score_Scientific', 'Unified_Score_Enhanced',
                        'HMM_State', 'HMM_Score'
                    ]
                    
                    nuevas_encontradas = []
                    for col in nuevas_columnas_cientificas:
                        if datos_procesados is not None and col in datos_procesados.columns:
                            nuevas_encontradas.append(col)
                            # Verificar que tiene datos válidos
                            datos_validos = datos_procesados[col].notna().sum()
                            self.log_test(f"Nueva Columna {col}", datos_validos > 0,
                                        f"Datos válidos: {datos_validos}")
                    
                    self.log_test("Nuevas Columnas Científicas", len(nuevas_encontradas) > 0,
                                f"Encontradas: {len(nuevas_encontradas)}")
                    
                    # 3.3.2 Verificar mejora del Unified_Score
                    if datos_procesados is not None and 'Unified_Score_Scientific' in datos_procesados.columns:
                        original_scores = datos_procesados['Unified_Score'].describe()
                        scientific_scores = datos_procesados['Unified_Score_Scientific'].describe()
                        
                        self.logger.info(f"Unified_Score original - Media: {original_scores['mean']:.4f}")
                        self.logger.info(f"Unified_Score científico - Media: {scientific_scores['mean']:.4f}")
                        
                        # Verificar que hay diferencias significativas
                        score_diff = abs(original_scores['mean'] - scientific_scores['mean'])
                        self.log_test("Mejora Unified_Score", score_diff > 0.001, 
                                    f"Diferencia en scores: {score_diff:.4f}")
                    
                    # 3.3.3 Verificar regímenes de mercado
                    if datos_procesados is not None and 'Market_Regime' in datos_procesados.columns:
                        regímenes = datos_procesados['Market_Regime'].value_counts()
                        self.log_test("Regímenes de Mercado", len(regímenes) >= 2,
                                    f"Regímenes detectados: {len(regímenes)}")
                        
                        for regime in regímenes.index:
                            count = regímenes[regime]
                            self.log_test(f"Régimen {regime}", count > 0, f"Estrategias: {count}")
            
            return True
            
        except Exception as e:
            self.log_test("Flujo Datos Completo", False, f"Error: {str(e)}")
            return False
    
    def test_4_poblacion_pestanas_gui(self):
        """Test 4: Auditoría de población de pestañas de la GUI"""
        self.log_section("POBLACIÓN PESTAÑAS GUI")
        
        try:
            # 4.1 Auditoría de pestañas principales
            self.logger.info("Auditoría de pestañas principales...")
            
            if self.gui:
                pestañas_principales = [
                    'tab_files', 'tab_analysis', 'tab_results', 'tab_summary',
                    'tab_asesor', 'tab_help'
                ]
                
                for pestaña in pestañas_principales:
                    if hasattr(self.gui, pestaña):
                        self.log_test(f"Pestaña {pestaña}", True, "Pestaña disponible")
                    else:
                        self.log_test(f"Pestaña {pestaña}", False, "Pestaña no encontrada")
                
                # 4.2 Auditoría de subpestañas del asesor
                self.logger.info("Auditoría de subpestañas del asesor...")
                
                subpestañas_asesor = [
                    'tab_asesor_analisis', 'tab_asesor_cientifico', 
                    'tab_asesor_empirico', 'tab_asesor_seleccionadas'
                ]
                
                for subpestaña in subpestañas_asesor:
                    if hasattr(self.gui, subpestaña):
                        self.log_test(f"Subpestaña {subpestaña}", True, "Subpestaña disponible")
                    else:
                        self.log_test(f"Subpestaña {subpestaña}", False, "Subpestaña no encontrada")
                
                # 4.3 Auditoría de widgets de datos
                self.logger.info("Auditoría de widgets de datos...")
                
                # Los widgets se crean dinámicamente después del análisis
                # Verificar que los métodos de creación existen
                metodos_creacion = [
                    '_display_results', '_build_results_table', '_build_asesor_seleccionadas_tab'
                ]
                
                for metodo in metodos_creacion:
                    if hasattr(self.gui, metodo):
                        self.log_test(f"Método {metodo}", True, "Método disponible")
                    else:
                        self.log_test(f"Método {metodo}", False, "Método no encontrado")
                
                # Verificar widgets que deberían existir después de la inicialización
                widgets_basicos = [
                    'notebook', 'tab_config', 'tab_results', 'tab_asesor'
                ]
                
                for widget in widgets_basicos:
                    if hasattr(self.gui, widget):
                        self.log_test(f"Widget {widget}", True, "Widget disponible")
                    else:
                        self.log_test(f"Widget {widget}", False, "Widget no encontrado")
            
            return True
            
        except Exception as e:
            self.log_test("Población Pestañas GUI", False, f"Error: {str(e)}")
            return False
    
    def test_5_integracion_cientifica_avanzada(self):
        """Test 5: Auditoría de integración científica avanzada"""
        self.log_section("INTEGRACIÓN CIENTÍFICA AVANZADA")
        
        try:
            # 5.1 Auditoría de métricas científicas en resultados
            self.logger.info("Auditoría de métricas científicas en resultados...")
            
            if self.datos_procesados is not None:
                # Verificar métricas científicas específicas
                metricas_cientificas = {
                    'FK96_Elite_Enhanced': 'Factor K Elite',
                    'FK96_Stability_Enhanced': 'Estabilidad',
                    'FK96_Growth_Enhanced': 'Crecimiento',
                    'FK96_Efficiency_Enhanced': 'Eficiencia',
                    'FK96_Consistency_Enhanced': 'Consistencia',
                    'FK96_Risk_Enhanced': 'Riesgo',
                    'Market_Regime': 'Régimen de Mercado',
                    'Regime_Score': 'Score de Régimen',
                    'Quality_Category': 'Categoría de Calidad'
                }
                
                metricas_encontradas = 0
                for columna, descripcion in metricas_cientificas.items():
                    if columna in self.datos_procesados.columns:
                        metricas_encontradas += 1
                        # Verificar que la columna tiene datos válidos
                        datos_validos = self.datos_procesados[columna].notna().sum()
                        self.log_test(f"Métrica {descripcion}", datos_validos > 0,
                                    f"Datos válidos: {datos_validos}")
                
                self.log_test("Total Métricas Científicas", metricas_encontradas >= 5,
                            f"Encontradas: {metricas_encontradas}")
                
                # 5.2 Auditoría de mejora de cálculos
                self.logger.info("Auditoría de mejora de cálculos...")
                
                if self.datos_originales and self.datos_procesados is not None and self.datos_originales['kpis'] is not None:
                    # Comparar estadísticas antes y después
                    if 'Unified_Score' in self.datos_originales['kpis'].columns:
                        score_original = self.datos_originales['kpis']['Unified_Score'].mean()
                        if 'FK96_Elite_Enhanced' in self.datos_procesados.columns:
                            score_mejorado = self.datos_procesados['FK96_Elite_Enhanced'].mean()
                            
                            mejora = abs(score_mejorado - score_original) > 0.01
                            self.log_test("Mejora de Cálculos", mejora,
                                        f"Score original: {score_original:.4f}, Score mejorado: {score_mejorado:.4f}")
                
                # 5.3 Auditoría de categorización de calidad
                self.logger.info("Auditoría de categorización de calidad...")
                
                if 'Quality_Category' in self.datos_procesados.columns:
                    categorias = self.datos_procesados['Quality_Category'].value_counts()
                    categorias_validas = ['Excelente', 'Muy Bueno', 'Bueno', 'Regular', 'Pobre']
                    
                    categorias_encontradas = [cat for cat in categorias_validas if cat in categorias.index]
                    self.log_test("Categorización Calidad", len(categorias_encontradas) >= 3,
                                f"Categorías encontradas: {len(categorias_encontradas)}")
                    
                    for categoria in categorias_encontradas:
                        count = categorias.get(categoria, 0)
                        self.log_test(f"Categoría {categoria}", count > 0, f"Estrategias: {count}")
            
            return True
            
        except Exception as e:
            self.log_test("Integración Científica Avanzada", False, f"Error: {str(e)}")
            return False
    
    def test_6_rendimiento_y_estabilidad_profesional(self):
        """Test 6: Auditoría de rendimiento y estabilidad profesional"""
        self.log_section("RENDIMIENTO Y ESTABILIDAD PROFESIONAL")
        
        try:
            # 6.1 Auditoría de tiempo de respuesta
            self.logger.info("Auditoría de tiempo de respuesta...")
            
            start_time = time.time()
            
            # Simular operaciones intensivas
            for i in range(10):
                if self.factor_k_engine and self.datos_originales and self.datos_originales['kpis'] is not None:
                    # Procesar una muestra de datos
                    muestra = self.datos_originales['kpis'].sample(min(10, len(self.datos_originales['kpis'])))
                    self.factor_k_engine.evaluate_strategies(muestra)
            
            total_time = time.time() - start_time
            
            self.log_test("Tiempo Respuesta", total_time < 5.0,
                        f"Tiempo total: {total_time:.2f}s")
            
            # 6.2 Auditoría de uso de memoria
            self.logger.info("Auditoría de uso de memoria...")
            
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            self.log_test("Uso Memoria", memory_usage < 500,
                        f"Memoria: {memory_usage:.1f}MB")
            
            # 6.3 Auditoría de manejo de errores
            self.logger.info("Auditoría de manejo de errores...")
            
            # Simular errores controlados
            try:
                # Intentar procesar datos inválidos
                datos_invalidos = pd.DataFrame({'columna_invalida': [1, 2, 3]})
                if self.factor_k_engine:
                    self.factor_k_engine.evaluate_strategies(datos_invalidos)
                self.log_test("Manejo Errores Datos Inválidos", False, "Debería fallar")
            except Exception as e:
                self.log_test("Manejo Errores Datos Inválidos", True, f"Error capturado: {str(e)[:50]}")
            
            # 6.4 Auditoría de consistencia de datos
            self.logger.info("Auditoría de consistencia de datos...")
            
            if self.datos_procesados is not None:
                # Verificar que no hay valores infinitos
                infinitos = np.isinf(self.datos_procesados.select_dtypes(include=[np.number])).sum().sum()
                self.log_test("Consistencia Datos", infinitos == 0,
                            f"Valores infinitos: {infinitos}")
                
                # Verificar que no hay valores NaN excesivos
                nans = self.datos_procesados.isnull().sum().sum()
                total_celdas = self.datos_procesados.size
                porcentaje_nans = (nans / total_celdas) * 100
                
                self.log_test("Calidad Datos", porcentaje_nans < 10,
                            f"Porcentaje NaN: {porcentaje_nans:.1f}%")
            
            return True
            
        except Exception as e:
            self.log_test("Rendimiento Estabilidad Profesional", False, f"Error: {str(e)}")
            return False
    
    def inicializar_componentes(self):
        """Inicializar todos los componentes del sistema"""
        try:
            # Inicializar GUI
            self.logger.info("Inicializando GUI...")
            self.gui = EnhancedRankGUI()
            self.log_test("Inicialización GUI", True, "GUI creada exitosamente")
            
            # Inicializar DataManager
            self.logger.info("Inicializando DataManager...")
            self.data_manager = DataManager()
            self.log_test("Inicialización DataManager", True, "DataManager creado exitosamente")
            
            # Inicializar componentes del Core Engine
            self.logger.info("Inicializando componentes del Core Engine...")
            self.factor_k_engine = FactorKElite96Enhanced()
            self.unified_evaluator = UnifiedEvaluatorEnhanced()
            self.config_manager = ConfigManagerEnhanced()
            self.log_test("Inicialización Core Engine", True, "Componentes del Core Engine creados exitosamente")
            
            # Inicializar Asesor Financiero
            self.logger.info("Inicializando Asesor Financiero...")
            self.asesor = AsesorFinancieroInteligente()
            self.log_test("Inicialización Asesor", True, "Asesor creado exitosamente")
            
            return True
            
        except Exception as e:
            self.log_test("Inicialización Componentes", False, f"Error: {str(e)}")
            return False
    
    def run_auditoria_completa(self):
        """Ejecutar auditoría completa del sistema"""
        print("🚀 INICIANDO AUDITORÍA PROFESIONAL EXHAUSTIVA")
        print("="*80)
        
        log_file = setup_logging()
        
        # Inicializar componentes
        if not self.inicializar_componentes():
            return False
        
        # Ejecutar todos los tests de auditoría
        tests = [
            self.test_1_auditoria_core_engine,
            self.test_2_configuracion_dinamica_gui,
            self.test_3_flujo_datos_completo,
            self.test_4_poblacion_pestanas_gui,
            self.test_5_integracion_cientifica_avanzada,
            self.test_6_rendimiento_y_estabilidad_profesional
        ]
        
        start_time = time.time()
        
        for test in tests:
            try:
                success = test()
                if not success:
                    self.logger.error(f"Test {test.__name__} falló")
            except Exception as e:
                self.logger.error(f"Error ejecutando test {test.__name__}: {str(e)}")
                self.results['errors'].append(f"{test.__name__}: {str(e)}")
        
        total_time = time.time() - start_time
        
        # Resumen final profesional
        self.print_resumen_profesional(total_time, log_file)
        
        return self.results['tests_failed'] == 0
    
    def print_resumen_profesional(self, total_time: float, log_file: str):
        """Imprimir resumen final profesional"""
        print("\n" + "="*80)
        print("📊 RESUMEN FINAL - AUDITORÍA PROFESIONAL EXHAUSTIVA")
        print("="*80)
        
        print(f"⏱️  Tiempo total de auditoría: {total_time:.2f} segundos")
        print(f"✅ Tests pasados: {self.results['tests_passed']}")
        print(f"❌ Tests fallidos: {self.results['tests_failed']}")
        print(f"⚠️  Advertencias: {len(self.results['warnings'])}")
        print(f"🚨 Errores: {len(self.results['errors'])}")
        
        if self.results['errors']:
            print("\n🚨 ERRORES DETECTADOS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        if self.results['warnings']:
            print("\n⚠️  ADVERTENCIAS:")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
        
        print("\n🎯 RECOMENDACIONES PROFESIONALES:")
        if self.results['tests_failed'] == 0:
            print("   ✅ Sistema completamente funcional - Auditoría exitosa")
            print("   🏆 Nivel profesional alcanzado")
        else:
            print("   🔧 Revisar errores detectados antes de continuar")
            print("   📝 Verificar logs para detalles específicos")
            print("   ⚠️  Sistema requiere correcciones antes de producción")
        
        print("\n📁 ARCHIVOS GENERADOS:")
        print(f"   • Log detallado: {log_file}")
        print(f"   • Resumen: test_cli_profesional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Guardar resultados en JSON
        results_file = f"test_cli_profesional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {results_file}")

if __name__ == "__main__":
    auditoria = AuditoriaProfesionalCLI()
    success = auditoria.run_auditoria_completa()
    sys.exit(0 if success else 1) 