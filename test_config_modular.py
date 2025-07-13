"""
Test para validar los módulos de configuración extraídos.

Este test verifica que las clases de configuración funcionan correctamente
después de la extracción modular.
"""

import pytest
from src.core.config.kpi_config import KPIConfig, TradingStyleConfig
from src.core.config.progress_callback import ProgressCallback
from src.core.config.config_manager import ConfigManagerEnhanced


def test_kpi_config():
    kpi = KPIConfig(name="Sharpe_Ratio", enabled=True, weight=1.0)
    assert kpi.validate() is True
    kpi.weight = -1.0
    assert kpi.validate() is False
    kpi.weight = 1.0
    kpi.min_value = 2.0
    kpi.max_value = 1.0
    assert kpi.validate() is False


def test_trading_style_config():
    style = TradingStyleConfig(
        name="General",
        description="Estilo general",
        kpi_weights={"Sharpe_Ratio": 1.0},
        component_weights={"profitability": 0.5, "risk": 0.3, "consistency": 0.2},
        priority_kpis=["Sharpe_Ratio"]
    )
    assert style.validate() is True
    style.component_weights = {"profitability": 0.5, "risk": 0.3, "consistency": 0.5}
    assert style.validate() is False


def test_progress_callback():
    cb = ProgressCallback()
    cb.update_progress("step1", 1, 10, "desc")
    progress = cb.get_progress()
    assert progress is not None
    assert progress['step'] == "step1"
    cb.cancel()
    cb.update_progress("step2", 2, 10, "desc2")
    # No debe poner más progreso tras cancelar
    assert cb.get_progress() is None


def test_config_manager_enhanced(tmp_path):
    config_path = tmp_path / "test_config.json"
    manager = ConfigManagerEnhanced(config_file=str(config_path))
    # Debe cargar config por defecto
    assert isinstance(manager.current_config, dict)
    # Guardar y recargar
    ok = manager.save_config(manager.current_config)
    assert ok is True
    loaded = manager.load_config()
    assert loaded == manager.current_config
    # Validar config
    valid, errors = manager.validate_config(manager.current_config)
    assert valid is True
    # Config inválida
    invalid = {}
    valid, errors = manager.validate_config(invalid)
    assert valid is False
    assert len(errors) > 0

if __name__ == "__main__":
    test_kpi_config()
    test_trading_style_config()
    test_progress_callback()
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        import pathlib
        test_config_manager_enhanced(pathlib.Path(tmpdir))
    print("Todos los tests de configuración pasaron correctamente.") 