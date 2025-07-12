#!/usr/bin/env python3
"""
Módulo de Compliance y Auditoría para Estrategias de Trading
===========================================================

Implementa sistema de compliance y auditoría para estrategias de trading:
- Registro y trazabilidad de decisiones de selección
- Auditoría de filtros aplicados y reglas de compliance
- Reportes de cumplimiento y validación
- Logging de cambios y modificaciones
- Verificación de integridad de datos
- Alertas de compliance y riesgo

Basado en estándares de compliance financiero y auditoría.

Autor: Sistema de Análisis Cuantitativo
Fecha: 2025-01-27
Versión: 1.0.0
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path
import hashlib
import uuid
from enum import Enum
import warnings
from collections import defaultdict, OrderedDict
import traceback
import sys

# Configurar warnings
warnings.filterwarnings("ignore")

# Configurar logging
logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    """Niveles de compliance."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditStatus(Enum):
    """Estados de auditoría."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    REVIEW = "review"

@dataclass
class ComplianceRule:
    """Regla de compliance."""
    rule_id: str
    name: str
    description: str
    category: str
    level: ComplianceLevel
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)

@dataclass
class AuditRecord:
    """Registro de auditoría."""
    audit_id: str
    timestamp: datetime
    action: str
    component: str
    status: AuditStatus
    details: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class ComplianceReport:
    """Reporte de compliance."""
    report_id: str
    timestamp: datetime
    total_strategies: int
    passed_strategies: int
    failed_strategies: int
    warnings: int
    rules_applied: List[str]
    compliance_score: float
    risk_level: str
    recommendations: List[str]

class ComplianceAuditor:
    """
    Sistema de compliance y auditoría para estrategias de trading.
    
    Funcionalidades principales:
    - Registro y trazabilidad de decisiones
    - Auditoría de filtros y reglas aplicadas
    - Reportes de cumplimiento
    - Verificación de integridad de datos
    - Alertas de compliance
    """
    
    def __init__(self, 
                 audit_log_path: Optional[str] = None,
                 compliance_rules: Optional[List[ComplianceRule]] = None):
        """
        Inicializa el sistema de compliance y auditoría.
        
        Args:
            audit_log_path: Ruta para guardar logs de auditoría
            compliance_rules: Lista de reglas de compliance predefinidas
        """
        self.audit_log_path = audit_log_path or "logs/compliance_audit.log"
        self.compliance_rules = compliance_rules or self._create_default_rules()
        self.audit_records = []
        self.session_id = str(uuid.uuid4())
        self.logger = logger
        
        # Crear directorio de logs si no existe
        Path(self.audit_log_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging específico para compliance
        self._setup_compliance_logging()
        
        self.logger.info(f"🔒 ComplianceAuditor inicializado con {len(self.compliance_rules)} reglas")
        self.logger.info(f"📋 Session ID: {self.session_id}")
    
    def _setup_compliance_logging(self):
        """Configura logging específico para compliance."""
        compliance_handler = logging.FileHandler(self.audit_log_path)
        compliance_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        compliance_handler.setFormatter(formatter)
        
        compliance_logger = logging.getLogger('compliance')
        compliance_logger.addHandler(compliance_handler)
        compliance_logger.setLevel(logging.INFO)
        
        self.compliance_logger = compliance_logger
    
    def _create_default_rules(self) -> List[ComplianceRule]:
        """Crea reglas de compliance por defecto."""
        default_rules = [
            ComplianceRule(
                rule_id="MIN_TRADES",
                name="Mínimo de Trades",
                description="Estrategia debe tener al menos 30 trades",
                category="data_quality",
                level=ComplianceLevel.HIGH,
                parameters={"min_trades": 30}
            ),
            ComplianceRule(
                rule_id="MIN_SHARPE",
                name="Ratio de Sharpe Mínimo",
                description="Ratio de Sharpe debe ser mayor a 0.5",
                category="risk_metrics",
                level=ComplianceLevel.MEDIUM,
                parameters={"min_sharpe": 0.5}
            ),
            ComplianceRule(
                rule_id="MAX_DRAWDOWN",
                name="Drawdown Máximo",
                description="Drawdown máximo no debe exceder 50%",
                category="risk_management",
                level=ComplianceLevel.CRITICAL,
                parameters={"max_drawdown": 0.50}
            ),
            ComplianceRule(
                rule_id="PROFIT_FACTOR",
                name="Factor de Beneficio",
                description="Factor de beneficio debe ser mayor a 1.0",
                category="profitability",
                level=ComplianceLevel.MEDIUM,
                parameters={"min_profit_factor": 1.0}
            ),
            ComplianceRule(
                rule_id="DATA_INTEGRITY",
                name="Integridad de Datos",
                description="Verificar integridad y consistencia de datos",
                category="data_quality",
                level=ComplianceLevel.CRITICAL,
                parameters={}
            ),
            ComplianceRule(
                rule_id="IS_OOS_VALIDATION",
                name="Validación IS/OOS",
                description="Validar predictividad IS/OOS",
                category="validation",
                level=ComplianceLevel.HIGH,
                parameters={"min_is_oos_correlation": 0.3}
            )
        ]
        
        return default_rules
    
    def audit_strategy_selection(self, 
                               df: pd.DataFrame,
                               selected_strategies: List[str],
                               filters_applied: Dict[str, Any],
                               user_id: Optional[str] = None) -> ComplianceReport:
        """
        Audita el proceso de selección de estrategias.
        
        Args:
            df: DataFrame con todas las estrategias
            selected_strategies: Lista de estrategias seleccionadas
            filters_applied: Filtros aplicados en la selección
            user_id: ID del usuario que realizó la selección
            
        Returns:
            ComplianceReport con resultados de la auditoría
        """
        try:
            self.logger.info("🔍 Iniciando auditoría de selección de estrategias")
            
            audit_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # Registrar inicio de auditoría
            self._log_audit_record(
                audit_id=audit_id,
                action="strategy_selection_audit_start",
                component="selection",
                status=AuditStatus.PENDING,
                details={
                    "total_strategies": len(df),
                    "selected_count": len(selected_strategies),
                    "filters_applied": filters_applied
                },
                user_id=user_id
            )
            
            # Aplicar reglas de compliance
            compliance_results = self._apply_compliance_rules(df, selected_strategies)
            
            # Calcular métricas de compliance
            total_strategies = len(selected_strategies)
            passed_strategies = len([r for r in compliance_results if r["status"] == AuditStatus.PASSED])
            failed_strategies = len([r for r in compliance_results if r["status"] == AuditStatus.FAILED])
            warnings = len([r for r in compliance_results if r["status"] == AuditStatus.WARNING])
            
            compliance_score = passed_strategies / total_strategies if total_strategies > 0 else 0.0
            
            # Determinar nivel de riesgo
            risk_level = self._determine_risk_level(compliance_score, failed_strategies, warnings)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(compliance_results, compliance_score)
            
            # Crear reporte
            report = ComplianceReport(
                report_id=audit_id,
                timestamp=timestamp,
                total_strategies=total_strategies,
                passed_strategies=passed_strategies,
                failed_strategies=failed_strategies,
                warnings=warnings,
                rules_applied=[rule.rule_id for rule in self.compliance_rules if rule.enabled],
                compliance_score=compliance_score,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
            # Registrar fin de auditoría
            self._log_audit_record(
                audit_id=audit_id,
                action="strategy_selection_audit_complete",
                component="selection",
                status=AuditStatus.PASSED if compliance_score >= 0.8 else AuditStatus.WARNING,
                details={
                    "compliance_score": compliance_score,
                    "risk_level": risk_level,
                    "recommendations_count": len(recommendations)
                },
                user_id=user_id
            )
            
            self.logger.info(f"✅ Auditoría completada - Compliance Score: {compliance_score:.2f}")
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error en auditoría de selección: {e}")
            return self._create_error_report(str(e))
    
    def _apply_compliance_rules(self, 
                               df: pd.DataFrame, 
                               selected_strategies: List[str]) -> List[Dict[str, Any]]:
        """Aplica todas las reglas de compliance a las estrategias seleccionadas."""
        results = []
        
        for rule in self.compliance_rules:
            if not rule.enabled:
                continue
                
            try:
                rule_result = self._apply_single_rule(rule, df, selected_strategies)
                results.append(rule_result)
                
            except Exception as e:
                self.logger.error(f"Error aplicando regla {rule.rule_id}: {e}")
                results.append({
                    "rule_id": rule.rule_id,
                    "status": AuditStatus.FAILED,
                    "message": f"Error aplicando regla: {e}",
                    "details": {}
                })
        
        return results
    
    def _apply_single_rule(self, 
                          rule: ComplianceRule, 
                          df: pd.DataFrame, 
                          selected_strategies: List[str]) -> Dict[str, Any]:
        """Aplica una regla específica de compliance."""
        
        if rule.rule_id == "MIN_TRADES":
            return self._check_min_trades(rule, df, selected_strategies)
        elif rule.rule_id == "MIN_SHARPE":
            return self._check_min_sharpe(rule, df, selected_strategies)
        elif rule.rule_id == "MAX_DRAWDOWN":
            return self._check_max_drawdown(rule, df, selected_strategies)
        elif rule.rule_id == "PROFIT_FACTOR":
            return self._check_profit_factor(rule, df, selected_strategies)
        elif rule.rule_id == "DATA_INTEGRITY":
            return self._check_data_integrity(rule, df, selected_strategies)
        elif rule.rule_id == "IS_OOS_VALIDATION":
            return self._check_is_oos_validation(rule, df, selected_strategies)
        else:
            return {
                "rule_id": rule.rule_id,
                "status": AuditStatus.WARNING,
                "message": f"Regla {rule.rule_id} no implementada",
                "details": {}
            }
    
    def _check_min_trades(self, rule: ComplianceRule, df: pd.DataFrame, selected_strategies: List[str]) -> Dict[str, Any]:
        """Verifica número mínimo de trades."""
        min_trades = rule.parameters.get("min_trades", 30)
        failed_strategies = []
        
        for strategy in selected_strategies:
            strategy_data = df[df.index == strategy] if strategy in df.index else df[df.iloc[:, 0] == strategy]
            if not strategy_data.empty:
                trades_col = next((col for col in strategy_data.columns if 'trades' in col.lower() or 'total_trades' in col.lower()), None)
                if trades_col:
                    trades_count = strategy_data[trades_col].iloc[0]
                    if pd.isna(trades_count) or trades_count < min_trades:
                        failed_strategies.append(strategy)
        
        status = AuditStatus.PASSED if not failed_strategies else AuditStatus.FAILED
        
        return {
            "rule_id": rule.rule_id,
            "status": status,
            "message": f"Verificación de trades mínimos ({min_trades})",
            "details": {
                "min_trades_required": min_trades,
                "failed_strategies": failed_strategies,
                "failed_count": len(failed_strategies)
            }
        }
    
    def _check_min_sharpe(self, rule: ComplianceRule, df: pd.DataFrame, selected_strategies: List[str]) -> Dict[str, Any]:
        """Verifica ratio de Sharpe mínimo."""
        min_sharpe = rule.parameters.get("min_sharpe", 0.5)
        failed_strategies = []
        
        for strategy in selected_strategies:
            strategy_data = df[df.index == strategy] if strategy in df.index else df[df.iloc[:, 0] == strategy]
            if not strategy_data.empty:
                sharpe_col = next((col for col in strategy_data.columns if 'sharpe' in col.lower()), None)
                if sharpe_col:
                    sharpe_value = strategy_data[sharpe_col].iloc[0]
                    if pd.isna(sharpe_value) or sharpe_value < min_sharpe:
                        failed_strategies.append(strategy)
        
        status = AuditStatus.PASSED if not failed_strategies else AuditStatus.FAILED
        
        return {
            "rule_id": rule.rule_id,
            "status": status,
            "message": f"Verificación de Sharpe mínimo ({min_sharpe})",
            "details": {
                "min_sharpe_required": min_sharpe,
                "failed_strategies": failed_strategies,
                "failed_count": len(failed_strategies)
            }
        }
    
    def _check_max_drawdown(self, rule: ComplianceRule, df: pd.DataFrame, selected_strategies: List[str]) -> Dict[str, Any]:
        """Verifica drawdown máximo."""
        max_drawdown = rule.parameters.get("max_drawdown", 0.50)
        failed_strategies = []
        
        for strategy in selected_strategies:
            strategy_data = df[df.index == strategy] if strategy in df.index else df[df.iloc[:, 0] == strategy]
            if not strategy_data.empty:
                dd_col = next((col for col in strategy_data.columns if 'drawdown' in col.lower() or 'dd' in col.lower()), None)
                if dd_col:
                    dd_value = abs(strategy_data[dd_col].iloc[0])
                    if pd.isna(dd_value) or dd_value > max_drawdown:
                        failed_strategies.append(strategy)
        
        status = AuditStatus.PASSED if not failed_strategies else AuditStatus.FAILED
        
        return {
            "rule_id": rule.rule_id,
            "status": status,
            "message": f"Verificación de drawdown máximo ({max_drawdown*100}%)",
            "details": {
                "max_drawdown_allowed": max_drawdown,
                "failed_strategies": failed_strategies,
                "failed_count": len(failed_strategies)
            }
        }
    
    def _check_profit_factor(self, rule: ComplianceRule, df: pd.DataFrame, selected_strategies: List[str]) -> Dict[str, Any]:
        """Verifica factor de beneficio mínimo."""
        min_profit_factor = rule.parameters.get("min_profit_factor", 1.0)
        failed_strategies = []
        
        for strategy in selected_strategies:
            strategy_data = df[df.index == strategy] if strategy in df.index else df[df.iloc[:, 0] == strategy]
            if not strategy_data.empty:
                pf_col = next((col for col in strategy_data.columns if 'profit_factor' in col.lower() or 'profitfactor' in col.lower()), None)
                if pf_col:
                    pf_value = strategy_data[pf_col].iloc[0]
                    if pd.isna(pf_value) or pf_value < min_profit_factor:
                        failed_strategies.append(strategy)
        
        status = AuditStatus.PASSED if not failed_strategies else AuditStatus.FAILED
        
        return {
            "rule_id": rule.rule_id,
            "status": status,
            "message": f"Verificación de factor de beneficio mínimo ({min_profit_factor})",
            "details": {
                "min_profit_factor_required": min_profit_factor,
                "failed_strategies": failed_strategies,
                "failed_count": len(failed_strategies)
            }
        }
    
    def _check_data_integrity(self, rule: ComplianceRule, df: pd.DataFrame, selected_strategies: List[str]) -> Dict[str, Any]:
        """Verifica integridad de datos."""
        integrity_issues = []
        
        # Verificar valores nulos en columnas críticas
        critical_columns = ['Sharpe_Ratio', 'Profit_factor', 'Max_DD_%', 'CAGR']
        available_columns = [col for col in critical_columns if col in df.columns]
        
        for strategy in selected_strategies:
            strategy_data = df[df.index == strategy] if strategy in df.index else df[df.iloc[:, 0] == strategy]
            if not strategy_data.empty:
                for col in available_columns:
                    if pd.isna(strategy_data[col].iloc[0]):
                        integrity_issues.append(f"{strategy}: {col} es nulo")
        
        status = AuditStatus.PASSED if not integrity_issues else AuditStatus.FAILED
        
        return {
            "rule_id": rule.rule_id,
            "status": status,
            "message": "Verificación de integridad de datos",
            "details": {
                "integrity_issues": integrity_issues,
                "issues_count": len(integrity_issues)
            }
        }
    
    def _check_is_oos_validation(self, rule: ComplianceRule, df: pd.DataFrame, selected_strategies: List[str]) -> Dict[str, Any]:
        """Verifica validación IS/OOS."""
        min_correlation = rule.parameters.get("min_is_oos_correlation", 0.3)
        validation_issues = []
        
        # Buscar columnas IS/OOS
        is_cols = [col for col in df.columns if '(IS)' in col]
        oos_cols = [col for col in df.columns if '(OOS)' in col]
        
        if not is_cols or not oos_cols:
            validation_issues.append("No se encontraron columnas IS/OOS para validación")
        else:
            for strategy in selected_strategies:
                strategy_data = df[df.index == strategy] if strategy in df.index else df[df.iloc[:, 0] == strategy]
                if not strategy_data.empty:
                    # Verificar correlación IS/OOS si hay datos
                    for is_col in is_cols[:3]:  # Solo primeros 3 KPIs
                        base = is_col.replace(' (IS)', '').replace('(IS)', '').strip()
                        oos_col = next((c for c in oos_cols if base == c.replace(' (OOS)', '').replace('(OOS)', '').strip()), None)
                        if oos_col:
                            is_val = strategy_data[is_col].iloc[0]
                            oos_val = strategy_data[oos_col].iloc[0]
                            if pd.notna(is_val) and pd.notna(oos_val):
                                # Calcular correlación simple (en un caso real sería más complejo)
                                if abs(is_val - oos_val) / (abs(is_val) + 1e-8) > 0.5:
                                    validation_issues.append(f"{strategy}: Alta divergencia IS/OOS en {base}")
        
        status = AuditStatus.PASSED if not validation_issues else AuditStatus.WARNING
        
        return {
            "rule_id": rule.rule_id,
            "status": status,
            "message": "Verificación de validación IS/OOS",
            "details": {
                "validation_issues": validation_issues,
                "issues_count": len(validation_issues),
                "min_correlation_required": min_correlation
            }
        }
    
    def _determine_risk_level(self, compliance_score: float, failed_count: int, warnings: int) -> str:
        """Determina el nivel de riesgo basado en métricas de compliance."""
        if compliance_score >= 0.95 and failed_count == 0:
            return "BAJO"
        elif compliance_score >= 0.80 and failed_count <= 2:
            return "MEDIO"
        elif compliance_score >= 0.60 and failed_count <= 5:
            return "ALTO"
        else:
            return "CRÍTICO"
    
    def _generate_recommendations(self, compliance_results: List[Dict], compliance_score: float) -> List[str]:
        """Genera recomendaciones basadas en resultados de compliance."""
        recommendations = []
        
        if compliance_score < 0.8:
            recommendations.append("🔴 Revisar criterios de selección - muchas estrategias fallan compliance")
        
        failed_rules = [r for r in compliance_results if r["status"] == AuditStatus.FAILED]
        if failed_rules:
            recommendations.append(f"⚠️ {len(failed_rules)} reglas de compliance fallaron")
        
        # Recomendaciones específicas por regla
        for result in compliance_results:
            if result["status"] == AuditStatus.FAILED:
                rule_id = result["rule_id"]
                if rule_id == "MIN_TRADES":
                    recommendations.append("📊 Aumentar número mínimo de trades para mayor robustez")
                elif rule_id == "MIN_SHARPE":
                    recommendations.append("📈 Revisar estrategias con Sharpe bajo")
                elif rule_id == "MAX_DRAWDOWN":
                    recommendations.append("⚠️ Estrategias con drawdown excesivo - revisar gestión de riesgo")
                elif rule_id == "PROFIT_FACTOR":
                    recommendations.append("💰 Estrategias con factor de beneficio bajo - revisar rentabilidad")
        
        if not recommendations:
            recommendations.append("✅ Todas las estrategias cumplen con los estándares de compliance")
        
        return recommendations
    
    def _log_audit_record(self, 
                         audit_id: str,
                         action: str,
                         component: str,
                         status: AuditStatus,
                         details: Dict[str, Any],
                         user_id: Optional[str] = None):
        """Registra un evento de auditoría."""
        record = AuditRecord(
            audit_id=audit_id,
            timestamp=datetime.now(),
            action=action,
            component=component,
            status=status,
            details=details,
            user_id=user_id,
            session_id=self.session_id
        )
        
        self.audit_records.append(record)
        
        # Log al archivo de compliance
        self.compliance_logger.info(
            f"AUDIT: {action} | {component} | {status.value} | "
            f"User: {user_id or 'Unknown'} | Session: {self.session_id}"
        )
    
    def _create_error_report(self, error_message: str) -> ComplianceReport:
        """Crea un reporte de error."""
        return ComplianceReport(
            report_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            total_strategies=0,
            passed_strategies=0,
            failed_strategies=0,
            warnings=0,
            rules_applied=[],
            compliance_score=0.0,
            risk_level="CRÍTICO",
            recommendations=[f"Error en auditoría: {error_message}"]
        )
    
    def generate_compliance_report(self, 
                                 report: ComplianceReport,
                                 output_path: Optional[str] = None) -> str:
        """
        Genera un reporte detallado de compliance.
        
        Args:
            report: ComplianceReport a procesar
            output_path: Ruta para guardar el reporte
            
        Returns:
            Contenido del reporte como string
        """
        try:
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("REPORTE DE COMPLIANCE - ESTRATEGIAS DE TRADING")
            report_lines.append("=" * 80)
            report_lines.append(f"Report ID: {report.report_id}")
            report_lines.append(f"Fecha: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Session ID: {self.session_id}")
            report_lines.append("")
            
            # Resumen ejecutivo
            report_lines.append("RESUMEN EJECUTIVO:")
            report_lines.append("-" * 40)
            report_lines.append(f"• Total de estrategias: {report.total_strategies}")
            report_lines.append(f"• Estrategias que pasan: {report.passed_strategies}")
            report_lines.append(f"• Estrategias que fallan: {report.failed_strategies}")
            report_lines.append(f"• Advertencias: {report.warnings}")
            report_lines.append(f"• Score de compliance: {report.compliance_score:.2%}")
            report_lines.append(f"• Nivel de riesgo: {report.risk_level}")
            report_lines.append("")
            
            # Reglas aplicadas
            report_lines.append("REGLAS DE COMPLIANCE APLICADAS:")
            report_lines.append("-" * 40)
            for rule_id in report.rules_applied:
                rule = next((r for r in self.compliance_rules if r.rule_id == rule_id), None)
                if rule:
                    report_lines.append(f"• {rule.name}: {rule.description}")
            report_lines.append("")
            
            # Recomendaciones
            report_lines.append("RECOMENDACIONES:")
            report_lines.append("-" * 40)
            for rec in report.recommendations:
                report_lines.append(f"• {rec}")
            report_lines.append("")
            
            # Estado general
            if report.compliance_score >= 0.8:
                report_lines.append("✅ COMPLIANCE APROBADO")
            elif report.compliance_score >= 0.6:
                report_lines.append("⚠️ COMPLIANCE CON ADVERTENCIAS")
            else:
                report_lines.append("❌ COMPLIANCE RECHAZADO")
            
            report_content = "\n".join(report_lines)
            
            # Guardar reporte si se especifica ruta
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.logger.info(f"📄 Reporte de compliance guardado en: {output_path}")
            
            return report_content
            
        except Exception as e:
            self.logger.error(f"❌ Error generando reporte de compliance: {e}")
            return f"Error generando reporte: {e}"
    
    def get_audit_history(self, 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         component: Optional[str] = None) -> List[AuditRecord]:
        """
        Obtiene historial de auditoría filtrado.
        
        Args:
            start_date: Fecha de inicio para filtrar
            end_date: Fecha de fin para filtrar
            component: Componente específico para filtrar
            
        Returns:
            Lista de registros de auditoría filtrados
        """
        filtered_records = self.audit_records
        
        if start_date:
            filtered_records = [r for r in filtered_records if r.timestamp >= start_date]
        
        if end_date:
            filtered_records = [r for r in filtered_records if r.timestamp <= end_date]
        
        if component:
            filtered_records = [r for r in filtered_records if r.component == component]
        
        return filtered_records

    def export_report_json(self, report: ComplianceReport, output_path: str) -> None:
        """Exporta el reporte de compliance a formato JSON profesional."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report.__dict__, f, indent=4, ensure_ascii=False, default=str)
            self.logger.info(f"📄 Reporte de compliance JSON exportado en: {output_path}")
        except Exception as e:
            self.logger.error(f"❌ Error exportando reporte de compliance JSON: {e}")

    def export_report_csv(self, report: ComplianceReport, output_path: str) -> None:
        """Exporta el reporte de compliance a formato CSV profesional (solo resumen ejecutivo)."""
        try:
            df = pd.DataFrame([{k: v for k, v in report.__dict__.items() if k != 'recommendations'}])
            df.to_csv(output_path, index=False, encoding='utf-8')
            self.logger.info(f"📄 Reporte de compliance CSV exportado en: {output_path}")
        except Exception as e:
            self.logger.error(f"❌ Error exportando reporte de compliance CSV: {e}")

    def generate_alerts(self, report: ComplianceReport) -> list:
        """
        Genera una lista estructurada de alertas automáticas a partir del reporte de compliance.
        Args:
            report: ComplianceReport
        Returns:
            Lista de diccionarios con alertas
        """
        alerts = []
        if report.failed_strategies > 0:
            alerts.append({
                'type': 'Incumplimiento',
                'level': 'Crítico' if report.risk_level == 'CRÍTICO' else 'Alto',
                'message': f'❌ {report.failed_strategies} estrategias no cumplen con las reglas de compliance.'
            })
        if report.warnings > 0:
            alerts.append({
                'type': 'Advertencia',
                'level': 'Medio',
                'message': f'⚠️ {report.warnings} advertencias detectadas en el análisis de compliance.'
            })
        if report.compliance_score < 0.8:
            alerts.append({
                'type': 'Riesgo',
                'level': 'Alto',
                'message': f'🔴 Score de compliance bajo: {report.compliance_score:.2%}'
            })
        if not alerts:
            alerts.append({
                'type': 'OK',
                'level': 'Bajo',
                'message': '✅ Todas las estrategias cumplen con los estándares de compliance.'
            })
        self.logger.info(f"🚨 {len(alerts)} alertas generadas para compliance")
        return alerts

    def export_alerts_json(self, alerts: list, output_path: str) -> None:
        """Exporta las alertas generadas a un archivo JSON."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, indent=4, ensure_ascii=False, default=str)
            self.logger.info(f"📄 Alertas de compliance exportadas en: {output_path}")
        except Exception as e:
            self.logger.error(f"❌ Error exportando alertas de compliance JSON: {e}")


def audit_strategy_selection_compliance(df: pd.DataFrame,
                                      selected_strategies: List[str],
                                      filters_applied: Dict[str, Any],
                                      user_id: Optional[str] = None) -> ComplianceReport:
    """
    Función de conveniencia para auditar compliance de selección de estrategias.
    
    Args:
        df: DataFrame con estrategias
        selected_strategies: Estrategias seleccionadas
        filters_applied: Filtros aplicados
        user_id: ID del usuario
        
    Returns:
        ComplianceReport con resultados
    """
    try:
        auditor = ComplianceAuditor()
        return auditor.audit_strategy_selection(df, selected_strategies, filters_applied, user_id)
    except Exception as e:
        logger.error(f"Error en auditoría de compliance: {e}")
        return ComplianceReport(
            report_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            total_strategies=0,
            passed_strategies=0,
            failed_strategies=0,
            warnings=0,
            rules_applied=[],
            compliance_score=0.0,
            risk_level="CRÍTICO",
            recommendations=[f"Error en auditoría: {e}"]
        )


if __name__ == "__main__":
    # Ejemplo de uso
    logging.basicConfig(level=logging.INFO)
    
    # Crear datos de ejemplo
    df = pd.DataFrame({
        'Strategy': ['Strategy_1', 'Strategy_2', 'Strategy_3'],
        'Sharpe_Ratio': [1.2, 0.3, 2.1],
        'Profit_factor': [1.5, 0.8, 2.3],
        'Max_DD_%': [0.15, 0.60, 0.10],
        'Total_Trades': [45, 15, 120]
    })
    
    selected = ['Strategy_1', 'Strategy_3']
    filters = {'min_sharpe': 0.5, 'min_trades': 30}
    
    report = audit_strategy_selection_compliance(df, selected, filters, "user_123")
    print(f"Compliance Score: {report.compliance_score:.2%}")
    print(f"Risk Level: {report.risk_level}") 