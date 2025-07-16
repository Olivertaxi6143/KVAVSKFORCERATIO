"""
Configuración común para todos los tests
Fixtures y configuración compartida para la batería de tests
"""

import pytest
import pandas as pd
import numpy as np
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
import tkinter as tk
from datetime import datetime

# Configurar logging para tests
def setup_test_logging():
    """Configura logging detallado para tests."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Crear nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/test_execution_{timestamp}.log"
    
    # Configurar logger raíz
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # También mostrar en consola
        ]
    )
    
    # Configurar logger específico para tests
    test_logger = logging.getLogger('tests')
    test_logger.setLevel(logging.DEBUG)
    
    # Configurar loggers específicos para componentes GUI
    gui_loggers = [
        'src.gui.interactive_charts',
        'src.gui.strategy_comparison', 
        'src.gui.advanced_export',
        'src.gui.advanced_filters_popup'
    ]
    
    for logger_name in gui_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    return log_file

# Llamar setup al inicio
test_log_file = setup_test_logging()

logger = logging.getLogger(__name__)

class TkWidgetMock(MagicMock):
    """Mock profesional para widgets de Tkinter."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Métodos de layout
        self.pack = MagicMock(return_value=None)
        self.grid = MagicMock(return_value=None)
        self.place = MagicMock(return_value=None)
        self.forget = MagicMock(return_value=None)
        self.grid_forget = MagicMock(return_value=None)
        self.pack_forget = MagicMock(return_value=None)
        # Métodos de configuración
        self.configure = MagicMock(return_value=None)
        self.config = MagicMock(return_value=None)
        self.cget = MagicMock(return_value="")
        # Métodos de información
        self.winfo_width = MagicMock(return_value=800)
        self.winfo_height = MagicMock(return_value=600)
        self.winfo_x = MagicMock(return_value=0)
        self.winfo_y = MagicMock(return_value=0)
        self.winfo_rootx = MagicMock(return_value=0)
        self.winfo_rooty = MagicMock(return_value=0)
        self.winfo_children = MagicMock(return_value=[])
        self.winfo_toplevel = MagicMock(return_value=self)
        # Métodos de eventos
        self.bind = MagicMock(return_value=None)
        self.unbind = MagicMock(return_value=None)
        self.after = MagicMock(return_value=None)
        self.after_cancel = MagicMock(return_value=None)
        self.update = MagicMock(return_value=None)
        self.update_idletasks = MagicMock(return_value=None)
        self.mainloop = MagicMock(return_value=None)
        self.quit = MagicMock(return_value=None)
        self.protocol = MagicMock(return_value=None)
        # Métodos de lista y acceso
        self.__len__ = lambda s: 0
        self.__getitem__ = lambda s, k: None
        # Otros atributos
        self._last_child_ids = {}
        self._w = "mock_root"
        self.children = {}
        self.master = None
        self.tk = MagicMock()
        self.tk.eval = MagicMock(return_value="")
        self.tk.call = MagicMock(return_value="")
        self.tk.winfo_toplevel = MagicMock(return_value=self)
        self.state = MagicMock(return_value='normal')
        self.title = MagicMock(return_value=None)
        self.geometry = MagicMock(return_value=None)
        self.resizable = MagicMock(return_value=None)
        self.transient = MagicMock(return_value=None)
        self.grab_set = MagicMock(return_value=None)
        self.destroy = MagicMock(return_value=None)

@pytest.fixture(scope="session")
def mock_tkinter_parent():
    """Mock profesional de ventana padre para tests de GUI."""
    logger.info("🧪 Creando mock profesional de ventana Tkinter")
    mock = TkWidgetMock()
    logger.info("✅ Mock profesional de Tkinter creado correctamente")
    return mock

@pytest.fixture(scope="session")
def temp_test_dir():
    """Directorio temporal para tests de archivos."""
    logger.info("🧪 Creando directorio temporal para tests")
    
    temp_dir = tempfile.mkdtemp(prefix="kvavsk_test_")
    logger.info(f"✅ Directorio temporal creado: {temp_dir}")
    
    yield temp_dir
    
    # Limpiar después de los tests
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    logger.info(f"🧹 Directorio temporal eliminado: {temp_dir}")

@pytest.fixture(scope="session")
def test_config():
    """Configuración de prueba para análisis."""
    logger.info("🧪 Creando configuración de prueba")
    
    config = {
        "trading_style": "Swing Trading",
        "alpha": 0.8,
        "top_n": 20,
        "percentil": 80,
        "scientific_improvements": True,
        "selected_kpis": {
            "CAGR": {"enabled": True, "weight": 1.0},
            "Sharpe_Ratio": {"enabled": True, "weight": 1.0},
            "Max_Drawdown": {"enabled": True, "weight": 1.0},
            "Profit_Factor": {"enabled": True, "weight": 1.0},
            "Total_Trades": {"enabled": True, "weight": 0.8},
            "Win_Rate": {"enabled": True, "weight": 0.9},
            "Recovery_Factor": {"enabled": True, "weight": 0.7},
            "Risk_Reward_Ratio": {"enabled": True, "weight": 0.8}
        },
        "ml_components": {
            "random_forest": True,
            "isolation_forest": True,
            "kmeans": True
        },
        "penalties": {
            "consecutive_losses": {"enabled": True, "threshold": 5},
            "stagnation": {"enabled": True, "threshold": 10},
            "oos_robustness": {"enabled": True, "min_correlation": 0.5},
            "overfitting": {"enabled": True, "contamination": 0.1}
        }
    }
    
    logger.info("✅ Configuración de prueba creada")
    return config

@pytest.fixture(scope="session")
def sample_portfolio_data():
    """Datos de ejemplo de portafolio para testing."""
    logger.info("🧪 Creando datos de ejemplo de portafolio")
    
    portfolio_data = pd.DataFrame({
        'Portfolio_Name': ['Conservative', 'Balanced', 'Aggressive', 'Elite_Only'],
        'Net_Profit': [45000, 78000, 120000, 95000],
        'Calmar_Ratio': [2.8, 3.2, 2.1, 4.5],
        'Sharpe_Ratio': [1.6, 1.9, 1.4, 2.3],
        'Max_Drawdown': [0.12, 0.15, 0.22, 0.08],
        'CAGR': [0.18, 0.22, 0.28, 0.25],
        'Num_Strategies': [8, 12, 15, 6],
        'Diversification_Score': [0.75, 0.85, 0.70, 0.90]
    })
    
    logger.info(f"✅ Datos de portafolio creados: {len(portfolio_data)} portafolios")
    return portfolio_data

@pytest.fixture(scope="session")
def sample_strategies_data():
    """Datos de ejemplo de estrategias para testing."""
    logger.info("🧪 Creando datos de ejemplo de estrategias")
    
    strategies_data = pd.DataFrame({
        'Strategy_Name': [
            'Elite_Strategy_01', 'Excellent_Strategy_02', 'Very_Good_Strategy_03',
            'Good_Strategy_04', 'Average_Strategy_05', 'Below_Average_Strategy_06',
            'Poor_Strategy_07', 'Very_Poor_Strategy_08', 'Elite_Strategy_09',
            'Excellent_Strategy_10'
        ],
        'Factor_K': [9.5, 8.8, 7.9, 6.8, 5.2, 4.1, 3.2, 2.1, 9.3, 8.5],
        'CAGR': [0.25, 0.22, 0.18, 0.15, 0.12, 0.08, 0.05, 0.02, 0.24, 0.21],
        'Sharpe_Ratio': [2.1, 1.9, 1.6, 1.4, 1.1, 0.8, 0.5, 0.2, 2.0, 1.8],
        'Max_Drawdown': [0.08, 0.10, 0.12, 0.15, 0.18, 0.22, 0.25, 0.30, 0.09, 0.11],
        'Profit_Factor': [2.8, 2.5, 2.2, 1.9, 1.6, 1.3, 1.1, 0.8, 2.7, 2.4],
        'Total_Trades': [150, 180, 200, 220, 250, 280, 300, 320, 160, 170],
        'Win_Rate': [0.75, 0.72, 0.68, 0.65, 0.60, 0.55, 0.50, 0.45, 0.74, 0.71],
        'Recovery_Factor': [3.2, 2.8, 2.4, 2.0, 1.6, 1.2, 0.8, 0.4, 3.1, 2.9],
        'Risk_Reward_Ratio': [2.5, 2.3, 2.0, 1.8, 1.5, 1.2, 0.9, 0.6, 2.4, 2.2],
        'Category': [
            'Elite', 'Excellent', 'Very Good', 'Good', 'Average',
            'Below Average', 'Poor', 'Very Poor', 'Elite', 'Excellent'
        ],
        'Market_Regime': [
            'Bull', 'Sideways', 'Bear', 'Crisis', 'Bull',
            'Sideways', 'Bear', 'Crisis', 'Bull', 'Sideways'
        ],
        'QVA_Score': [9.2, 8.5, 7.8, 6.9, 5.8, 4.5, 3.2, 2.1, 9.1, 8.3],
        'Unified_Score': [9.4, 8.7, 7.9, 6.8, 5.5, 4.2, 3.0, 1.8, 9.3, 8.6]
    })
    
    logger.info(f"✅ Datos de estrategias creados: {len(strategies_data)} estrategias")
    return strategies_data

def pytest_configure(config):
    """Configuración adicional de pytest."""
    logger.info("🚀 Configurando batería de tests comprehensiva")
    
    # Añadir marcadores personalizados
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "gui: marks tests as GUI tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "ml: marks tests as machine learning tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modificar items de colección de tests."""
    logger.info(f"📋 Coleccionando {len(items)} tests")
    
    for item in items:
        # Marcar tests de GUI automáticamente
        if "gui" in item.nodeid.lower() or "window" in item.nodeid.lower():
            item.add_marker(pytest.mark.gui)
        
        # Marcar tests de integración automáticamente
        if "integration" in item.nodeid.lower() or "workflow" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Marcar tests de performance automáticamente
        if "performance" in item.nodeid.lower() or "stress" in item.nodeid.lower():
            item.add_marker(pytest.mark.performance)
        
        # Marcar tests de ML automáticamente
        if "ml" in item.nodeid.lower() or "predict" in item.nodeid.lower():
            item.add_marker(pytest.mark.ml)

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Resumen personalizado al final de los tests."""
    logger.info("📊 Generando resumen de tests")
    
    # Estadísticas básicas
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    errors = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    
    total = passed + failed + errors + skipped
    
    logger.info(f"✅ Tests pasados: {passed}")
    logger.info(f"❌ Tests fallidos: {failed}")
    logger.info(f"💥 Tests con errores: {errors}")
    logger.info(f"⏭️ Tests omitidos: {skipped}")
    logger.info(f"📈 Total de tests: {total}")
    
    if total > 0:
        success_rate = (passed / total) * 100
        logger.info(f"🎯 Tasa de éxito: {success_rate:.1f}%")
    
    if exitstatus == 0:
        logger.info("🎉 ¡Todos los tests pasaron exitosamente!")
    else:
        logger.warning("⚠️ Algunos tests fallaron - revisar errores")

def pytest_runtest_logreport(report):
    """Log de resultados de cada test."""
    logger = logging.getLogger('tests')
    
    if report.when == 'call':
        if report.passed:
            logger.info(f"✅ {report.nodeid} - PASÓ")
        elif report.failed:
            logger.error(f"❌ {report.nodeid} - FALLÓ")
            if report.longrepr:
                logger.error(f"Detalles del error:\n{report.longrepr}")
        elif report.skipped:
            logger.warning(f"⏭️ {report.nodeid} - OMITIDO")
    
    elif report.when == 'setup':
        logger.debug(f"🔧 Configurando: {report.nodeid}")
    
    elif report.when == 'teardown':
        logger.debug(f"🧹 Limpiando: {report.nodeid}")

def pytest_sessionfinish(session, exitstatus):
    """Resumen final de la sesión de tests."""
    logger = logging.getLogger('tests')
    
    logger.info("=" * 60)
    logger.info("📊 RESUMEN FINAL DE TESTS")
    logger.info("=" * 60)
    logger.info(f"📝 Log completo: {test_log_file}")
    
    if exitstatus == 0:
        logger.info("🎉 ¡Todos los tests pasaron exitosamente!")
    else:
        logger.warning("⚠️ Algunos tests fallaron - revisar errores en el log")
    
    logger.info("=" * 60) 