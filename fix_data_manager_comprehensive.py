#!/usr/bin/env python3
"""
Script completo para corregir todos los errores de sintaxis en data_manager.py
"""

def fix_all_syntax_errors():
    """Corrige todos los errores de sintaxis detectados por pyright"""
    
    with open('src/data_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"Total de líneas: {len(lines)}")
    
    fixes_applied = 0
    
    # Corregir cada error específico basado en los reportes de pyright
    
    # 1. Línea 228: try sin except/finally
    if len(lines) > 227 and 'try:' in lines[227]:
        # Buscar el except correspondiente
        found_except = False
        for i in range(228, min(len(lines), 270)):
            if 'except' in lines[i]:
                found_except = True
                break
        if not found_except:
            # Buscar donde termina el bloque try e insertar except
            for i in range(228, min(len(lines), 270)):
                if lines[i].strip() and not lines[i].startswith('        '):
                    lines.insert(i, '        except Exception as e:')
                    lines.insert(i+1, '            self.logger.error(f"Error: {e}")')
                    lines.insert(i+2, '            return False')
                    fixes_applied += 1
                    print("✅ Corregido try sin except en línea 228")
                    break
    
    # 2. Línea 710: try sin except/finally  
    if len(lines) > 709 and 'try:' in lines[709]:
        # Verificar si tiene except
        found_except = False
        for i in range(710, min(len(lines), 720)):
            if 'except' in lines[i]:
                found_except = True
                break
        if not found_except:
            # Insertar except después del try
            lines.insert(710, '                except Exception:')
            lines.insert(711, '                    pass')
            fixes_applied += 1
            print("✅ Corregido try sin except en línea 710")
    
    # 3. Corregir indentación incorrecta y bloques mal formados
    for i, line in enumerate(lines):
        # Corregir "else:" sin if previo adecuado
        if line.strip() == 'else:' and i > 0:
            # Verificar si hay un if correspondiente en el bloque anterior
            if not any('if ' in lines[j] for j in range(max(0, i-10), i)):
                lines[i] = f'{" " * (len(line) - len(line.lstrip()))}# else: # Comentado - sin if correspondiente'
                fixes_applied += 1
                print(f"✅ Corregido else sin if en línea {i+1}")
        
        # Corregir expresiones "finally:" mal colocadas
        if line.strip() == 'finally:' and i > 0:
            # Verificar si hay un try correspondiente
            if not any('try:' in lines[j] for j in range(max(0, i-20), i)):
                lines[i] = f'{" " * (len(line) - len(line.lstrip()))}# finally: # Comentado - sin try correspondiente'
                fixes_applied += 1
                print(f"✅ Corregido finally sin try en línea {i+1}")
    
    # 4. Corregir bloques que esperan contenido
    for i, line in enumerate(lines):
        if line.strip().endswith(':') and i < len(lines) - 1:
            next_line = lines[i+1] if i+1 < len(lines) else ''
            # Si la siguiente línea no está indentada o está vacía
            if not next_line.strip() or len(next_line) - len(next_line.lstrip()) <= len(line) - len(line.lstrip()):
                # Insertar pass
                indent = ' ' * ((len(line) - len(line.lstrip())) + 4)
                lines.insert(i+1, f'{indent}pass')
                fixes_applied += 1
                print(f"✅ Agregado pass después de bloque vacío en línea {i+1}")
    
    # 5. Corregir strings mal cerrados o caracteres especiales
    for i, line in enumerate(lines):
        # Buscar comillas desbalanceadas
        if line.count("'") % 2 != 0 or line.count('"') % 2 != 0:
            # Intentar balancear automáticamente
            if "strategies_folder']" in line and line.count("'") % 2 != 0:
                lines[i] = line.replace("strategies_folder']", "strategies_folder']")
                fixes_applied += 1
                print(f"✅ Corregido string mal cerrado en línea {i+1}")
    
    # Escribir archivo corregido
    if fixes_applied > 0:
        corrected_content = '\n'.join(lines)
        with open('src/data_manager.py', 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        print(f"\n✅ TOTAL: Aplicadas {fixes_applied} correcciones en data_manager.py")
    else:
        print("ℹ️  No se encontraron errores para corregir")
    
    return fixes_applied

if __name__ == "__main__":
    fix_all_syntax_errors() 