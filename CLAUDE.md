# CLAUDE.md — QVA Strategy Studio (KVAVSKFORCERATIO)

This file provides AI assistants with the context needed to work effectively in this codebase.

---

## Project Overview

**QVA Strategy Studio** is an advanced quantitative trading analysis platform for evaluating, ranking, and comparing trading strategies. It combines multi-factor scoring (Factor K + QVA), machine learning, statistical analysis, and a PySide6 GUI.

- **Language:** Python 3.11+ (supports 3.12, 3.13)
- **Package name:** `qva-strategy-studio` v1.0.0
- **Primary GUI framework:** PySide6
- **Key analysis libraries:** pandas, numpy, scipy, statsmodels, scikit-learn, lightgbm, xgboost, catboost
- **Documentation language:** Predominantly Spanish (comments, docstrings, variable names)

---

## Repository Structure

```
KVAVSKFORCERATIO/
├── src/                          # All source code (~34,700 LOC, 75 Python files)
│   ├── core/                     # Core analysis engine
│   │   ├── analysis/             # Scoring algorithms (Factor K, QVA, Unified Evaluator)
│   │   ├── config/               # ConfigManagerEnhanced and related config classes
│   │   ├── utils/                # Error handling, caching, memory, lazy loading
│   │   ├── optimization/         # Optimization modules
│   │   ├── post_processing/      # Post-processing utilities
│   │   ├── integration_layer.py  # Bridge/facade between all analysis modules
│   │   ├── market_regime_analyzer.py   # KMeans/HMM regime detection
│   │   ├── predictability_analyzer.py  # Walk-forward validation
│   │   └── robustness_analyzer.py      # Stress testing and Monte Carlo
│   ├── gui/                      # PySide6 GUI (19 files)
│   │   ├── main_window.py        # Main application window with tab container
│   │   ├── steps/                # Multi-step workflow wizard UI
│   │   ├── advisor/              # Financial advisor GUI components
│   │   ├── *_tab.py              # Individual analysis tabs
│   │   └── utils.py              # GUI helper utilities
│   ├── data/                     # Data pipeline
│   │   ├── data_manager.py       # Centralized loader (CSV, Excel, PDF, SQX)
│   │   ├── data_utils.py         # Transformations and normalization helpers
│   │   ├── column_mapping.py     # Column name normalization across formats
│   │   ├── isa_database.py       # ISA (In-Sample/Out-of-Sample) database
│   │   ├── ml_database.py        # ML feature/label storage
│   │   ├── sqx_exporter.py       # StrategyQuant X format export
│   │   └── isa_integration.py    # ISA workflow integration
│   ├── analysis/                 # Higher-level analysis modules
│   │   ├── advanced_analysis_enhanced.py      # ML-enhanced analysis (98KB)
│   │   ├── asesor_financiero_inteligente.py   # AI financial advisor logic (64KB)
│   │   ├── scientific_analysis.py             # Scientific/statistical metrics
│   │   ├── predictability_metrics.py          # IS/OOS correlation analysis
│   │   ├── tail_risk_metrics.py               # VaR, CVaR, Ulcer Index
│   │   ├── axi_select_analysis.py             # AXISelect integration
│   │   └── darwinex_pipeline.py               # Darwinex data pipeline
│   ├── ml/                       # Machine learning subsystem
│   │   ├── isa_training.py               # ISA model training
│   │   ├── isa_training_enhanced.py      # Enhanced ISA training
│   │   └── advanced_ml_validation.py     # Cross-validation and ML validation
│   ├── config/                   # Additional config utilities
│   └── logger_config.py          # Centralized logging configuration
│
├── tests/                        # Test suite
│   ├── conftest.py               # Pytest fixtures and shared setup
│   ├── test_error_handler.py     # GUI error handling tests (11 tests)
│   ├── test_isa_phase11.py       # ISA database tests (4 tests)
│   └── test_robustness_validation.py  # Validation and error handling (18+ tests)
│
├── config/
│   └── trading_config.json       # KPI weights, trading styles, scoring parameters
│
├── docs/                         # Documentation (15+ Markdown files, mostly Spanish)
│   ├── README.md
│   ├── CORE_MODULE.md
│   ├── DATA_MODULE.md
│   ├── CORE_ENGINE_DOCUMENTACION.md
│   ├── TEST_COVERAGE_ANALYSIS.md # Coverage gap analysis and prioritization
│   ├── ROADMAPS/                 # Feature and professional roadmaps
│   └── GUI_MODULAR_WIREFRAME.md
│
├── .github/workflows/
│   ├── ci.yml                    # PR/push lint+test pipeline (Python 3.11)
│   └── ci-cd.yml                 # Full pipeline: test + security + build + deploy
│
├── pyproject.toml                # Project metadata + all tool configuration
├── requirements.txt              # Minimal dependency list
├── main.py                       # Primary entry point
├── run_gui.py                    # GUI launcher script
├── run_gui.sh / run_gui.bat      # Platform-specific GUI launchers
├── cli_asesor_financiero.py      # CLI for financial advisor workflow
├── cli_runner.py                 # General CLI runner framework
└── build_exe.spec                # PyInstaller spec for standalone executable
```

---

## Development Setup

```bash
# Requires Python 3.11+
python --version

# Install with all dev dependencies
pip install -e ".[dev]"

# Or install just core dependencies
pip install -e .

# Optional dependency groups:
pip install -e ".[ml]"    # Extra ML libraries (optuna, etc.)
pip install -e ".[gui]"   # PyQt6 alternative
pip install -e ".[docs]"  # Sphinx documentation
```

---

## Common Commands

### Run the Application

```bash
# Launch GUI
python run_gui.py
# or
python main.py

# Platform launchers
./run_gui.sh        # Linux/Mac
run_gui.bat         # Windows

# CLI financial advisor
python cli_asesor_financiero.py

# General CLI runner
python cli_runner.py
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run by marker
pytest -m unit
pytest -m "not slow"
pytest -m "not gui"           # Skip GUI tests (useful in headless environments)
pytest -m integration
pytest -m performance

# Run specific test file
pytest tests/test_error_handler.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/

# Security audit
bandit -r src/
safety check

# Run all checks (mirrors CI)
black --check src/ tests/ && isort --check src/ tests/ && ruff check src/ tests/ && mypy src/
```

---

## Architecture Overview

### Scoring Pipeline

The core workflow evaluates trading strategies through three layers:

```
Input Data (CSV/Excel/PDF/SQX)
        ↓
  DataManager (src/data/data_manager.py)
  - Loads and normalizes column names (column_mapping.py)
  - Validates data types and ranges
        ↓
  Factor K Analyzer (src/core/analysis/factor_k_analyzer.py)
  - Computes Factor K 9.6 score
  - Categories: Elite / Excellent / Good / Average / Poor
        ↓
  QVA Analyzer (src/core/analysis/qva_analyzer.py)
  - Quantitative Value Analysis scoring
  - Weighted KPI combination by trading style
        ↓
  ML Intelligence Enhancer (src/core/analysis/ml_intelligence_enhancer.py)
  - Optional ML layer on top of analytical scores
        ↓
  Unified Evaluator (src/core/analysis/unified_evaluator.py)
  - Combines Factor K + QVA + ML scores
  - Final ranking and categorization
        ↓
  Export (CSV, Excel, SQX format via src/data/sqx_exporter.py)
```

### Integration Layer

`src/core/integration_layer.py` is the primary facade used by the GUI and CLI. It bridges all analysis modules and provides a stable interface during ongoing refactoring. When adding new analysis modules, register them through the integration layer.

### GUI Architecture (PySide6)

- `src/gui/main_window.py` — QMainWindow with tab container
- Each analysis domain has its own `*_tab.py` — Performance, Tail Risk, Advisor, Portfolio, ISA Database, Strategy Comparison, Interactive Charts
- Long-running analyses use QThread with queue-based communication to avoid blocking the UI
- Error handling uses `GUIAnalysisError` and `RobustErrorHandler` from `src/core/utils/`

### Data Flow for ISA (In-Sample/Out-of-Sample)

```
Raw strategy results
    → ISA Database (src/data/isa_database.py)
    → ML training (src/ml/isa_training.py)
    → Predictability metrics (src/analysis/predictability_metrics.py)
    → IS/OOS correlation analysis
```

---

## Key Modules Reference

| Module | Purpose |
|--------|---------|
| `src/core/analysis/unified_evaluator.py` | Central scoring engine combining all metrics |
| `src/core/analysis/factor_k_analyzer.py` | Factor K 9.6 computation and categorization |
| `src/core/analysis/qva_analyzer.py` | QVA scoring algorithm (1,779 lines) |
| `src/core/integration_layer.py` | Facade bridging all analysis modules |
| `src/data/data_manager.py` | Unified data loader for all input formats |
| `src/data/column_mapping.py` | Column name normalization dictionary |
| `src/gui/main_window.py` | PySide6 main window and tab container |
| `src/core/robustness_analyzer.py` | Monte Carlo and stress testing |
| `src/core/market_regime_analyzer.py` | KMeans/HMM market regime detection |
| `src/core/predictability_analyzer.py` | Walk-forward validation |
| `src/analysis/tail_risk_metrics.py` | VaR, CVaR, Ulcer Index |
| `src/logger_config.py` | Centralized logging setup |
| `config/trading_config.json` | Runtime KPI weights and trading style configs |

---

## Code Conventions

### Formatting and Linting

All configured in `pyproject.toml`:

- **Black:** 88-character line length (`[tool.black]`)
- **isort:** `profile = "black"`, multi_line_output = 3 (`[tool.isort]`)
- **Ruff:** Rules E, W, F, I, B, C4, UP; ignores E501 (line length handled by Black) and C901 (complexity) (`[tool.ruff]`)
- **Mypy:** Strict mode — `disallow_untyped_defs`, `check_untyped_defs`, `warn_return_any`, etc. (`[tool.mypy]`)

### Naming

- **Modules/functions/variables:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private members:** `_leading_underscore`

### Language

- **Comments and docstrings:** Predominantly Spanish
- **Variable/function names:** Mix of Spanish and English; follow the existing style in the file you're editing
- **Log messages:** Spanish

### Type Annotations

All functions must have type annotations. Mypy strict mode is enforced in CI. Use `from __future__ import annotations` for forward references.

```python
def calcular_factor_k(
    datos: pd.DataFrame,
    estilo: str = "Swing",
) -> dict[str, float]:
    ...
```

### Error Handling

- Use `RobustErrorHandler` from `src/core/utils/` for recoverable errors
- Use `GUIAnalysisError` for GUI-layer errors
- Optional dependencies (e.g., `plotly`, `umap-learn`) must be imported with try/except and graceful fallback:

```python
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
```

### Logging

```python
from src.logger_config import get_logger

logger = get_logger(__name__)
logger.info("Procesando estrategia: %s", nombre)
```

### Performance Patterns

- Use `src/core/utils/cache_manager.py` for expensive computations
- Use `src/core/utils/memory_manager.py` when handling large DataFrames
- Use `src/core/utils/lazy_loader.py` for deferred module imports

---

## Testing

### Framework

- **pytest** with configuration in `pyproject.toml` (`[tool.pytest.ini_options]`)
- Fixtures defined in `tests/conftest.py`
- Strict markers — all custom markers must be registered

### Test Markers

| Marker | Use |
|--------|-----|
| `@pytest.mark.unit` | Pure unit tests (no I/O, no GUI) |
| `@pytest.mark.integration` | Tests involving multiple modules |
| `@pytest.mark.gui` | Tests requiring a display (skip in headless CI) |
| `@pytest.mark.slow` | Tests taking >5s |
| `@pytest.mark.performance` | Performance benchmarks |
| `@pytest.mark.stress` | Stress/load tests |

### Coverage Status

**Current coverage: ~5% (critical gap)**. Only 4 test files exist covering ~4 of 75 source modules. See `docs/TEST_COVERAGE_ANALYSIS.md` for the prioritized coverage roadmap.

Priority areas without tests:
1. `src/core/analysis/` — scoring engines (highest priority)
2. `src/data/data_manager.py` — data pipeline
3. `src/analysis/tail_risk_metrics.py` and `predictability_metrics.py`
4. `src/ml/` — ML training modules

When adding new features, write tests for the new code. Follow the `tests/test_robustness_validation.py` style for parametrized data validation tests.

---

## Configuration

### `config/trading_config.json`

Runtime configuration for:
- **Trading styles:** Intradía, Swing, Tendencial, Reversión a la media, Breakout
- **KPI weights:** Per-style weights for 20+ KPIs
- **Component weights:** Profitability (0.4), Risk (0.35), Consistency (0.25)
- **Scoring thresholds:** Category cutoffs for Elite/Excellent/Good/Average/Poor

Changes to this file affect live scoring without requiring code changes.

### `src/core/config/` — ConfigManagerEnhanced

For programmatic configuration overrides:
```python
from src.core.config import ConfigManagerEnhanced

config = ConfigManagerEnhanced()
config.set("kpi_weights.sharpe_ratio", 0.25)
```

---

## CI/CD

### `ci.yml` — PR/Push Pipeline (Python 3.11)

Triggers on push to `main` and all pull requests:
1. Lint: ruff, black --check, isort --check
2. Type check: pyright
3. Tests: pytest

### `ci-cd.yml` — Full Pipeline (Python 3.11, 3.12, 3.13)

Stages:
1. **test** — Lint (black, isort, ruff) + type check (mypy) + pytest
2. **integration-test** — End-to-end workflows, performance tests, GUI tests
3. **security** — bandit (code security) + safety (dependency CVEs)
4. **build** — Wheel and sdist packages
5. **deploy** — GitHub Release with artifacts (on version tags)
6. **notify** — Success/failure notifications

---

## Known Gaps and Priorities

1. **Test coverage (~5%)** — The single most critical improvement area. See `docs/TEST_COVERAGE_ANALYSIS.md` for the prioritized plan. Focus on `src/core/analysis/` first.
2. **Type annotation completeness** — Some older modules in `src/analysis/` have incomplete annotations. Mypy overrides exist for all third-party packages.
3. **Module migration** — `src/analysis/` (legacy) is being progressively migrated to `src/core/analysis/`. The `integration_layer.py` maintains backward compatibility during this transition.
4. **Optional ML dependencies** — catboost, lightgbm, xgboost, shap, optuna are optional at runtime but required in CI. Guard with try/except in new code.
