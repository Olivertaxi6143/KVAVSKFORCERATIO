"""
Pestaña de AXI Select Analysis para QVA Strategy Studio
Integra el módulo AXISelectAnalysis con interfaz profesional.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from src.analysis.axi_select_analysis import AXISelectPredictiveSystem, ModelType
from src.data.data_utils import clean_returns

logger = logging.getLogger(__name__)

class AXISelectTab:
    """Pestaña profesional para análisis AXI Select."""
    
    def __init__(self, parent_frame):
        """Inicializa la pestaña de AXI Select Analysis."""
        self.parent = parent_frame
        self.axi_system = AXISelectPredictiveSystem()
        self.current_data = None
        self.analysis_results = None
        
        self._create_widgets()
        logger.info("🎯 Pestaña AXI Select Analysis inicializada")
    
    def _create_widgets(self):
        """Crea los widgets de la interfaz."""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(
            self.main_frame, 
            text="🎯 AXI Select Analysis", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(self.main_frame, text="Controles de Análisis", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botón de análisis
        self.analyze_btn = ttk.Button(
            controls_frame,
            text="🎯 Ejecutar AXI Select Analysis",
            command=self._run_axi_analysis
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
            command=self._export_axi_report,
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
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(self.main_frame, text="Configuración de Modelos", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Checkboxes para tipos de modelos
        self.model_vars = {}
        model_types = [
            ("Random Forest", "random_forest"),
            ("Linear Regression", "linear_regression"),
            ("Gradient Boosting", "gradient_boosting"),
            ("MLP Sklearn", "mlp_sklearn"),
            ("LightGBM", "lightgbm"),
            ("CatBoost", "catboost"),
            ("PyTorch NN", "pytorch_nn")
        ]
        
        for i, (name, key) in enumerate(model_types):
            var = tk.BooleanVar(value=True)
            self.model_vars[key] = var
            ttk.Checkbutton(
                config_frame,
                text=name,
                variable=var
            ).grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
        
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
🎯 AXI SELECT ANALYSIS

Este módulo implementa un sistema predictivo híbrido para selección de estrategias:

• Modelos Explicables: Random Forest, Linear Regression (SHAP)
• Modelos de Precisión: LightGBM, CatBoost, PyTorch NN
• Validación Walk-Forward: Robustez temporal
• Interpretabilidad: Feature importance y SHAP values
• Ensemble Predictions: Combinación inteligente de modelos

Target: Predicción de Factor K o CAGR futuro
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack()
    
    def set_data(self, data: pd.DataFrame):
        """Establece los datos para el análisis."""
        self.current_data = data
        logger.info(f"📊 Datos establecidos para AXI Select Analysis: {len(data)} estrategias")
    
    def _run_axi_analysis(self):
        """Ejecuta el análisis AXI Select."""
        if self.current_data is None or len(self.current_data) == 0:
            messagebox.showwarning(
                "Advertencia",
                "No hay datos disponibles para el análisis AXI Select.\n"
                "Por favor, carga datos de estrategias primero."
            )
            return
        
        try:
            self.analyze_btn.config(state=tk.DISABLED)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "🎯 Ejecutando análisis AXI Select...\n\n")
            self.parent.update()
            
            # Ejecutar análisis
            self.analysis_results = self._perform_axi_analysis()
            
            # Mostrar resultados
            self._display_results()
            
            # Habilitar botones
            self.visualize_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)
            
            logger.info("✅ Análisis AXI Select completado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error en análisis AXI Select: {e}")
            messagebox.showerror(
                "Error",
                f"Error durante el análisis AXI Select:\n{str(e)}"
            )
            self.analyze_btn.config(state=tk.NORMAL)
    
    def _perform_axi_analysis(self) -> Dict[str, Any]:
        """Realiza el análisis AXI Select."""
        results = {
            "models_performance": {},
            "feature_importance": {},
            "predictions": {},
            "ensemble_results": {},
            "shap_analysis": {},
            "recommendations": []
        }
        
        # Preparar datos para análisis
        analysis_data = self._prepare_analysis_data()
        
        if len(analysis_data) < 10:
            raise ValueError("Se requieren al menos 10 estrategias para el análisis")
        
        # Configurar modelos activos
        active_models = []
        for key, var in self.model_vars.items():
            if var.get():
                active_models.append(key)
        
        if not active_models:
            raise ValueError("Debe seleccionar al menos un tipo de modelo")
        
        # Ejecutar análisis predictivo
        target_column = 'Factor_K' if 'Factor_K' in analysis_data.columns else 'CAGR_IS'
        
        try:
            # Entrenar y predecir
            self.axi_system.fit(analysis_data, target_column)
            predictions = self.axi_system.predict_hybrid(analysis_data, target_column)
            
            results["models_performance"] = predictions.get("model_performance", {})
            results["feature_importance"] = predictions.get("feature_importance", {})
            results["predictions"] = predictions.get("predictions", {})
            results["ensemble_results"] = predictions.get("ensemble_results", {})
            results["shap_analysis"] = predictions.get("shap_analysis", {})
            
            # Generar recomendaciones
            results["recommendations"] = self._generate_recommendations(predictions, analysis_data)
            
        except Exception as e:
            logger.error(f"Error en análisis predictivo: {e}")
            results["error"] = str(e)
        
        return results
    
    def _prepare_analysis_data(self) -> pd.DataFrame:
        """Prepara los datos para el análisis AXI Select."""
        if self.current_data is None:
            return pd.DataFrame()
        
        # Seleccionar columnas relevantes
        relevant_columns = [
            'Strategy_Name', 'Factor_K', 'CAGR_IS', 'Sharpe_Ratio_IS', 
            'Max_Drawdown_IS', 'Profit_Factor_IS', 'Total_Trades_IS',
            'Win_Rate_IS', 'Average_Trade_IS', 'Recovery_Factor_IS'
        ]
        
        # Filtrar columnas disponibles
        available_columns = [col for col in relevant_columns if col in self.current_data.columns]
        
        if len(available_columns) < 3:
            # Usar columnas básicas si no hay suficientes
            available_columns = ['Strategy_Name', 'Factor_K', 'CAGR_IS']
            available_columns = [col for col in available_columns if col in self.current_data.columns]
        
        analysis_data = self.current_data[available_columns].copy()
        
        # Limpiar datos
        analysis_data = analysis_data.dropna()
        
        # Convertir columnas numéricas
        for col in analysis_data.columns:
            if col != 'Strategy_Name':
                analysis_data[col] = pd.to_numeric(analysis_data[col], errors='coerce')
        
        # Eliminar filas con valores nulos
        analysis_data = analysis_data.dropna()
        
        return analysis_data
    
    def _generate_recommendations(self, predictions: Dict[str, Any], data: pd.DataFrame) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []
        
        try:
            # Análisis de performance de modelos
            model_performance = predictions.get("model_performance", {})
            if model_performance:
                best_model = max(model_performance.items(), key=lambda x: x[1].get('r2_score', 0))
                recommendations.append(f"Mejor modelo: {best_model[0]} (R²: {best_model[1].get('r2_score', 0):.3f})")
            
            # Análisis de feature importance
            feature_importance = predictions.get("feature_importance", {})
            if feature_importance:
                top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
                recommendations.append(f"Features más importantes: {', '.join([f[0] for f in top_features])}")
            
            # Análisis de confianza
            confidence = predictions.get("confidence", 0)
            if confidence > 0.8:
                recommendations.append("✅ Alta confianza en las predicciones")
            elif confidence > 0.6:
                recommendations.append("⚠️ Confianza moderada en las predicciones")
            else:
                recommendations.append("❌ Baja confianza en las predicciones")
            
            # Recomendaciones de estrategias
            if len(data) > 0:
                recommendations.append(f"📊 Analizadas {len(data)} estrategias")
                
                if 'Factor_K' in data.columns:
                    avg_factor_k = data['Factor_K'].mean()
                    recommendations.append(f"Factor K promedio: {avg_factor_k:.2f}")
                
                if 'CAGR_IS' in data.columns:
                    avg_cagr = data['CAGR_IS'].mean()
                    recommendations.append(f"CAGR promedio: {avg_cagr:.2f}%")
        
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")
            recommendations.append("⚠️ Error generando recomendaciones detalladas")
        
        return recommendations
    
    def _display_results(self):
        """Muestra los resultados del análisis."""
        if not self.analysis_results:
            return
        
        self.results_text.delete(1.0, tk.END)
        
        # Encabezado
        header = "🎯 RESULTADOS DEL ANÁLISIS AXI SELECT\n"
        header += "=" * 60 + "\n\n"
        self.results_text.insert(tk.END, header)
        
        # Performance de modelos
        models_performance = self.analysis_results.get("models_performance", {})
        if models_performance:
            self.results_text.insert(tk.END, "📊 PERFORMANCE DE MODELOS:\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n")
            
            for model_name, metrics in models_performance.items():
                self.results_text.insert(tk.END, f"\n🏆 Modelo: {model_name}\n")
                
                for metric, value in metrics.items():
                    if isinstance(value, float):
                        self.results_text.insert(tk.END, f"   {metric}: {value:.4f}\n")
                    else:
                        self.results_text.insert(tk.END, f"   {metric}: {value}\n")
        
        # Feature importance
        feature_importance = self.analysis_results.get("feature_importance", {})
        if feature_importance:
            self.results_text.insert(tk.END, "\n🎯 FEATURE IMPORTANCE:\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n")
            
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            for feature, importance in sorted_features[:10]:  # Top 10
                self.results_text.insert(tk.END, f"   {feature}: {importance:.4f}\n")
        
        # Recomendaciones
        recommendations = self.analysis_results.get("recommendations", [])
        if recommendations:
            self.results_text.insert(tk.END, "\n💡 RECOMENDACIONES:\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n")
            
            for rec in recommendations:
                self.results_text.insert(tk.END, f"   • {rec}\n")
        
        # Errores
        if "error" in self.analysis_results:
            self.results_text.insert(tk.END, "\n❌ ERRORES:\n")
            self.results_text.insert(tk.END, "-" * 40 + "\n")
            self.results_text.insert(tk.END, f"   {self.analysis_results['error']}\n")
        
        # Resumen
        self.results_text.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.results_text.insert(tk.END, f"✅ Análisis completado: {len(models_performance)} modelos evaluados\n")
        self.results_text.insert(tk.END, f"🎯 Features analizadas: {len(feature_importance)}\n")
        self.results_text.insert(tk.END, f"💡 Recomendaciones: {len(recommendations)}\n")
    
    def _show_detailed_results(self):
        """Muestra ventana detallada con resultados."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No hay resultados para mostrar.")
            return
        
        # Crear ventana detallada
        detail_window = tk.Toplevel(self.parent)
        detail_window.title("📊 Resultados Detallados - AXI Select Analysis")
        detail_window.geometry("900x700")
        
        # Notebook para pestañas
        notebook = ttk.Notebook(detail_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de performance de modelos
        performance_frame = ttk.Frame(notebook)
        notebook.add(performance_frame, text="Performance de Modelos")
        
        # Crear tabla de performance
        self._create_performance_table(performance_frame)
        
        # Pestaña de feature importance
        importance_frame = ttk.Frame(notebook)
        notebook.add(importance_frame, text="Feature Importance")
        
        # Crear gráfico de feature importance
        self._create_importance_chart(importance_frame)
        
        # Pestaña de predicciones
        predictions_frame = ttk.Frame(notebook)
        notebook.add(predictions_frame, text="Predicciones")
        
        # Crear tabla de predicciones
        self._create_predictions_table(predictions_frame)
    
    def _create_performance_table(self, parent):
        """Crea tabla de performance de modelos."""
        # Crear Treeview
        columns = ("Modelo", "R² Score", "MSE", "MAE", "Confianza")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Insertar datos
        models_performance = self.analysis_results.get("models_performance", {})
        for model_name, metrics in models_performance.items():
            r2 = metrics.get('r2_score', 0)
            mse = metrics.get('mse', 0)
            mae = metrics.get('mae', 0)
            confidence = metrics.get('confidence', 0)
            
            tree.insert("", "end", values=(
                model_name,
                f"{r2:.4f}",
                f"{mse:.4f}",
                f"{mae:.4f}",
                f"{confidence:.2f}"
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_importance_chart(self, parent):
        """Crea gráfico de feature importance."""
        feature_importance = self.analysis_results.get("feature_importance", {})
        
        if not feature_importance:
            ttk.Label(parent, text="No hay datos de feature importance disponibles.").pack(pady=20)
            return
        
        # Crear frame para el gráfico
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear Treeview para feature importance
        columns = ("Feature", "Importance", "Porcentaje")
        tree = ttk.Treeview(chart_frame, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Calcular total para porcentajes
        total_importance = sum(feature_importance.values())
        
        # Insertar datos ordenados
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features:
            percentage = (importance / total_importance * 100) if total_importance > 0 else 0
            
            tree.insert("", "end", values=(
                feature,
                f"{importance:.4f}",
                f"{percentage:.2f}%"
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(chart_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_predictions_table(self, parent):
        """Crea tabla de predicciones."""
        predictions = self.analysis_results.get("predictions", {})
        
        if not predictions:
            ttk.Label(parent, text="No hay predicciones disponibles.").pack(pady=20)
            return
        
        # Crear Treeview
        columns = ("Estrategia", "Predicción", "Confianza", "Modelo")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Insertar datos
        for strategy, pred_data in predictions.items():
            prediction = pred_data.get('prediction', 0)
            confidence = pred_data.get('confidence', 0)
            model = pred_data.get('model', 'Unknown')
            
            tree.insert("", "end", values=(
                strategy,
                f"{prediction:.4f}",
                f"{confidence:.2f}",
                model
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _export_axi_report(self):
        """Exporta reporte de AXI Select."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No hay resultados para exportar.")
            return
        
        try:
            # Crear reporte en formato texto
            report_content = self._generate_axi_report_content()
            
            # Guardar archivo
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Guardar Reporte de AXI Select"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                messagebox.showinfo(
                    "Éxito",
                    f"Reporte de AXI Select exportado exitosamente a:\n{filename}"
                )
                
                logger.info(f"📤 Reporte de AXI Select exportado: {filename}")
        
        except Exception as e:
            logger.error(f"❌ Error exportando reporte: {e}")
            messagebox.showerror("Error", f"Error al exportar reporte:\n{str(e)}")
    
    def _generate_axi_report_content(self) -> str:
        """Genera contenido del reporte de AXI Select."""
        content = "REPORTE DE ANÁLISIS AXI SELECT\n"
        content += "=" * 50 + "\n\n"
        
        # Información general
        models_performance = self.analysis_results.get("models_performance", {})
        feature_importance = self.analysis_results.get("feature_importance", {})
        recommendations = self.analysis_results.get("recommendations", [])
        
        content += f"MODELOS EVALUADOS: {len(models_performance)}\n"
        content += f"FEATURES ANALIZADAS: {len(feature_importance)}\n"
        content += f"RECOMENDACIONES: {len(recommendations)}\n\n"
        
        # Performance de modelos
        if models_performance:
            content += "PERFORMANCE DE MODELOS:\n"
            content += "-" * 30 + "\n"
            for model_name, metrics in models_performance.items():
                content += f"\nModelo: {model_name}\n"
                for metric, value in metrics.items():
                    if isinstance(value, float):
                        content += f"  {metric}: {value:.4f}\n"
                    else:
                        content += f"  {metric}: {value}\n"
        
        # Feature importance
        if feature_importance:
            content += "\nFEATURE IMPORTANCE:\n"
            content += "-" * 30 + "\n"
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            for feature, importance in sorted_features:
                content += f"  {feature}: {importance:.4f}\n"
        
        # Recomendaciones
        if recommendations:
            content += "\nRECOMENDACIONES:\n"
            content += "-" * 30 + "\n"
            for rec in recommendations:
                content += f"  • {rec}\n"
        
        return content
    
    def _clear_results(self):
        """Limpia los resultados del análisis."""
        self.analysis_results = None
        self.results_text.delete(1.0, tk.END)
        self.visualize_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        logger.info("🧹 Resultados de AXI Select Analysis limpiados") 