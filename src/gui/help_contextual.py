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
    
    def _initialize_help_content(self) -> dict:
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
                    "predictibilidad": {
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
                "title": "❓ Preguntas Frecuentes (FAQ)",
                "content": {
                    "general": {
                        "title": "🤔 Preguntas Generales",
                        "questions": {
                            "¿Qué es QVA Strategy Studio?": {
                                "answer": "QVA Strategy Studio es una aplicación profesional para análisis cuantitativo de estrategias de trading. Permite evaluar, comparar y seleccionar estrategias basándose en métricas avanzadas como Factor K, predictibilidad, Sharpe ratio y más.",
                                "tags": ["general", "introduccion"]
                            },
                            "¿Cómo interpreto los resultados?": {
                                "answer": "Los resultados se presentan con badges visuales (🥇🥈🥉⭐⚠️❌) y colores automáticos. Las estrategias Elite (🥇) son las mejores, seguidas por Excellent (🥈), Very Good (🥉), etc. La fila sticky muestra la mejor estrategia.",
                                "tags": ["interpretacion", "resultados"]
                            },
                            "¿Qué métricas son más importantes?": {
                                "answer": "Factor K es la métrica principal (evalúa calidad general). Predictibilidad indica estabilidad futura. Sharpe ratio mide rendimiento vs riesgo. Drawdown indica el peor escenario. Todas son importantes, evalúa en conjunto.",
                                "tags": ["metricas", "importancia"]
                            }
                        }
                    },
                    "tecnicas": {
                        "title": "⚙️ Preguntas Técnicas",
                        "questions": {
                            "¿Qué formato de archivo necesito?": {
                                "answer": "La aplicación acepta archivos CSV con delimitador ';' y decimal ','. Las columnas deben incluir: Strategy Name, FactorK, CAGR, Sharpe, MaxDD, Trades, etc. Ver plantilla en la documentación.",
                                "tags": ["formato", "archivos"]
                            },
                            "¿Cómo configuro los filtros?": {
                                "answer": "Usa los filtros rápidos para rangos básicos o '🔍 Filtros Avanzados' para configuración detallada. Puedes filtrar por Factor K, predictibilidad, Sharpe, drawdown, y más. Los filtros se aplican en tiempo real.",
                                "tags": ["filtros", "configuracion"]
                            },
                            "¿Puedo exportar los resultados?": {
                                "answer": "Sí, puedes exportar a Excel (múltiples hojas), HTML (dashboard interactivo), PDF (reportes profesionales), y archivos .sqx. Usa '📤 Exportación Avanzada' para opciones completas.",
                                "tags": ["exportacion", "resultados"]
                            }
                        }
                    },
                    "analisis": {
                        "title": "🧪 Preguntas de Análisis",
                        "questions": {
                            "¿Qué es el análisis científico?": {
                                "answer": "Incluye análisis de Tail Risk (VaR, CVaR), AXISelect (selección de activos), análisis científico avanzado, y asesor financiero inteligente. Proporciona insights profundos sobre las estrategias.",
                                "tags": ["analisis", "cientifico"]
                            },
                            "¿Cómo interpreto la predictibilidad?": {
                                "answer": "La predictibilidad mide la estabilidad futura. EXCELENTE (≥85%) indica alta confiabilidad, BUENA (70-84%) buena estabilidad, etc. Valores altos sugieren estrategias más confiables.",
                                "tags": ["predictibilidad", "interpretacion"]
                            },
                            "¿Qué significa Factor K Elite 9.6?": {
                                "answer": "Factor K es una métrica compuesta que evalúa calidad general. Considera Estabilidad (S), Crecimiento (G), Eficiencia (E) y Consistencia (C). Elite (≥9.2) indica estrategias excepcionales.",
                                "tags": ["factor_k", "metricas"]
                            }
                        }
                    },
                    "troubleshooting": {
                        "title": "🔧 Solución de Problemas",
                        "questions": {
                            "¿Qué hago si no se cargan los datos?": {
                                "answer": "Verifica el formato del archivo CSV (delimitador ';', decimal ','). Asegúrate de que las columnas requeridas estén presentes. Revisa el log de errores para detalles específicos.",
                                "tags": ["carga", "errores"]
                            },
                            "¿Por qué no aparecen resultados después de filtrar?": {
                                "answer": "Los filtros pueden ser muy restrictivos. Prueba relajando los criterios o usando 'Limpiar Filtros'. Verifica que los rangos de valores sean apropiados para tus datos.",
                                "tags": ["filtros", "resultados"]
                            },
                            "¿Cómo actualizo la aplicación?": {
                                "answer": "Descarga la última versión desde el repositorio oficial. Respeta la estructura de carpetas y archivos de configuración. Consulta la documentación de actualización para detalles.",
                                "tags": ["actualizacion", "version"]
                            }
                        }
                    }
                }
            }
        }
    
    def show_help_panel(self, section: str = "metricas"):
        """Muestra el panel de ayuda contextual."""
        try:
            if self.help_window is not None:
                self.help_window.destroy()
            
            self.help_window = tk.Toplevel(self.parent)
            self.help_window.title("❓ Ayuda Contextual - QVA Strategy Studio")
            self.help_window.geometry("900x700")
            self.help_window.resizable(True, True)
            
            # Configurar estilo
            style = ttk.Style()
            style.configure('HelpTitle.TLabel', font=('Arial', 14, 'bold'))
            style.configure('HelpSection.TLabel', font=('Arial', 12, 'bold'))
            style.configure('HelpContent.TLabel', font=('Arial', 10))
            
            # Construir interfaz
            self._build_help_interface(section)
            
            # Centrar ventana
            self.help_window.transient(self.parent)
            self.help_window.grab_set()
            
            logger.info(f"✅ Panel de ayuda contextual mostrado (sección: {section})")
            
        except Exception as e:
            logger.error(f"Error mostrando panel de ayuda: {e}")
            messagebox.showerror("Error", f"Error mostrando ayuda: {e}")
    
    def _build_help_interface(self, initial_section: str):
        """Construye la interfaz del panel de ayuda."""
        # Frame principal
        main_frame = ttk.Frame(self.help_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel de navegación (izquierda)
        nav_frame = ttk.Frame(main_frame, width=250)
        nav_frame.pack(side="left", fill="y", padx=(0, 10))
        nav_frame.pack_propagate(False)
        
        self._build_navigation_panel(nav_frame, initial_section)
        
        # Panel de contenido (derecha)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side="right", fill="both", expand=True)
        
        self._build_content_panel(content_frame, initial_section)
    
    def _build_navigation_panel(self, parent: ttk.Frame, initial_section: str):
        """Construye el panel de navegación."""
        # Título
        title_label = ttk.Label(parent, text="📚 Ayuda Contextual", 
                               style="HelpTitle.TLabel")
        title_label.pack(pady=(0, 15))
        
        # Botones de navegación
        for section_key, section_data in self.help_content.items():
            btn = ttk.Button(
                parent,
                text=section_data["title"],
                command=lambda s=section_key: self._show_section_content(s)
            )
            btn.pack(fill="x", pady=2)
            
        # Separador
        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)
        
        # Botón de cerrar
        close_btn = ttk.Button(
            parent,
            text="❌ Cerrar",
            command=(self.help_window.destroy if self.help_window is not None else lambda: None)
        )
        close_btn.pack(fill="x", pady=5)
    
    def _build_content_panel(self, parent: ttk.Frame, initial_section: str):
        """Construye el panel de contenido."""
        # Frame con scroll
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar contenido inicial
        self._show_section_content(initial_section, scrollable_frame)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _show_section_content(self, section: str, parent_frame: ttk.Frame = None):
        """Muestra el contenido de una sección."""
        try:
            if parent_frame is None:
                logger.error(f"No se encontró un parent_frame válido para mostrar la sección {section}.")
                return
            # Limpiar contenido anterior
            for widget in parent_frame.winfo_children():
                widget.destroy()
            
            section_data = self.help_content[section]
            
            # Título de sección
            section_title = ttk.Label(
                parent_frame,
                text=section_data["title"],
                style="HelpTitle.TLabel"
            )
            section_title.pack(pady=(0, 20))
            
            # Contenido específico según sección
            if section == "metricas":
                self._show_metrics_content(section_data["content"], parent_frame)
            elif section == "interpretacion":
                self._show_interpretation_content(section_data["content"], parent_frame)
            elif section == "tutoriales":
                self._show_tutorials_content(section_data["content"], parent_frame)
            elif section == "faq":
                self._show_faq_content(section_data["content"], parent_frame)
            
            self.current_section = section
            
        except Exception as e:
            logger.error(f"Error mostrando contenido de sección {section}: {e}")
    
    def _show_metrics_content(self, content: Dict[str, Any], parent: ttk.Frame):
        """Muestra el contenido de métricas."""
        for metric_key, metric_data in content.items():
            # Frame para cada métrica
            metric_frame = ttk.LabelFrame(parent, text=metric_data["title"])
            metric_frame.pack(fill="x", pady=5)
            
            # Descripción
            desc_label = ttk.Label(
                metric_frame,
                text=metric_data["description"],
                style="HelpContent.TLabel",
                wraplength=600
            )
            desc_label.pack(pady=5)
            
            # Componentes específicos según métrica
            if "components" in metric_data:
                comp_label = ttk.Label(
                    metric_frame,
                    text="Componentes:",
                    style="HelpSection.TLabel"
                )
                comp_label.pack(anchor="w", padx=10)
                
                for component in metric_data["components"]:
                    comp_item = ttk.Label(
                        metric_frame,
                        text=f"• {component}",
                        style="HelpContent.TLabel"
                    )
                    comp_item.pack(anchor="w", padx=20)
            
            # Categorías
            if "categories" in metric_data:
                cat_label = ttk.Label(
                    metric_frame,
                    text="Categorías:",
                    style="HelpSection.TLabel"
                )
                cat_label.pack(anchor="w", padx=10, pady=(10, 0))
                
                for category in metric_data["categories"]:
                    cat_item = ttk.Label(
                        metric_frame,
                        text=f"• {category}",
                        style="HelpContent.TLabel"
                    )
                    cat_item.pack(anchor="w", padx=20)
            
            # Interpretación
            if "interpretation" in metric_data:
                int_label = ttk.Label(
                    metric_frame,
                    text="Interpretación:",
                    style="HelpSection.TLabel"
                )
                int_label.pack(anchor="w", padx=10, pady=(10, 0))
                
                for interpretation in metric_data["interpretation"]:
                    int_item = ttk.Label(
                        metric_frame,
                        text=f"• {interpretation}",
                        style="HelpContent.TLabel"
                    )
                    int_item.pack(anchor="w", padx=20)
            
            # Fórmula
                if "formula" in metric_data:
                formula_label = ttk.Label(
                    metric_frame,
                    text=f"Fórmula: {metric_data['formula']}",
                    style="HelpContent.TLabel"
                )
                formula_label.pack(anchor="w", padx=10, pady=(10, 0))
    
    def _show_interpretation_content(self, content: Dict[str, Any], parent: ttk.Frame):
        """Muestra el contenido de interpretación."""
        for interpret_key, interpret_data in content.items():
            # Frame para cada interpretación
            interpret_frame = ttk.LabelFrame(parent, text=interpret_data["title"])
            interpret_frame.pack(fill="x", pady=5)
            
            # Descripción
            desc_label = ttk.Label(
                interpret_frame,
                text=interpret_data["description"],
                style="HelpContent.TLabel",
                wraplength=600
            )
            desc_label.pack(pady=5)
            
            # Badges
            if "badges" in interpret_data:
                badges_label = ttk.Label(
                    interpret_frame,
                    text="Badges:",
                    style="HelpSection.TLabel"
                )
                badges_label.pack(anchor="w", padx=10, pady=(10, 0))
                
                for badge, description in interpret_data["badges"].items():
                    badge_item = ttk.Label(
                        interpret_frame,
                        text=f"{badge} {description}",
                        style="HelpContent.TLabel"
                    )
                    badge_item.pack(anchor="w", padx=20)
            
            # Criterios
            if "criteria" in interpret_data:
                criteria_label = ttk.Label(
                    interpret_frame,
                    text="Criterios:",
                    style="HelpSection.TLabel"
                )
                criteria_label.pack(anchor="w", padx=10, pady=(10, 0))
                
                for criterion in interpret_data["criteria"]:
                    crit_item = ttk.Label(
                        interpret_frame,
                        text=f"• {criterion}",
                        style="HelpContent.TLabel"
                    )
                    crit_item.pack(anchor="w", padx=20)
            
            # Colores
            if "colors" in interpret_data:
                colors_label = ttk.Label(
                    interpret_frame,
                    text="Colores:",
                    style="HelpSection.TLabel"
                )
                colors_label.pack(anchor="w", padx=10, pady=(10, 0))
                
                for category, color in interpret_data["colors"].items():
                    color_item = ttk.Label(
                        interpret_frame,
                        text=f"• {category}: {color}",
                        style="HelpContent.TLabel"
                    )
                    color_item.pack(anchor="w", padx=20)
    
    def _show_tutorials_content(self, content: Dict[str, Any], parent: ttk.Frame):
        """Muestra el contenido de tutoriales."""
        for tutorial_key, tutorial_data in content.items():
            # Frame para cada tutorial
            tutorial_frame = ttk.LabelFrame(parent, text=tutorial_data["title"])
            tutorial_frame.pack(fill="x", pady=5)
            
            # Pasos
            for step in tutorial_data["steps"]:
                step_item = ttk.Label(
                    tutorial_frame,
                    text=step,
                    style="HelpContent.TLabel"
                )
                step_item.pack(anchor="w", padx=10, pady=2)
    
    def _show_faq_content(self, content: Dict[str, Any], parent: ttk.Frame):
        """Muestra el contenido del FAQ."""
        for faq_key, faq_data in content.items():
            # Frame para cada categoría de FAQ
            faq_frame = ttk.LabelFrame(parent, text=faq_data["title"])
            faq_frame.pack(fill="x", pady=5)
            
            # Preguntas y respuestas
            for question, answer_data in faq_data["questions"].items():
                # Pregunta
                question_label = ttk.Label(
                    faq_frame,
                    text=f"❓ {question}",
                    style="HelpSection.TLabel"
                )
                question_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Respuesta
                answer_label = ttk.Label(
                    faq_frame,
                    text=answer_data["answer"],
                    style="HelpContent.TLabel",
                    wraplength=600
                )
                answer_label.pack(anchor="w", padx=20, pady=(0, 10))
    
    def show_contextual_help(self, topic: str):
        """Muestra ayuda contextual para un tema específico."""
        try:
            # Mapear temas a secciones
            topic_mapping = {
                "factor_k": "metricas",
                "predictibilidad": "metricas", 
                "sharpe": "metricas",
                "drawdown": "metricas",
                "cagr": "metricas",
                "badges": "interpretacion",
                "filtros": "tutoriales",
                "carga": "tutoriales",
                "exportacion": "tutoriales",
                "errores": "faq"
            }
            
            section = topic_mapping.get(topic, "metricas")
            self.show_help_panel(section)
            
            logger.info(f"✅ Ayuda contextual mostrada para tema: {topic}")
            
        except Exception as e:
            logger.error(f"Error mostrando ayuda contextual: {e}")

def create_help_contextual_panel(parent: tk.Tk) -> HelpContextualPanel:
    """Crea y retorna una instancia del panel de ayuda contextual."""
    return HelpContextualPanel(parent) 