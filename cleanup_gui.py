#!/usr/bin/env python3
"""
Script para limpiar el archivo main_window.py eliminando funciones duplicadas
"""

def clean_gui_file():
    input_file = 'src/gui/main_window.py'
    output_file = 'src/gui/main_window_clean.py'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Archivo original tiene {len(lines)} líneas")
    
    # Encontrar donde empiezan las funciones duplicadas
    # Buscar la primera aparición de funciones duplicadas
    duplicate_start = None
    
    for i, line in enumerate(lines):
        if 'def _build_estrategias_asesor_tab(self):' in line and i > 1000:
            duplicate_start = i
            print(f"Funciones duplicadas encontradas a partir de la línea {i+1}")
            break
    
    if duplicate_start:
        # Mantener solo hasta las funciones duplicadas
        clean_lines = lines[:duplicate_start]
        
        # Agregar la función de normalización al final
        clean_lines.append('\n')
        clean_lines.append('def normalizar_columnas_y_kpis(df):\n')
        clean_lines.append('    """\n')
        clean_lines.append('    Normaliza las columnas del dataframe para que coincidan con las esperadas por el análisis.\n')
        clean_lines.append('    """\n')
        clean_lines.append('    import pandas as pd\n')
        clean_lines.append('    \n')
        clean_lines.append('    # Mapeo de nombres de columnas comunes\n')
        clean_lines.append('    column_mapping = {\n')
        clean_lines.append("        'Strategy Name': 'Strategy_Name',\n")
        clean_lines.append("        'Total Trades': 'Total_Trades',\n")
        clean_lines.append("        'Profit Factor': 'Profit_Factor',\n")
        clean_lines.append("        'Max. Drawdown (%)': 'Max_Drawdown_Percent',\n")
        clean_lines.append("        'Sharpe Ratio': 'Sharpe_Ratio',\n")
        clean_lines.append("        'CAGR': 'CAGR'\n")
        clean_lines.append('    }\n')
        clean_lines.append('    \n')
        clean_lines.append('    # Aplicar mapeo de columnas\n')
        clean_lines.append('    df_normalized = df.rename(columns=column_mapping)\n')
        clean_lines.append('    \n')
        clean_lines.append('    return df_normalized\n')
        
        print(f"Archivo limpio tendrá {len(clean_lines)} líneas")
        
        # Escribir archivo limpio
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(clean_lines)
        
        print(f"Archivo limpio guardado como: {output_file}")
        
        # Reemplazar el archivo original
        import shutil
        shutil.move(output_file, input_file)
        print(f"Archivo original reemplazado con la versión limpia")
        
    else:
        print("No se encontraron funciones duplicadas")

if __name__ == "__main__":
    clean_gui_file() 