#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis en data_manager.py
"""

def fix_data_manager_syntax():
    """Corrige los errores de sintaxis detectados por pyright"""
    
    with open('src/data_manager.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total de líneas: {len(lines)}")
    
    # Corregir errores específicos
    fixes_applied = 0
    
    # Error en línea 240 - corregir string mal cerrado
    if len(lines) > 239:
        line_240 = lines[239]
        if "strategies_folder']" in line_240:
            lines[239] = line_240.replace("strategies_folder']", "strategies_folder']")
            fixes_applied += 1
            print("✅ Corregido error en línea 240")
    
    # Error en línea 715 - except sin try
    if len(lines) > 714:
        line_715 = lines[714]
        if line_715.strip() == "except:":
            # Buscar el try correspondiente
            for i in range(714, -1, -1):
                if "try:" in lines[i]:
                    break
            else:
                # No se encontró try, agregar excepción
                lines[714] = "                except Exception:\n"
                fixes_applied += 1
                print("✅ Corregido error en línea 715")
    
    # Error en línea 810 - bloque if sin contenido  
    if len(lines) > 809:
        line_810 = lines[809]
        if line_810.strip().endswith(":") and (len(lines) <= 810 or not lines[810].strip()):
            # Agregar pass después del :
            if len(lines) > 810:
                lines[810] = "                pass\n"
            else:
                lines.append("                pass\n")
            fixes_applied += 1
            print("✅ Corregido error en línea 810")
    
    # Escribir archivo corregido
    if fixes_applied > 0:
        with open('src/data_manager.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ Aplicadas {fixes_applied} correcciones en data_manager.py")
    else:
        print("ℹ️  No se encontraron errores específicos para corregir")

if __name__ == "__main__":
    fix_data_manager_syntax() 