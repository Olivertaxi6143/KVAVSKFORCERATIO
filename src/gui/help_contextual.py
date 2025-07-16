"""
Panel de Ayuda Contextual
Proporciona información detallada y guías de interpretación para la GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class HelpContextualPanel:
    """
    Panel de ayuda contextual profesional para la GUI.
    
    Características:
    - Información detallada sobre métricas
    - Guías de interpretación
    - Tutoriales paso a paso
    - FAQ dinámico
    """
    
    def __init__(self, parent: tk.Tk):
        """Inicializa el panel de ayuda contextual."""
        self.parent = parent
        self.help_window = None
        self.current_section = None
        
        # Contenido de ayuda organizado por secciones
        self.help_content = self._initialize_help_content()
        
        logger.info("✅ HelpContextualPanel inicializado")
    
    def _initialize_help_content(self) -> Dict[str, Dict[str, str]]:
        """Inicializa el contenido de ayuda organizado."""
        return {
            "metricas": {
                "title": "📊 Métricas y KPIs",
                "content": {
                    "factor_k": {
                        "title": "🏆 Factor K Elite 9.6",
                        "description": "Métrica compuesta que evalúa la calidad general de la estrategia.",
                        "components": [
                            "S (Stability): Estabilidad de rendimientos",
                            "G (Growth): Crecimiento consistente", 
                            "E (Efficiency): Eficiencia operativa",
                            "C (Consistency): Consistencia temporal"
                        ],
                        "categories": [
                            "Elite (≥9.2): Estrategias excepcionales",
                            "Excellent (≥8.2): Estrategias muy buenas",
                            "Very Good (≥7.2): Estrategias buenas",
                            "Good (≥6.2): Estrategias aceptables",
                            "Poor (<6.2): Estrategias con problemas"
                        ],
                        "regime_weights": {
                            "Bull": "30% S, 40% G, 20% E, 10% C",
                            "Bear": "40% S, 20% G, 30% E, 10% C",
                            "Sideways": "35% S, 25% G, 25% E, 15% C",
                            "Crisis": "50% S, 10% G, 30% E, 10% C"
                        }
                    },
                    "predictabilidad": {
                        "title": "🎯 Predictibilidad",
                        "description": "Evalúa la capacidad de la estrategia para mantener su rendimiento en datos futuros.",
                        "scales": [
                            "EXCELENTE (≥85%): Alta confiabilidad",
                            "BUENA (70-84%): Buena estabilidad",
                            "ACEPTABLE (60-69%): Estabilidad moderada",
                            "BAJA (<60%): Riesgo de inestabilidad"
                        ],
                        "factors": [
                            "Consistencia IS/OOS",
                            "Robustez temporal",
                            "Estabilidad de parámetros",
                            "Correlación de rendimientos"
                        ]
                    },
                    "sharpe": {
                        "title": "📈 Sharpe Ratio",
                        "description": "Mide el rendimiento ajustado por riesgo de la estrategia.",
                        "interpretation": [
                            "≥2.0: Excelente (rendimiento superior)",
                            "1.5-2.0: Muy bueno",
                            "1.0-1.5: Bueno",
                            "0.5-1.0: Aceptable",
                            "<0.5: Pobre"
                        ],
                        "formula": "Sharpe = (Retorno - Tasa Libre de Riesgo) / Desviación Estándar"
                    },
                    "drawdown": {
                        "title": "📉 Máximo Drawdown",
                        "description": "La mayor pérdida desde un pico hasta un valle.",
                        "interpretation": [
                            "<10%: Excelente (bajo riesgo)",
                            "10-20%: Bueno",
                            "20-30%: Aceptable",
                            "30-50%: Alto riesgo",
                            ">50%: Muy alto riesgo"
                        ]
                    },
                    "cagr": {
                        "title": "📊 CAGR (Compound Annual Growth Rate)",
                        "description": "Tasa de crecimiento anual compuesto de la estrategia.",
                        "interpretation": [
                            ">20%: Excelente crecimiento",
                            "15-20%: Muy buen crecimiento",
                            "10-15%: Bueno crecimiento",
                            "5-10%: Crecimiento moderado",
                            "<5%: Crecimiento bajo"
                        ],
                        "formula": "CAGR = (Valor Final / Valor Inicial)^(1/años) - 1"
                    }
                }
            },
            "interpretacion": {
                "title": "🔍 Guías de Interpretación",
                "content": {
                    "badges_visuales": {
                        "title": "🏅 Badges Visuales",
                        "description": "Sistema de badges para categorizar estrategias visualmente.",
                        "badges": {
                            "🥇": "Elite - Estrategias excepcionales",
                            "🥈": "Excellent - Estrategias muy buenas",
                            "🥉": "Very Good - Estrategias buenas",
                            "⭐": "Good - Estrategias aceptables",
                            "⚠️": "Poor - Estrategias con problemas",
                            "❌": "Very Poor - Estrategias no recomendadas"
                        }
                    },
                    "fila_sticky": {
                        "title": "📌 Fila Sticky",
                        "description": "La mejor estrategia se mantiene visible en la parte superior.",
                        "criteria": [
                            "Factor K más alto",
                            "Predictibilidad excelente",
                            "Sharpe Ratio superior",
                            "Drawdown bajo"
                        ]
                    },
                    "colores_automaticos": {
                        "title": "🎨 Colores Automáticos",
                        "description": "Colores automáticos según la categoría de la estrategia.",
                        "colors": {
                            "Elite": "Verde dorado (#FFD700)",
                            "Excellent": "Verde (#32CD32)",
                            "Very Good": "Verde claro (#90EE90)",
                            "Good": "Amarillo (#FFFF00)",
                            "Poor": "Naranja (#FFA500)",
                            "Very Poor": "Rojo (#FF0000)"
                        }
                    }
                }
            },
            "tutoriales": {
                "title": "📚 Tutoriales Paso a Paso",
                "content": {
                    "carga_datos": {
                        "title": "📁 Carga de Datos",
                        "steps": [
                            "1. Hacer clic en '📁 Cargar Datos'",
                            "2. Seleccionar archivo CSV de estrategias",
                            "3. Esperar validación automática",
                            "4. Revisar estadísticas de carga",
                            "5. Confirmar datos cargados"
                        ]
                    },
                    "filtros_avanzados": {
                        "title": "🔍 Filtros Avanzados",
                        "steps": [
                            "1. Hacer clic en '🔍 Filtros Avanzados'",
                            "2. Configurar rangos de métricas",
                            "3. Aplicar filtros de categoría",
                            "4. Revisar resultados filtrados",
                            "5. Guardar configuración de filtros"
                        ]
                    },
                    "analisis_cientifico": {
                        "title": "🧪 Análisis Científico",
                        "steps": [
                            "1. Hacer clic en '🧪 Análisis Científico'",
                            "2. Seleccionar tipo de análisis",
                            "3. Configurar parámetros",
                            "4. Ejecutar análisis",
                            "5. Revisar resultados y gráficos"
                        ]
                    },
                    "exportacion": {
                        "title": "📤 Exportación",
                        "steps": [
                            "1. Hacer clic en '📤 Exportación Avanzada'",
                            "2. Seleccionar formato (Excel, HTML, PDF)",
                            "3. Configurar opciones de exportación",
                            "4. Seleccionar directorio de salida",
                            "5. Confirmar exportación"
                        ]
                    }
                }
            },
            "faq": {
                "title": "❓ Preguntas Frecuentes",
                "content": {
                    "mejor_estrategia": {
                        "question": "¿Cómo identifico la mejor estrategia?",
                        "answer": "La mejor estrategia combina Factor K alto (≥9.2), predictibilidad excelente (≥85%), Sharpe Ratio superior (≥2.0) y drawdown bajo (<10%)."
                    },
                    "interpretar_predictibilidad": {
                        "question": "¿Cómo interpreto la predictibilidad?",
                        "answer": "La predictibilidad indica qué tan confiable será la estrategia en datos futuros. Valores ≥85% son excelentes, mientras que <60% indican alto riesgo."
                    },
                    "filtros_eficientes": {
                        "question": "¿Qué filtros son más eficientes?",
                        "answer": "Comience con Factor K ≥7.0, Sharpe ≥1.0 y drawdown ≤20%. Luego refine según sus criterios específicos."
                    },
                    "exportar_resultados": {
                        "question": "¿Cómo exporto mis resultados?",
                        "answer": "Use '📤 Exportación Avanzada' para Excel con múltiples hojas, o '📤 Exportar .SQX' para archivos de estrategia."
                    },
                    "optimizar_performance": {
                        "question": "¿Cómo optimizo el rendimiento?",
                        "answer": "Use filtros para reducir el dataset, cierre ventanas innecesarias y use análisis por lotes para datasets grandes."
                    }
                }
            }
        }
    
    def show_help_panel(self, section: str = "metricas"):
        """Muestra el panel de ayuda contextual."""
        try:
            # Cerrar ventana anterior si existe
            if self.help_window:
                self.help_window.destroy()
            
            # Crear nueva ventana
            self.help_window = tk.Toplevel(self.parent)
            self.help_window.title("❓ Ayuda Contextual - QVA Strategy Studio")
            self.help_window.geometry("800x600")
            self.help_window.resizable(True, True)
            
            # Configurar ventana
            self.help_window.transient(self.parent)
            self.help_window.grab_set()
            
            # Construir interfaz
            self._build_help_interface(section)
            
            logger.info(f"✅ Panel de ayuda mostrado - Sección: {section}")
            
        except Exception as e:
            logger.error(f"Error mostrando panel de ayuda: {e}")
            messagebox.showerror("Error", f"Error mostrando ayuda: {e}")
    
    def _build_help_interface(self, initial_section: str):
        """Construye la interfaz del panel de ayuda."""
        # Frame principal
        main_frame = ttk.Frame(self.help_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel izquierdo (navegación)
        self._build_navigation_panel(main_frame, initial_section)
        
        # Panel derecho (contenido)
        self._build_content_panel(main_frame, initial_section)
    
    def _build_navigation_panel(self, parent: ttk.Frame, initial_section: str):
        """Construye el panel de navegación."""
        nav_frame = ttk.Frame(parent, width=200)
        nav_frame.pack(side="left", fill="y", padx=(0, 10))
        nav_frame.pack_propagate(False)
        
        # Título
        ttk.Label(nav_frame, text="📚 Secciones de Ayuda", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Lista de secciones
        sections_frame = ttk.Frame(nav_frame)
        sections_frame.pack(fill="both", expand=True)
        
        # Crear botones para cada sección
        for section_key, section_data in self.help_content.items():
            btn = ttk.Button(
                sections_frame,
                text=section_data["title"],
                command=lambda s=section_key: self._show_section_content(s)
            )
            btn.pack(fill="x", pady=2)
            
            # Marcar sección inicial como seleccionada
            if section_key == initial_section:
                btn.state(['pressed'])
        
        # Botón de cerrar
        ttk.Button(nav_frame, text="❌ Cerrar", 
                  command=self.help_window.destroy).pack(pady=(10, 0))
    
    def _build_content_panel(self, parent: ttk.Frame, initial_section: str):
        """Construye el panel de contenido."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(side="right", fill="both", expand=True)
        
        # Área de contenido con scroll
        self.content_canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.content_canvas.yview)
        self.content_text = tk.Text(self.content_canvas, wrap="word", padx=10, pady=10)
        
        # Configurar scroll
        self.content_text.configure(yscrollcommand=scrollbar.set)
        self.content_canvas.create_window((0, 0), window=self.content_text, anchor="nw")
        
        # Layout
        self.content_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll
        self.content_text.bind("<Configure>", lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all")))
        
        # Mostrar contenido inicial
        self._show_section_content(initial_section)
    
    def _show_section_content(self, section: str):
        """Muestra el contenido de una sección específica."""
        try:
            # Limpiar contenido anterior
            self.content_text.delete(1.0, tk.END)
            
            if section not in self.help_content:
                self.content_text.insert(tk.END, "❌ Sección no encontrada")
                return
            
            section_data = self.help_content[section]
            
            # Título de la sección
            self.content_text.insert(tk.END, f"{section_data['title']}\n", "title")
            self.content_text.insert(tk.END, "=" * 50 + "\n\n", "separator")
            
            # Contenido de la sección
            if section == "metricas":
                self._show_metrics_content(section_data["content"])
            elif section == "interpretacion":
                self._show_interpretation_content(section_data["content"])
            elif section == "tutoriales":
                self._show_tutorials_content(section_data["content"])
            elif section == "faq":
                self._show_faq_content(section_data["content"])
            
            # Configurar tags para formato
            self.content_text.tag_configure("title", font=("Arial", 14, "bold"))
            self.content_text.tag_configure("subtitle", font=("Arial", 12, "bold"))
            self.content_text.tag_configure("separator", font=("Arial", 10))
            self.content_text.tag_configure("highlight", background="yellow")
            
            self.current_section = section
            
        except Exception as e:
            logger.error(f"Error mostrando contenido de sección {section}: {e}")
            self.content_text.insert(tk.END, f"❌ Error cargando contenido: {e}")
    
    def _show_metrics_content(self, content: Dict[str, Any]):
        """Muestra contenido de métricas."""
        for metric_key, metric_data in content.items():
            # Título de la métrica
            self.content_text.insert(tk.END, f"{metric_data['title']}\n", "subtitle")
            self.content_text.insert(tk.END, f"{metric_data['description']}\n\n")
            
            # Componentes específicos según la métrica
            if metric_key == "factor_k":
                self.content_text.insert(tk.END, "📋 Componentes:\n", "subtitle")
                for component in metric_data["components"]:
                    self.content_text.insert(tk.END, f"• {component}\n")
                
                self.content_text.insert(tk.END, "\n🏆 Categorías:\n", "subtitle")
                for category in metric_data["categories"]:
                    self.content_text.insert(tk.END, f"• {category}\n")
                
                self.content_text.insert(tk.END, "\n⚖️ Pesos por Régimen:\n", "subtitle")
                for regime, weights in metric_data["regime_weights"].items():
                    self.content_text.insert(tk.END, f"• {regime}: {weights}\n")
            
            elif metric_key == "predictabilidad":
                self.content_text.insert(tk.END, "📊 Escalas:\n", "subtitle")
                for scale in metric_data["scales"]:
                    self.content_text.insert(tk.END, f"• {scale}\n")
                
                self.content_text.insert(tk.END, "\n🔍 Factores:\n", "subtitle")
                for factor in metric_data["factors"]:
                    self.content_text.insert(tk.END, f"• {factor}\n")
            
            elif metric_key in ["sharpe", "drawdown", "cagr"]:
                if "interpretation" in metric_data:
                    self.content_text.insert(tk.END, "📈 Interpretación:\n", "subtitle")
                    for interpretation in metric_data["interpretation"]:
                        self.content_text.insert(tk.END, f"• {interpretation}\n")
                
                if "formula" in metric_data:
                    self.content_text.insert(tk.END, f"\n🧮 Fórmula:\n{metric_data['formula']}\n")
            
            self.content_text.insert(tk.END, "\n" + "-" * 40 + "\n\n")
    
    def _show_interpretation_content(self, content: Dict[str, Any]):
        """Muestra contenido de interpretación."""
        for item_key, item_data in content.items():
            # Título del item
            self.content_text.insert(tk.END, f"{item_data['title']}\n", "subtitle")
            self.content_text.insert(tk.END, f"{item_data['description']}\n\n")
            
            # Contenido específico
            if item_key == "badges_visuales":
                self.content_text.insert(tk.END, "🏅 Badges Disponibles:\n", "subtitle")
                for badge, description in item_data["badges"].items():
                    self.content_text.insert(tk.END, f"• {badge} {description}\n")
            
            elif item_key == "colores_automaticos":
                self.content_text.insert(tk.END, "🎨 Esquema de Colores:\n", "subtitle")
                for category, color in item_data["colors"].items():
                    self.content_text.insert(tk.END, f"• {category}: {color}\n")
            
            elif item_key == "fila_sticky":
                self.content_text.insert(tk.END, "📌 Criterios de Selección:\n", "subtitle")
                for criterion in item_data["criteria"]:
                    self.content_text.insert(tk.END, f"• {criterion}\n")
            
            self.content_text.insert(tk.END, "\n" + "-" * 40 + "\n\n")
    
    def _show_tutorials_content(self, content: Dict[str, Any]):
        """Muestra contenido de tutoriales."""
        for tutorial_key, tutorial_data in content.items():
            # Título del tutorial
            self.content_text.insert(tk.END, f"{tutorial_data['title']}\n", "subtitle")
            self.content_text.insert(tk.END, "\n📝 Pasos a seguir:\n\n")
            
            # Pasos del tutorial
            for i, step in enumerate(tutorial_data["steps"], 1):
                self.content_text.insert(tk.END, f"{step}\n")
                if i < len(tutorial_data["steps"]):
                    self.content_text.insert(tk.END, "\n")
            
            self.content_text.insert(tk.END, "\n" + "-" * 40 + "\n\n")
    
    def _show_faq_content(self, content: Dict[str, Any]):
        """Muestra contenido de FAQ."""
        for faq_key, faq_data in content.items():
            # Pregunta
            self.content_text.insert(tk.END, f"❓ {faq_data['question']}\n", "subtitle")
            
            # Respuesta
            self.content_text.insert(tk.END, f"💡 {faq_data['answer']}\n\n")
            
            self.content_text.insert(tk.END, "-" * 40 + "\n\n")
    
    def show_contextual_help(self, topic: str):
        """Muestra ayuda contextual para un tema específico."""
        try:
            # Mapear temas a secciones
            topic_mapping = {
                "factor_k": "metricas",
                "predictabilidad": "metricas", 
                "sharpe": "metricas",
                "drawdown": "metricas",
                "cagr": "metricas",
                "badges": "interpretacion",
                "colores": "interpretacion",
                "sticky": "interpretacion",
                "tutorial": "tutoriales",
                "faq": "faq"
            }
            
            section = topic_mapping.get(topic, "metricas")
            self.show_help_panel(section)
            
            logger.info(f"✅ Ayuda contextual mostrada para tema: {topic}")
            
        except Exception as e:
            logger.error(f"Error mostrando ayuda contextual: {e}")
            messagebox.showerror("Error", f"Error mostrando ayuda: {e}")

def create_help_contextual_panel(parent: tk.Tk) -> HelpContextualPanel:
    """Crea una instancia del panel de ayuda contextual."""
    return HelpContextualPanel(parent) 