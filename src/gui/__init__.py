"""
GUI Package - Interfaz Gráfica Modularizada

Este paquete contiene todos los módulos de la interfaz gráfica
del sistema de análisis cuantitativo, organizados de forma modular.
"""

# Importar módulos principales
from .main_window import MainWindow, create_main_window
from .utils import (
    TkinterLogHandler,
    GUIAnalysisError,
    validate_input,
    log_execution_time,
    QVA_COL_MAP,
    DEFAULT_CONFIG,
    CATEGORY_COLORS,
    WIDGET_STYLES,
    create_styled_button,
    create_styled_label,
    create_styled_entry,
    show_info_message,
    show_error_message,
    show_warning_message,
    ask_yes_no_question,
    select_file,
    select_directory,
    save_file,
    validate_dataframe,
    load_data_with_datamanager,
    format_number,
    format_percentage,
    create_progress_bar,
    update_progress_bar,
    create_treeview,
    populate_treeview,
    create_scrolled_frame,
    setup_logging_to_widget,
    clear_log_widget,
    export_results_to_excel,
    export_results_to_csv,
    create_tooltip,
    create_help_button,
    create_status_bar,
    update_status,
    create_menu_bar,
    center_window,
    create_loading_dialog,
    close_loading_dialog,
    create_error_dialog,
    create_confirm_dialog,
    create_info_dialog,
    create_wizard_navigation,
    create_filter_panel,
    create_results_table,
    create_chart_frame,
    create_summary_panel,
    update_summary_panel,
    create_export_panel,
    create_help_panel,
    create_about_dialog,
    setup_widget_styles
)

# Importar módulos de pasos
from .steps import (
    Step1LoadFrame,
    create_step1_load_frame,
    Step2ConfigureFrame,
    create_step2_configure_frame
)

# Importar módulos de asesor (placeholders)
# from .advisor import (
#     AdvisorMainTab,
#     AsesorCientificoTab,
#     AsesorEmpiricoTab,
#     AsesorConsejosTab,
#     AsesorResumenTab
# )

__all__ = [
    # Módulos principales
    'MainWindow',
    'create_main_window',
    
    # Utilidades
    'TkinterLogHandler',
    'GUIAnalysisError',
    'validate_input',
    'log_execution_time',
    'QVA_COL_MAP',
    'DEFAULT_CONFIG',
    'CATEGORY_COLORS',
    'WIDGET_STYLES',
    'create_styled_button',
    'create_styled_label',
    'create_styled_entry',
    'show_info_message',
    'show_error_message',
    'show_warning_message',
    'ask_yes_no_question',
    'select_file',
    'select_directory',
    'save_file',
    'validate_dataframe',
    'load_data_with_datamanager',
    'format_number',
    'format_percentage',
    'create_progress_bar',
    'update_progress_bar',
    'create_treeview',
    'populate_treeview',
    'create_scrolled_frame',
    'setup_logging_to_widget',
    'clear_log_widget',
    'export_results_to_excel',
    'export_results_to_csv',
    'create_tooltip',
    'create_help_button',
    'create_status_bar',
    'update_status',
    'create_menu_bar',
    'center_window',
    'create_loading_dialog',
    'close_loading_dialog',
    'create_error_dialog',
    'create_confirm_dialog',
    'create_info_dialog',
    'create_wizard_navigation',
    'create_filter_panel',
    'create_results_table',
    'create_chart_frame',
    'create_summary_panel',
    'update_summary_panel',
    'create_export_panel',
    'create_help_panel',
    'create_about_dialog',
    'setup_widget_styles',
    
    # Módulos de pasos
    'Step1LoadFrame',
    'create_step1_load_frame',
    'Step2ConfigureFrame',
    'create_step2_configure_frame'
    
    # Módulos de asesor (futuros)
    # 'AdvisorMainTab',
    # 'AsesorCientificoTab',
    # 'AsesorEmpiricoTab',
    # 'AsesorConsejosTab',
    # 'AsesorResumenTab'
] 
