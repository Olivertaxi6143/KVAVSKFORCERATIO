# Test Coverage Analysis & Improvement Plan

## Executive Summary

The KVAVSKFORCERATIO (QVA Strategy Studio) codebase has **significant test coverage gaps**. With ~75 source files (~44,400 LOC) and only 3 substantive test files (~33 tests), the estimated line coverage is **under 5%**. The existing tests cover error handling and ISA database basics, but the core financial analysis engine, scoring systems, data pipeline, ML validation, and nearly all business logic remain untested.

---

## Current State

### What exists

| Test File | Module Tested | Tests | Coverage Scope |
|---|---|---|---|
| `test_error_handler.py` | `gui/error_handler.py` | 11 | IntuitiveErrorHandler initialization, categories, solutions, basic handling |
| `test_isa_phase11.py` | `data/isa_database.py` | 4 | ISADatabase init, strategy CRUD, analysis results, backup |
| `test_robustness_validation.py` | `core/utils/error_handler.py`, `core/utils/validation_utils.py` | 18 | RobustErrorHandler init, data validation shapes/types/ranges, corrupted data, system limits |

### What is missing

**71 out of ~75 source files have zero dedicated test coverage.** Key untested areas:

- **Core scoring engine** (QVA scorer, Factor K calculator, unified evaluator)
- **Financial analysis** (tail risk, predictability, scientific analysis, Darwinex pipeline)
- **Data pipeline** (data_manager, data_utils, column_mapping, SQX exporter)
- **ML subsystem** (advanced ML validation, ISA training, ML intelligence enhancer)
- **Market analysis** (regime detection, robustness analyzer)
- **Compliance** (audit trails, compliance reporting)
- **Integration layer** (CoreEngine orchestration)
- **All GUI components** (19 files, no functional tests)
- **Utility infrastructure** (cache, memory management, lazy loading, parallel processing)

---

## Priority Recommendations

### Priority 1 (Critical) - Core Business Logic

These modules contain the financial calculations that the entire system depends on. Bugs here produce silently wrong results.

#### 1.1 QVA Scoring System (`src/core/analysis/qva_analyzer.py`)

**Why:** The QVA score is the primary output of the system. 1,779 lines with zero tests.

**Recommended tests:**
- `calculate_qva_score()` with known input DataFrames and expected score outputs
- `compute_qva_score_robust()` produces scores within valid ranges (0-10)
- Weight updates via `update_trading_style_weights()` change output scores predictably
- Penalty configuration via `update_penalty_config()` applies correctly
- `explain_score()` returns breakdown that sums to the total score
- Edge cases: empty DataFrame, single-row DataFrame, all-NaN columns, extreme values
- Different trading styles produce different weight distributions

#### 1.2 Factor K Calculator (`src/core/analysis/factor_k_analyzer.py`)

**Why:** Factor K is a proprietary scoring metric central to strategy evaluation. 1,140 lines untested.

**Recommended tests:**
- `evaluate_strategies()` returns DataFrame with expected columns and valid ranges
- Component calculations (stability, growth, efficiency, consistency, risk) return sensible values for known inputs
- Dynamic penalties reduce scores for poor strategies
- `load_and_prepare_data()` handles CSV/Excel with missing columns gracefully
- Edge cases: strategies with zero trades, negative returns, extreme drawdowns

#### 1.3 Unified Evaluator (`src/core/analysis/unified_evaluator.py`)

**Why:** Combines QVA + Factor K + ML scores. Untested integration point.

**Recommended tests:**
- Combined score is a weighted function of its inputs
- Missing individual scores are handled (fallback behavior)
- Category assignment (Elite, Excellent, Good, etc.) uses correct thresholds

---

### Priority 2 (High) - Data Pipeline

Data loading and transformation bugs silently corrupt all downstream analysis.

#### 2.1 Data Utilities (`src/data/data_utils.py`)

**Why:** 869 lines of pure utility functions - highly testable, foundational to everything.

**Recommended tests:**
- `safe_float()`, `safe_int()`, `safe_str()`, `safe_bool()` with valid, invalid, None, edge-case inputs
- `calculate_max_drawdown()` with known return series (manually computed expected values)
- `detect_outliers_iqr()` correctly identifies known outliers
- `clean_extreme_values()` removes/clips extremes without altering normal data
- `normalize_series()` produces values in [0,1] for min-max, mean-0/std-1 for z-score
- `read_and_prepare()` with CSV files containing various column formats
- `improve_missing_data_handling()` imputes correctly, doesn't destroy valid data
- `ensure_numeric_columns()` converts string numbers, handles non-convertible values

#### 2.2 Data Manager (`src/data/data_manager.py`)

**Why:** Central data orchestration (1,393 lines). Every analysis path goes through it.

**Recommended tests:**
- `load_and_prepare_data_pipeline()` with valid CSV/Excel returns correct DataFrame shape
- `analyze_data_quality()` reports correct null counts, type distributions
- `validate_inputtest_data()` rejects DataFrames missing required columns
- Cache round-trip: `save_to_cache()` then `load_from_cache()` returns equivalent data
- `export_consolidated_data()` writes valid CSV/Excel files
- Error handling: non-existent file paths, corrupt files, permission errors

#### 2.3 Column Mapping (`src/data/column_mapping.py`)

**Why:** Column name normalization is a silent failure point. If mappings are wrong, analysis uses wrong data.

**Recommended tests:**
- `normalize_column_names()` maps known SQX/Darwinex column names to internal names
- Unmapped columns are preserved (not dropped)
- Case-insensitive matching works correctly
- Duplicate column names after normalization are handled

---

### Priority 3 (High) - Validation Utilities

#### 3.1 Validation Utils (`src/core/utils/validation_utils.py`)

**Why:** Currently imported but no functions are actually called in tests. Every validation function needs direct tests.

**Recommended tests:**
- `validate_config()` passes with all required keys, fails with missing keys
- `validate_kpi_config()` rejects configs with invalid weight ranges
- `validate_file_path()` accepts existing files of correct type, rejects missing/wrong-type
- `validate_numeric_range()` for boundary conditions (at min, at max, below min, above max)
- `validate_percentage()` accepts 0-100, rejects negatives and >100
- `validate_probability()` accepts 0-1, rejects outside range
- `validate_series_quality()` rejects series with too many nulls
- `validate_correlation_matrix()` rejects non-symmetric matrices

---

### Priority 4 (Medium) - Financial Analysis Modules

#### 4.1 Tail Risk Metrics (`src/analysis/tail_risk_metrics.py`)

**Recommended tests:**
- `calculate_tail_risk_metrics()` returns correct VaR/CVaR for known return distributions (e.g., normal distribution with known parameters)
- Historical vs parametric methods produce different but reasonable results
- Portfolio-level tail risk aggregation with known weights
- Edge cases: single return observation, all-positive returns, extreme outliers

#### 4.2 Predictability Metrics (`src/analysis/predictability_metrics.py`)

**Recommended tests:**
- IS/OOS consistency score: identical IS and OOS data should score high; uncorrelated should score low
- Overfitting detection: strategy with IS >> OOS performance flags as overfitted
- Temporal robustness: stable time-series scores high; trending scores lower
- Stability score: low-variance metrics score high

#### 4.3 Scientific Analysis (`src/analysis/scientific_analysis.py`)

**Recommended tests:**
- Available analyses list matches expected analysis types
- Correlation matrix preparation returns valid symmetric matrix
- Score distribution preparation returns correct histogram data
- Each analysis type runs without error on sample data

#### 4.4 Market Regime Detection (`src/core/market_regime_analyzer.py`)

**Recommended tests:**
- `detect_regimes()` assigns one of the expected regime labels (Bull, Bear, Sideways, Crisis)
- Clearly bullish data (monotonically increasing) labels as Bull
- Clearly bearish data labels as Bear
- Regime-specific weight optimization changes weights based on regime
- HMM fitting converges on synthetic data with known regimes

---

### Priority 5 (Medium) - ML and Integration

#### 5.1 Advanced ML Validation (`src/ml/advanced_ml_validation.py`)

**Recommended tests:**
- Walk-forward validation produces expected number of folds
- Data drift detection flags when distributions shift significantly
- Regime detection returns valid regime labels
- Temporal validation handles time-series data correctly
- Edge cases: insufficient data for splits, constant features

#### 5.2 Integration Layer (`src/core/integration_layer.py`)

**Recommended tests:**
- `run_comprehensive_analysis()` returns dict with all expected keys
- `validate_dataframe()` rejects invalid inputs, accepts valid ones
- `generate_insights()` returns non-empty list for scored strategies
- `categorize_quality()` assigns correct categories based on score thresholds
- End-to-end: sample data through full pipeline produces consistent results

#### 5.3 Compliance Audit (`src/core/compliance_audit.py`)

**Recommended tests:**
- `audit_strategy_selection()` creates valid ComplianceReport
- Audit history is retrievable by date range
- JSON/CSV export produces valid, parseable files
- Alert generation flags actual compliance violations

---

### Priority 6 (Lower) - Infrastructure & Caching

#### 6.1 Cache Manager (`src/core/utils/cache_manager.py`)

**Recommended tests:**
- Cache set/get round-trip returns same data
- Cache respects `max_age_hours` (expired entries return None)
- Cache respects `max_size_mb` (evicts old entries when full)
- `clear_cache()` removes all entries
- `get_stats()` reports correct hit/miss counts

#### 6.2 Memory Manager & Optimizer

**Recommended tests:**
- Memory optimization reduces DataFrame memory usage
- Cleanup releases references to large objects

#### 6.3 Lazy Loader & Parallel Trainer

**Recommended tests:**
- Lazy-loaded modules are only imported when accessed
- Parallel trainer distributes work across workers

---

### Priority 7 (Lower) - GUI Components

GUI testing requires `pytest-qt` (already in optional deps). Focus on logic, not visual layout.

**Recommended approach:**
- Test tab classes that contain business logic (e.g., filter application, data transformation)
- Test `advanced_export.py` export logic with mock data
- Test `advanced_filters_popup.py` filter criteria generation
- Test `gui/utils.py` utility functions independently
- Use `pytest-qt` fixtures for widget lifecycle tests

---

## Structural Recommendations

### 1. Mirror source structure in tests

```
tests/
  analysis/
    test_tail_risk_metrics.py
    test_predictability_metrics.py
    test_scientific_analysis.py
  core/
    analysis/
      test_qva_analyzer.py
      test_factor_k_analyzer.py
      test_unified_evaluator.py
    utils/
      test_validation_utils.py
      test_cache_manager.py
    test_robustness_analyzer.py
    test_market_regime_analyzer.py
    test_integration_layer.py
    test_compliance_audit.py
  data/
    test_data_manager.py
    test_data_utils.py
    test_column_mapping.py
    test_isa_database.py
  ml/
    test_advanced_ml_validation.py
  gui/
    test_error_handler.py
  conftest.py
```

### 2. Add shared test data fixtures

The existing `conftest.py` has good fixtures (`sample_strategies_data`, `sample_portfolio_data`). Extend with:
- A fixture producing a minimal but complete DataFrame suitable for full-pipeline testing
- Fixtures for known-answer test cases (e.g., a return series where drawdown is manually calculated)
- Temporary file fixtures for CSV/Excel loading tests

### 3. Use pytest markers consistently

The markers are configured (`slow`, `integration`, `unit`, `gui`, `ml`, `performance`) but none of the existing tests use them. Apply markers so CI can run fast unit tests on every commit and slower tests on schedule.

### 4. Set a coverage target

The CI pipeline already has `pytest-cov` and Codecov integration. Set a minimum coverage threshold (start at 40%, increase incrementally) in `pyproject.toml`:

```toml
[tool.coverage.report]
fail_under = 40
```

### 5. Prioritize pure-function tests first

Many modules in `data_utils.py`, `validation_utils.py`, and `column_mapping.py` are pure functions with no side effects. These are the easiest to test and provide the highest confidence-per-effort ratio. Start here.

---

## Risk Assessment

| Untested Area | Risk Level | Impact of Bug |
|---|---|---|
| QVA Scoring | **Critical** | Wrong strategy rankings, bad investment decisions |
| Factor K Calculation | **Critical** | Incorrect strategy evaluation scores |
| Data Utils (safe_float, normalization) | **High** | Silent data corruption across all analyses |
| Column Mapping | **High** | Wrong data fed to calculations |
| Validation Utils | **High** | Invalid configs accepted, causing runtime errors |
| Tail Risk / Predictability | **Medium** | Incorrect risk assessments |
| ML Validation | **Medium** | Overfitting not detected, unreliable predictions |
| Cache Manager | **Low** | Stale results served (functional, not financial risk) |
| GUI Components | **Low** | UI bugs, not calculation errors |

---

## Conclusion

The most impactful next step is writing tests for the **core scoring modules** (QVA analyzer, Factor K, unified evaluator) and the **data utility functions**. These represent the highest risk (financial calculation correctness) and the highest testability (pure functions with known inputs/outputs). A focused effort on Priority 1-3 would bring the codebase from ~5% to ~30-40% meaningful coverage and catch the most dangerous class of bugs: silently wrong financial calculations.
