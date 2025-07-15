# 🏗️ GUI MODULAR ARCHITECTURE DIAGRAM - QVA Strategy Studio

## 📋 Resumen Ejecutivo

Este documento define la arquitectura técnica modular de la GUI, mostrando el flujo de datos, componentes y relaciones entre módulos para mantener la separación de responsabilidades y escalabilidad.

---

## 🔄 Diagrama de Flujo Principal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QVA STRATEGY STUDIO - FLUJO PRINCIPAL                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   INPUT     │───▶│   PROCESS   │───▶│   ANALYZE   │───▶│   OUTPUT    │ │
│  │   DATA      │    │   & CLEAN   │    │   & SCORE   │    │   & EXPORT  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                   │                   │                   │      │
│         ▼                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ • CSV Files │    │ • Validation│    │ • QVA Score │    │ • Excel     │ │
│  │ • SQX Files │    │ • Cleaning  │    │ • Factor K  │    │ • HTML      │ │
│  │ • Market    │    │ • Mapping   │    │ • Regime    │    │ • PDF       │ │
│  │ • Config    │    │ • Normalize │    │ • Risk      │    │ • SQX       │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DE COMPONENTES                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        PRESENTATION LAYER                          │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ MainWindow (tk.Tk)                                                 │    │
│  │ ├── Notebook (ttk.Notebook)                                        │    │
│  │ │   ├── DataTab (Step1LoadFrame)                                   │    │
│  │ │   ├── CoreTab (Step2ConfigureFrame)                              │    │
│  │ │   ├── ResultsTab (ResultsFrame)                                   │    │
│  │ │   ├── AdvancedTab (AdvancedFrame)                                 │    │
│  │ │   ├── AdvisorTab (AdvisorFrame)                                   │    │
│  │ │   ├── ExportTab (ExportFrame)                                     │    │
│  │ │   ├── HelpTab (HelpFrame)                                         │    │
│  │ │   └── LogsTab (LogsFrame)                                         │    │
│  │ └── StatusBar (ttk.Frame)                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        BUSINESS LOGIC LAYER                        │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ DataManager (data/data_manager.py)                                 │    │
│  │ ├── load_csv_data()                                                │    │
│  │ ├── validate_data()                                                │    │
│  │ ├── clean_data()                                                   │    │
│  │ └── export_data()                                                  │    │
│  │                                                                     │    │
│  │ ConfigManager (core/config/config_manager.py)                      │    │
│  │ ├── load_config()                                                  │    │
│  │ ├── save_config()                                                  │    │
│  │ ├── validate_config()                                              │    │
│  │ └── get_default_config()                                           │    │
│  │                                                                     │    │
│  │ QVAAnalyzer (core/analysis/qva_analyzer.py)                       │    │
│  │ ├── calculate_qva_score()                                          │    │
│  │ ├── analyze_regime()                                               │    │
│  │ ├── calculate_risk_metrics()                                       │    │
│  │ └── generate_report()                                              │    │
│  │                                                                     │    │
│  │ AdvancedModules (analysis/)                                        │    │
│  │ ├── DarwinEX (darwinex_pipeline.py)                               │    │
│  │ ├── AXISelect (axi_select_analysis.py)                            │    │
│  │ └── Advisor (asesor_financiero_inteligente.py)                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        DATA ACCESS LAYER                           │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ FileSystem (pathlib.Path)                                          │    │
│  │ ├── CSV Files                                                      │    │
│  │ ├── SQX Files                                                      │    │
│  │ ├── Config Files                                                   │    │
│  │ └── Output Files                                                   │    │
│  │                                                                     │    │
│  │ Database (SQLite/PostgreSQL)                                       │    │
│  │ ├── Strategies Table                                               │    │
│  │ ├── Analysis Results                                               │    │
│  │ ├── Configurations                                                 │    │
│  │ └── Logs                                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Diagrama de Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE DATOS DETALLADO                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   INPUT     │───▶│  VALIDATE   │───▶│   CLEAN     │───▶│   STORE     │ │
│  │   FILES     │    │   & MAP     │    │   & NORM    │    │   IN DB     │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                   │                   │                   │      │
│         ▼                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ • CSV       │    │ • Column    │    │ • Remove    │    │ • SQLite    │ │
│  │ • SQX       │    │   Mapping   │    │   Duplicates │    │ • Pandas    │ │
│  │ • Market    │    │ • Type      │    │ • Fix NaN   │    │ • JSON      │ │
│  │ • Config    │    │   Validation│    │ • Normalize │    │ • Pickle    │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   ANALYZE   │───▶│   SCORE     │───▶│   RANK      │───▶│   FILTER    │ │
│  │   CORE      │    │   QVA       │    │   & SORT    │    │   & SELECT  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                   │                   │                   │      │
│         ▼                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ • Factor K  │    │ • QVA       │    │ • Elite     │    │ • Top N     │ │
│  │ • Regime    │    │   Formula   │    │ • Excellent │    │ • Min Sharpe│ │
│  │ • Risk      │    │ • Adaptive  │    │ • Very Good │    │ • Max DD    │ │
│  │ • Metrics   │    │   Weights   │    │ • Good      │    │ • Min Trades│ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   ADVANCED  │───▶│   PORTFOLIO │───▶│   OPTIMIZE  │───▶│   EXPORT    │ │
│  │   MODULES   │    │   BUILD     │    │   WEIGHTS   │    │   REPORTS   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                   │                   │                   │      │
│         ▼                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ • DarwinEX  │    │ • Select    │    │ • Risk      │    │ • Excel     │ │
│  │ • AXI Select│    │   Strategies│    │   Parity    │    │ • HTML      │ │
│  │ • Advisor   │    │ • Calculate │    │ • Sharpe    │    │ • PDF       │ │
│  │ • ML        │    │   Weights   │    │   Ratio     │    │ • SQX       │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Diagrama de Módulos GUI

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MÓDULOS GUI - ESTRUCTURA DETALLADA                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        MAIN WINDOW                                  │    │
│  │                    (main_window.py)                                 │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ • Window Management                                                 │    │
│  │ • Tab Navigation                                                    │    │
│  │ • Menu System                                                       │    │
│  │ • Status Bar                                                        │    │
│  │ • Event Handling                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        TAB MODULES                                  │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │                                                                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  │   DATA TAB  │  │  CORE TAB   │  │ RESULTS TAB │  │ADVANCED TAB │ │
│  │  │             │  │             │  │             │  │             │ │
│  │  │ • File Load │  │ • Config    │  │ • Ranking   │  │ • DarwinEX  │ │
│  │  │ • Validation│  │ • Analysis  │  │ • Filtering │  │ • AXI Select│ │
│  │  │ • Preview   │  │ • Progress  │  │ • Charts    │  │ • Advisor   │ │
│  │  │ • Export    │  │ • Results   │  │ • Export    │  │ • Portfolio │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
│  │                                                                     │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  │ ADVISOR TAB │  │ EXPORT TAB  │  │  HELP TAB   │  │  LOGS TAB   │ │
│  │  │             │  │             │  │             │  │             │ │
│  │  │ • Chat      │  │ • Reports   │  │ • Guide     │  │ • System    │ │
│  │  │ • Analysis  │  │ • Formats   │  │ • FAQ       │  │ • Performance│ │
│  │  │ • Recommend │  │ • Settings  │  │ • Contact   │  │ • Errors    │ │
│  │  │ • Portfolio │  │ • Schedule  │  │ • Support   │  │ • Monitoring│ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      SHARED COMPONENTS                              │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ • Progress Bars                                                    │    │
│  │ • Data Tables                                                      │    │
│  │ • Charts & Graphs                                                  │    │
│  │ • Form Controls                                                    │    │
│  │ • Dialogs & Modals                                                 │    │
│  │ • Tooltips & Help                                                  │    │
│  │ • Error Handling                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Diagrama de Comunicación Asíncrona

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMUNICACIÓN ASÍNCRONA                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   GUI       │◄──▶│   Worker    │◄──▶│   Core      │◄──▶│   Data      │ │
│  │   Thread    │    │   Thread    │    │   Engine    │    │   Manager   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                   │                   │                   │      │
│         ▼                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ • User      │    │ • Progress  │    │ • QVA       │    │ • File I/O  │ │
│  │   Input     │    │   Updates   │    │   Analysis  │    │ • Validation│ │
│  │ • UI        │    │ • Status    │    │ • Factor K  │    │ • Cleaning  │ │
│  │   Updates   │    │   Messages  │    │ • Regime    │    │ • Mapping   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Advanced  │◄──▶│   ML        │◄──▶│   Database  │◄──▶│   File      │ │
│  │   Modules   │    │   Models    │    │   Layer     │    │   System    │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                   │                   │                   │      │
│         ▼                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ • DarwinEX  │    │ • Model     │    │ • SQLite    │    │ • CSV       │ │
│  │ • AXI Select│    │   Training  │    │ • PostgreSQL│    │ • SQX       │ │
│  │ • Advisor   │    │ • Prediction│    │ • Caching   │    │ • JSON      │ │
│  │ • Portfolio │    │ • Validation│    │ • Logging   │    │ • Config    │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Diagrama de Estados de la Aplicación

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ESTADOS DE LA APLICACIÓN                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   INITIAL   │───▶│   LOADING   │───▶│   READY     │───▶│   ANALYZING │ │
│  │   STATE     │    │   DATA      │    │   FOR        │    │   DATA      │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         ▲                   │                   │                   │      │
│         │                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   ERROR     │◄───│   VALIDATE  │    │   CONFIGURE │    │   PROCESSING│ │
│  │   STATE     │    │   DATA      │    │   ANALYSIS  │    │   RESULTS   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                   │                   │                   │      │
│         ▼                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ • Show      │    │ • Progress  │    │ • Enable    │    │ • Progress  │ │
│  │   Error     │    │   Bar       │    │   Tabs      │    │   Bar       │ │
│  │ • Retry     │    │ • Status    │    │ • Load      │    │ • Status    │ │
│  │ • Log       │    │   Message   │    │   Config    │    │   Updates   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   RESULTS   │◄───│   EXPORTING │◄───│   ADVANCED  │◄───│   COMPLETE  │ │
│  │   READY     │    │   REPORTS   │    │   ANALYSIS  │    │   ANALYSIS  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                   │                   │                   │      │
│         ▼                   ▼                   ▼                   ▼      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ • Show      │    │ • Progress  │    │ • Progress  │    │ • Enable    │ │
│  │   Results   │    │   Bar       │    │   Bar       │    │   Export    │ │
│  │ • Enable    │    │ • Status    │    │ • Status    │    │   Tabs      │ │
│  │   Filtering │    │   Message   │    │   Message   │    │   Results   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Diagrama de Configuración y Persistencia

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONFIGURACIÓN Y PERSISTENCIA                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        CONFIG FILES                                │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ config/                                                             │    │
│  │ ├── app_config.json                                                │    │
│  │ │   ├── gui_settings                                               │    │
│  │ │   ├── analysis_params                                            │    │
│  │ │   ├── export_settings                                            │    │
│  │ │   └── logging_config                                             │    │
│  │ │                                                                   │    │
│  │ ├── user_preferences.json                                          │    │
│  │ │   ├── window_size                                                │    │
│  │ │   ├── theme_preferences                                          │    │
│  │ │   ├── default_paths                                              │    │
│  │ │   └── recent_files                                               │    │
│  │ │                                                                   │    │
│  │ └── analysis_templates.json                                        │    │
│  │     ├── conservative_profile                                       │    │
│  │     ├── aggressive_profile                                         │    │
│  │     └── balanced_profile                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        DATABASE SCHEMA                              │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ strategies                                                          │    │
│  │ ├── id (PRIMARY KEY)                                               │    │
│  │ ├── name (TEXT)                                                    │    │
│  │ ├── file_path (TEXT)                                               │    │
│  │ ├── factor_k (REAL)                                                │    │
│  │ ├── category (TEXT)                                                │    │
│  │ ├── cagr (REAL)                                                    │    │
│  │ ├── sharpe (REAL)                                                  │    │
│  │ ├── max_dd (REAL)                                                  │    │
│  │ ├── trades (INTEGER)                                               │    │
│  │ └── created_at (TIMESTAMP)                                         │    │
│  │                                                                     │    │
│  │ analysis_results                                                    │    │
│  │ ├── id (PRIMARY KEY)                                               │    │
│  │ ├── strategy_id (FOREIGN KEY)                                      │    │
│  │ ├── qva_score (REAL)                                               │    │
│  │ ├── regime_score (REAL)                                            │    │
│  │ ├── risk_score (REAL)                                              │    │
│  │ ├── darwinex_score (REAL)                                          │    │
│  │ ├── axi_score (REAL)                                               │    │
│  │ └── analysis_date (TIMESTAMP)                                      │    │
│  │                                                                     │    │
│  │ portfolios                                                          │    │
│  │ ├── id (PRIMARY KEY)                                               │    │
│  │ ├── name (TEXT)                                                    │    │
│  │ ├── description (TEXT)                                             │    │
│  │ ├── strategies (JSON)                                              │    │
│  │ ├── weights (JSON)                                                 │    │
│  │ ├── metrics (JSON)                                                 │    │
│  │ └── created_at (TIMESTAMP)                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Diagrama de Temas y Estilos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TEMAS Y ESTILOS - ESTRUCTURA                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        THEME MANAGER                               │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ themes/                                                            │    │
│  │ ├── light_theme.json                                              │    │
│  │ │   ├── primary_color: "#2563eb"                                  │    │
│  │ │   ├── secondary_color: "#64748b"                                │    │
│  │ │   ├── success_color: "#059669"                                  │    │
│  │ │   ├── warning_color: "#d97706"                                  │    │
│  │ │   ├── error_color: "#dc2626"                                    │    │
│  │ │   ├── background_color: "#f8fafc"                               │    │
│  │ │   ├── text_color: "#1e293b"                                     │    │
│  │ │   └── border_color: "#e2e8f0"                                   │    │
│  │ │                                                                   │    │
│  │ ├── dark_theme.json                                                │    │
│  │ │   ├── primary_color: "#3b82f6"                                  │    │
│  │ │   ├── secondary_color: "#94a3b8"                                │    │
│  │ │   ├── success_color: "#10b981"                                  │    │
│  │ │   ├── warning_color: "#f59e0b"                                  │    │
│  │ │   ├── error_color: "#ef4444"                                    │    │
│  │ │   ├── background_color: "#0f172a"                               │    │
│  │ │   ├── text_color: "#f1f5f9"                                     │    │
│  │ │   └── border_color: "#334155"                                   │    │
│  │ │                                                                   │    │
│  │ └── custom_theme.json                                              │    │
│  │     ├── user_defined_colors                                        │    │
│  │     ├── custom_fonts                                               │    │
│  │     └── special_effects                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        STYLE COMPONENTS                             │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ components/                                                        │    │
│  │ ├── buttons.py                                                     │    │
│  │ │   ├── PrimaryButton                                             │    │
│  │ │   ├── SecondaryButton                                           │    │
│  │ │   ├── SuccessButton                                             │    │
│  │ │   ├── WarningButton                                             │    │
│  │ │   └── ErrorButton                                               │    │
│  │ │                                                                   │    │
│  │ ├── inputs.py                                                      │    │
│  │ │   ├── TextInput                                                 │    │
│  │ │   ├── NumberInput                                               │    │
│  │ │   ├── FileInput                                                 │    │
│  │ │   ├── DropdownInput                                             │    │
│  │ │   └── SliderInput                                               │    │
│  │ │                                                                   │    │
│  │ ├── tables.py                                                      │    │
│  │ │   ├── DataTable                                                 │    │
│  │ │   ├── ResultsTable                                              │    │
│  │ │   ├── PortfolioTable                                            │    │
│  │ │   └── LogsTable                                                 │    │
│  │ │                                                                   │    │
│  │ └── charts.py                                                      │    │
│  │     ├── FactorKChart                                              │    │
│  │     ├── PerformanceChart                                           │    │
│  │     ├── RiskChart                                                 │    │
│  │     └── PortfolioChart                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Diagrama de Métricas y KPIs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MÉTRICAS Y KPIS - MONITOREO                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        PERFORMANCE METRICS                          │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ • Application Startup Time: < 3 seconds                            │    │
│  │ • Data Loading Time: < 5 seconds                                   │    │
│  │ • Analysis Execution Time: < 30 seconds                            │    │
│  │ • UI Response Time: < 100ms                                         │    │
│  │ • Memory Usage: < 500MB                                             │    │
│  │ • CPU Usage: < 20% average                                          │    │
│  │ • Disk I/O: < 10MB/s                                                │    │
│  │ • Network Usage: < 1MB/s                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        QUALITY METRICS                              │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ • Code Coverage: > 90%                                              │    │
│  │ • Test Pass Rate: > 95%                                             │    │
│  │ • Error Rate: < 1%                                                  │    │
│  │ • User Satisfaction: > 4.5/5                                        │    │
│  │ • Feature Completeness: > 95%                                       │    │
│  │ • Documentation Coverage: > 90%                                      │    │
│  │ • Accessibility Score: > 95%                                         │    │
│  │ • Internationalization: > 80%                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        BUSINESS METRICS                             │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ • Strategies Analyzed: 1,250+                                       │    │
│  │ • Analysis Accuracy: > 95%                                          │    │
│  │ • Portfolio Optimization: > 90%                                      │    │
│  │ • Report Generation: 100% success                                    │    │
│  │ • Export Formats: 4 (Excel, HTML, PDF, SQX)                        │    │
│  │ • Advanced Modules: 3 (DarwinEX, AXI, Advisor)                     │    │
│  │ • User Sessions: > 100/day                                          │    │
│  │ • System Uptime: > 99.9%                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Especificaciones Técnicas de Implementación

### Patrones de Diseño Utilizados
- **MVC (Model-View-Controller)**: Separación clara de responsabilidades
- **Observer**: Actualización automática de vistas
- **Factory**: Creación de componentes dinámicos
- **Strategy**: Diferentes algoritmos de análisis
- **Command**: Operaciones deshacer/rehacer
- **Singleton**: Configuración global
- **Repository**: Acceso a datos centralizado

### Tecnologías y Librerías
- **GUI Framework**: Tkinter (Python 3.11+)
- **Charts**: Matplotlib, Plotly
- **Data Processing**: Pandas, NumPy
- **Database**: SQLite (local), PostgreSQL (production)
- **ML/AI**: Scikit-learn, TensorFlow (opcional)
- **Testing**: Pytest, pytest-qt
- **Documentation**: Sphinx, MkDocs

### Arquitectura de Archivos
```
src/gui/
├── main_window.py          # Ventana principal
├── modules/
│   ├── __init__.py
│   ├── data_tab.py        # Tab de datos
│   ├── core_tab.py        # Tab de análisis core
│   ├── results_tab.py     # Tab de resultados
│   ├── advanced_tab.py    # Tab de módulos avanzados
│   ├── advisor_tab.py     # Tab del asesor
│   ├── export_tab.py      # Tab de exportación
│   ├── help_tab.py        # Tab de ayuda
│   └── logs_tab.py        # Tab de logs
├── components/
│   ├── __init__.py
│   ├── charts.py          # Componentes de gráficos
│   ├── tables.py          # Componentes de tablas
│   ├── forms.py           # Componentes de formularios
│   ├── dialogs.py         # Diálogos modales
│   └── widgets.py         # Widgets personalizados
├── utils/
│   ├── __init__.py
│   ├── async_worker.py    # Trabajo asíncrono
│   ├── theme_manager.py   # Gestión de temas
│   ├── validation.py      # Validación de datos
│   └── file_utils.py      # Utilidades de archivos
└── config/
    ├── __init__.py
    ├── gui_config.py      # Configuración GUI
    ├── themes.py          # Definición de temas
    └── constants.py       # Constantes
```

### Flujo de Datos Asíncrono
1. **User Input** → GUI Thread
2. **Validation** → Worker Thread
3. **Data Processing** → Core Engine
4. **Analysis** → Advanced Modules
5. **Results** → GUI Thread (via callback)
6. **Export** → Worker Thread

### Manejo de Errores
- **Try-Catch** en cada operación crítica
- **Logging** detallado de errores
- **User-friendly** mensajes de error
- **Recovery** automático cuando sea posible
- **Fallback** a configuraciones por defecto

### Optimización de Rendimiento
- **Lazy Loading** de componentes pesados
- **Caching** de resultados de análisis
- **Background Processing** para operaciones largas
- **Memory Management** con garbage collection
- **Database Indexing** para consultas rápidas

---

## 📋 Checklist de Implementación

### Fase 1: Estructura Base
- [ ] Crear estructura de directorios
- [ ] Implementar MainWindow base
- [ ] Configurar sistema de tabs
- [ ] Implementar navegación
- [ ] Configurar tema básico

### Fase 2: Módulos Core
- [ ] Implementar DataTab
- [ ] Implementar CoreTab
- [ ] Implementar ResultsTab
- [ ] Integrar con DataManager
- [ ] Integrar con ConfigManager

### Fase 3: Módulos Avanzados
- [ ] Implementar AdvancedTab
- [ ] Implementar AdvisorTab
- [ ] Implementar ExportTab
- [ ] Integrar módulos avanzados
- [ ] Implementar portfolio builder

### Fase 4: Componentes y Utilidades
- [ ] Implementar componentes reutilizables
- [ ] Implementar sistema de temas
- [ ] Implementar trabajo asíncrono
- [ ] Implementar validación robusta
- [ ] Implementar logging completo

### Fase 5: Testing y Optimización
- [ ] Implementar tests unitarios
- [ ] Implementar tests de integración
- [ ] Optimizar rendimiento
- [ ] Documentar código
- [ ] Preparar para deployment

---

*Este diagrama técnico define la arquitectura completa de la GUI modular, asegurando escalabilidad, mantenibilidad y una experiencia de usuario profesional.* 