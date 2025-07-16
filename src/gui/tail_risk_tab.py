"""
Pestaña de Tail Risk Analysis para QVA Strategy Studio
Integra el módulo TailRiskMetrics con interfaz profesional.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from src.analysis.tail_risk_metrics import TailRiskAnalyzer
from src.data.data_utils import clean_returns

logger = logging.getLogger(__name__)

class TailRiskTab:
    """Pestaña profesional para análisis de Tail Risk."""
    
    def __init__(self, parent_frame):
        """Inicializa la pestaña de Tail Risk Analysis."""
        self.parent = parent_frame
        self.analyzer = TailRiskAnalyzer()
        self.current_data = None
        self.analysis_results = None
        
        self._create_widgets()
        logger.info("🔬 Pestaña Tail Risk Analysis inicializada")
    
    def _create_widgets(self):
        """Crea los widgets de la interfaz."""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(
            self.main_frame, 
            text="🔬 Análisis de Tail Risk", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(self.main_frame, text="Controles de Análisis", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botón de análisis
        self.analyze_btn = ttk.Button(
            controls_frame,
            text="🔬 Ejecutar Análisis de Tail Risk",
            command=self._run_tail_risk_analysis
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de visualización
        self.visualize_btn = ttk.Button(
            controls_frame,
            text="📊 Visualizar Resultados",
            command=self._show_detailed_results,
            state=tk.DISABLED
        )
        self.visualize_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de exportación
        self.export_btn = ttk.Button(
            controls_frame,
            text="📤 Exportar Reporte",
            command=self._export_tail_risk_report,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de limpiar
        self.clear_btn = ttk.Button(
            controls_frame,
            text="🧹 Limpiar",
            command=self._clear_results
        )
        self.clear_btn.pack(side=tk.LEFT)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(self.main_frame, text="Resultados del Análisis", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de resultados con scroll
        self.results_text = tk.Text(
            results_frame,
            wrap=tk.WORD,
            height=20,
            font=("Consolas", 10)
        )
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Información del análisis
        info_frame = ttk.LabelFrame(self.main_frame, text="Información del Análisis", padding=10)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = """
🔬 ANÁLISIS DE TAIL RISK

Este módulo calcula métricas avanzadas de riesgo de cola para estrategias de trading:

• VaR (Value at Risk): Pérdida máxima esperada en un nivel de confianza
• CVaR (Conditional Value at Risk): Pérdida esperada condicionada a estar en la cola
• Expected Shortfall: Pérdida esperada en eventos extremos
• Tail Concentration: Concentración de riesgo en las colas
• Extreme Loss Probability: Probabilidad de pérdidas extremas
• Volatility of Tails: Volatilidad de los eventos de cola

Niveles de confianza: 90%, 95%, 99%
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack()
    
    def set_data(self, data: pd.DataFrame):
        """Establece los datos para el análisis."""
        self.current_data = data
        logger.info(f"📊 Datos establecidos para Tail Risk Analysis: {len(data)} estrategias")
    
    def _run_tail_risk_analysis(self):
        """Ejecuta el análisis de tail risk."""
        if self.current_data is None or len(self.current_data) == 0:
            messagebox.showwarning(
                "Advertencia",
                "No hay datos disponibles para el análisis de Tail Risk.\n"
                "Por favor, carga datos de estrategias primero."
            )
            return
        
        try:
            self.analyze_btn.config(state=tk.DISABLED)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "🔬 Ejecutando análisis de Tail Risk...\n\n")
            self.parent.update()
            
            # Ejecutar análisis
            self.analysis_results = self._perform_tail_risk_analysis()
            
            # Mostrar resultados
            self._display_results()
            
            # Habilitar botones
            self.visualize_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)
            
            logger.info("✅ Análisis de Tail Risk completado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error en análisis de Tail Risk: {e}")
            messagebox.showerror(
                "Error",
                f"Error durante el análisis de Tail Risk:\n{str(e)}"
            )
            self.analyze_btn.config(state=tk.NORMAL)
    
    def _perform_tail_risk_analysis(self) -> Dict[str, Any]:
        """Realiza el análisis de tail risk."""
        results = {
            "strategies_analysis": [],
            "portfolio_analysis": None,
            "risk_alerts": []
        }
        
        # Analizar cada estrategia
        for idx, row in self.current_data.iterrows():
            strategy_name = row.get('Strategy_Name', f'Strategy_{idx}')
            
            # Simular retornos (en implementación real, usar datos reales)
            returns = self._simulate_returns_for_strategy(row)
            
            # Calcular métricas de tail risk
            metrics = self.analyzer.calculate_tail_risk_metrics(
                returns, 
                strategy_name=strategy_name
            )
            
            results["strategies_analysis"].append(metrics)
            
            # Verificar alertas de riesgo
            if self._check_risk_alerts(metrics):
                results["risk_alerts"].append({
                    "strategy": strategy_name,
                    "alert_type": "High Tail Risk",
                    "details": f"VaR 95%: {metrics.get('var_95', 'N/A'):.2f}%"
                })
        
        # Análisis de portafolio
        if len(results["strategies_analysis"]) > 1:
            results["portfolio_analysis"] = self.analyzer.analyze_portfolio_tail_risk(
                results["strategies_analysis"]
            )
        
        return results
    
    def _simulate_returns_for_strategy(self, strategy_data: pd.Series) -> pd.Series:
        """Simula retornos basados en métricas de la estrategia."""
        # En implementación real, usar datos históricos reales
        factor_k = strategy_data.get('Factor_K', 7.0)
        sharpe = strategy_data.get('Sharpe_Ratio_IS', 1.5)
        drawdown = strategy_data.get('Max_Drawdown_IS', 15.0)
        
        # Generar retornos simulados basados en métricas
        n_days = 252  # Año comercial
        volatility = drawdown / 100 * 2  # Aproximación de volatilidad
        expected_return = sharpe * volatility / np.sqrt(252)
        
        # Generar retornos con distribución t-student (colas más pesadas)
        returns = np.random.standard_t(df=5, size=n_days) * volatility / np.sqrt(252) + expected_return
        
        return pd.Series(returns)
    
    def _check_risk_alerts(self, metrics: Dict[str, Any]) -> bool:
        """Verifica si hay alertas de riesgo."""
        var_95 = metrics.get('var_95', np.nan)
        extreme_prob = metrics.get('extreme_loss_probability', np.nan)
        
        return (
            (not np.isnan(var_95) and var_95 < -0.05) or  # VaR > 5%
            (not np.isnan(extreme_prob) and extreme_prob > 0.05)  # Prob extrema > 5%
        )
    
    def _display_results(self):
        """Muestra los resultados del análisis."""
        if not self.analysis_results:
            return
        
        self.results_text.delete(1.0, tk.END)
        
        # Encabezado
        header = "🔬 RESULTADOS DEL ANÁLISIS DE TAIL RISK\n"
        header += "=" * 60 + "\n\n"
        self.results_text.insert(tk.END, header)
        
        # Análisis por estrategia
        strategies_analysis = self.analysis_results.get("strategies_analysis", [])
        if strategies_analysis:
            self.results_text.insert(tk.END, "📊 ANÁLISIS POR ESTRATEGIA:\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n")
            
            for analysis in strategies_analysis:
                strategy_name = analysis.get("strategy_name", "Unknown")
                self.results_text.insert(tk.END, f"\n🏆 Estrategia: {strategy_name}\n")
                
                # Métricas principales
                var_95 = analysis.get("var_95", np.nan)
                cvar_95 = analysis.get("cvar_95", np.nan)
                tail_conc = analysis.get("tail_concentration", np.nan)
                extreme_prob = analysis.get("extreme_loss_probability", np.nan)
                
                self.results_text.insert(tk.END, f"   VaR 95%: {var_95:.2f}%\n")
                self.results_text.insert(tk.END, f"   CVaR 95%: {cvar_95:.2f}%\n")
                self.results_text.insert(tk.END, f"   Concentración de cola: {tail_conc:.2f}%\n")
                self.results_text.insert(tk.END, f"   Prob. pérdida extrema: {extreme_prob:.2f}%\n")
        
        # Análisis de portafolio
        portfolio_analysis = self.analysis_results.get("portfolio_analysis")
        if portfolio_analysis:
            self.results_text.insert(tk.END, "\n📈 ANÁLISIS DE PORTAFOLIO:\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n")
            
            avg_var = portfolio_analysis.get("average_var_95", np.nan)
            avg_cvar = portfolio_analysis.get("average_cvar_95", np.nan)
            max_var = portfolio_analysis.get("max_var_95", np.nan)
            
            self.results_text.insert(tk.END, f"   VaR promedio: {avg_var:.2f}%\n")
            self.results_text.insert(tk.END, f"   CVaR promedio: {avg_cvar:.2f}%\n")
            self.results_text.insert(tk.END, f"   VaR máximo: {max_var:.2f}%\n")
        
        # Alertas de riesgo
        risk_alerts = self.analysis_results.get("risk_alerts", [])
        if risk_alerts:
            self.results_text.insert(tk.END, "\n⚠️ ALERTAS DE RIESGO:\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n")
            
            for alert in risk_alerts:
                strategy = alert.get("strategy", "Unknown")
                alert_type = alert.get("alert_type", "Unknown")
                details = alert.get("details", "")
                
                self.results_text.insert(tk.END, f"   {strategy}: {alert_type}\n")
                self.results_text.insert(tk.END, f"   {details}\n")
        
        # Resumen
        self.results_text.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.results_text.insert(tk.END, f"✅ Análisis completado: {len(strategies_analysis)} estrategias analizadas\n")
        self.results_text.insert(tk.END, f"⚠️ Alertas generadas: {len(risk_alerts)}\n")
    
    def _show_detailed_results(self):
        """Muestra ventana detallada con resultados."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No hay resultados para mostrar.")
            return
        
        # Crear ventana detallada
        detail_window = tk.Toplevel(self.parent)
        detail_window.title("📊 Resultados Detallados - Tail Risk Analysis")
        detail_window.geometry("800x600")
        
        # Notebook para pestañas
        notebook = ttk.Notebook(detail_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de métricas por estrategia
        metrics_frame = ttk.Frame(notebook)
        notebook.add(metrics_frame, text="Métricas por Estrategia")
        
        # Crear tabla de métricas
        self._create_metrics_table(metrics_frame)
        
        # Pestaña de alertas
        alerts_frame = ttk.Frame(notebook)
        notebook.add(alerts_frame, text="Alertas de Riesgo")
        
        # Crear lista de alertas
        self._create_alerts_list(alerts_frame)
    
    def _create_metrics_table(self, parent):
        """Crea tabla de métricas detalladas."""
        # Crear Treeview
        columns = ("Estrategia", "VaR 95%", "CVaR 95%", "Tail Conc.", "Extreme Prob.")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Insertar datos
        strategies_analysis = self.analysis_results.get("strategies_analysis", [])
        for analysis in strategies_analysis:
            strategy_name = analysis.get("strategy_name", "Unknown")
            var_95 = analysis.get("var_95", np.nan)
            cvar_95 = analysis.get("cvar_95", np.nan)
            tail_conc = analysis.get("tail_concentration", np.nan)
            extreme_prob = analysis.get("extreme_loss_probability", np.nan)
            
            tree.insert("", "end", values=(
                strategy_name,
                f"{var_95:.2f}%" if not np.isnan(var_95) else "N/A",
                f"{cvar_95:.2f}%" if not np.isnan(cvar_95) else "N/A",
                f"{tail_conc:.2f}%" if not np.isnan(tail_conc) else "N/A",
                f"{extreme_prob:.2f}%" if not np.isnan(extreme_prob) else "N/A"
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_alerts_list(self, parent):
        """Crea lista de alertas de riesgo."""
        alerts_frame = ttk.Frame(parent)
        alerts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(alerts_frame, text="⚠️ Alertas de Riesgo Detectadas", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Lista de alertas
        risk_alerts = self.analysis_results.get("risk_alerts", [])
        if not risk_alerts:
            no_alerts_label = ttk.Label(alerts_frame, text="✅ No se detectaron alertas de riesgo críticas.")
            no_alerts_label.pack(pady=20)
        else:
            for alert in risk_alerts:
                alert_frame = ttk.Frame(alerts_frame)
                alert_frame.pack(fill=tk.X, pady=5)
                
                strategy = alert.get("strategy", "Unknown")
                alert_type = alert.get("alert_type", "Unknown")
                details = alert.get("details", "")
                
                ttk.Label(alert_frame, text=f"🔴 {strategy}: {alert_type}", font=("Arial", 10, "bold")).pack(anchor=tk.W)
                ttk.Label(alert_frame, text=f"   {details}", font=("Arial", 9)).pack(anchor=tk.W)
    
    def _export_tail_risk_report(self):
        """Exporta reporte de tail risk."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No hay resultados para exportar.")
            return
        
        try:
            # Crear reporte en formato texto
            report_content = self._generate_report_content()
            
            # Guardar archivo
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Guardar Reporte de Tail Risk"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                messagebox.showinfo(
                    "Éxito",
                    f"Reporte de Tail Risk exportado exitosamente a:\n{filename}"
                )
                
                logger.info(f"📤 Reporte de Tail Risk exportado: {filename}")
        
        except Exception as e:
            logger.error(f"❌ Error exportando reporte: {e}")
            messagebox.showerror("Error", f"Error al exportar reporte:\n{str(e)}")
    
    def _generate_report_content(self) -> str:
        """Genera contenido del reporte."""
        content = "REPORTE DE ANÁLISIS DE TAIL RISK\n"
        content += "=" * 50 + "\n\n"
        
        # Análisis por estrategia
        strategies_analysis = self.analysis_results.get("strategies_analysis", [])
        content += f"ESTRATEGIAS ANALIZADAS: {len(strategies_analysis)}\n"
        content += "-" * 30 + "\n\n"
        
        for analysis in strategies_analysis:
            strategy_name = analysis.get("strategy_name", "Unknown")
            content += f"Estrategia: {strategy_name}\n"
            
            for key, value in analysis.items():
                if key != "strategy_name":
                    if isinstance(value, float) and not np.isnan(value):
                        content += f"  {key}: {value:.4f}\n"
                    else:
                        content += f"  {key}: N/A\n"
            content += "\n"
        
        # Alertas
        risk_alerts = self.analysis_results.get("risk_alerts", [])
        if risk_alerts:
            content += "ALERTAS DE RIESGO:\n"
            content += "-" * 20 + "\n"
            for alert in risk_alerts:
                content += f"- {alert['strategy']}: {alert['alert_type']}\n"
                content += f"  {alert['details']}\n"
        
        return content
    
    def _clear_results(self):
        """Limpia los resultados del análisis."""
        self.analysis_results = None
        self.results_text.delete(1.0, tk.END)
        self.visualize_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        logger.info("🧹 Resultados de Tail Risk Analysis limpiados") 