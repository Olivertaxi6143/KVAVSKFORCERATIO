"""
Módulo de análisis del core engine.

Este módulo contiene todos los analizadores especializados:
- Factor K Elite 96 Enhanced
- QVA Analyzer  
- Unified Scorer
- Darwin Analyzer
- Darwin Pipeline
- Extra KPI Manager
"""

from .factor_k_analyzer import FactorKElite96Enhanced
# Los siguientes se implementarán en pasos posteriores
# from .qva_analyzer import QVAAnalyzer
# from .unified_scorer import UnifiedScorer
# from .darwin_analyzer import DarwinAnalyzer
# from .darwin_pipeline import DarwinPipeline
# from .extra_kpi_manager import ExtraKPIManager

__all__ = [
    'FactorKElite96Enhanced',
    # 'QVAAnalyzer', 
    # 'UnifiedScorer',
    # 'DarwinAnalyzer',
    # 'DarwinPipeline',
    # 'ExtraKPIManager'
] 