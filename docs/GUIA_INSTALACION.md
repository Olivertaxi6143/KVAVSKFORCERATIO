# 🚀 GUÍA DE INSTALACIÓN - KFORCEVSQVARATIOS v2.0

## 📋 Requisitos del Sistema

### Requisitos Mínimos
- **Sistema Operativo**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 o superior
- **RAM**: 4GB mínimo, 8GB recomendado
- **Espacio en Disco**: 2GB para instalación, 5GB para datos
- **Procesador**: Intel i5 o AMD equivalente

### Requisitos Recomendados
- **RAM**: 16GB o superior
- **Espacio en Disco**: 10GB para datos y cache
- **Procesador**: Intel i7 o AMD Ryzen 7
- **GPU**: No requerida (procesamiento CPU)

---

## 🔧 Instalación Paso a Paso

### Paso 1: Preparación del Entorno

#### 1.1 Verificar Python
```bash
# Verificar versión de Python
python --version
# Debe mostrar Python 3.8 o superior
```

#### 1.2 Crear Entorno Virtual (Recomendado)
```bash
# Crear entorno virtual
python -m venv kforce_env

# Activar entorno virtual
# Windows:
kforce_env\Scripts\activate
# macOS/Linux:
source kforce_env/bin/activate
```

### Paso 2: Instalación de Dependencias

#### 2.1 Instalar Dependencias Principales
```bash
# Instalar dependencias base
pip install pandas numpy scipy scikit-learn matplotlib seaborn

# Instalar dependencias de GUI
pip install tkinter pillow

# Instalar dependencias de logging
pip install logging

# Instalar dependencias adicionales
pip install pathlib psutil
```

#### 2.2 Verificar Instalación
```bash
# Verificar que todas las dependencias están instaladas
python -c "import pandas, numpy, scipy, sklearn, matplotlib, seaborn; print('✅ Todas las dependencias instaladas correctamente')"
```

### Paso 3: Descarga e Instalación del Sistema

#### 3.1 Descargar KFORCEVSQVARATIOS v2.0
```bash
# Clonar repositorio (si está en Git)
git clone https://github.com/usuario/kforcevsqvaratios.git
cd kforcevsqvaratios

# O descargar archivo ZIP y extraer
# Descargar desde: [URL_DEL_REPOSITORIO]
```

#### 3.2 Instalar el Sistema
```bash
# Navegar al directorio del proyecto
cd KVAVSKFORCERATIO

# Instalar en modo desarrollo
pip install -e .

# O instalar directamente
python setup.py install
```

### Paso 4: Configuración Inicial

#### 4.1 Crear Directorios de Datos
```bash
# Crear directorio de datos
mkdir ~/KFORCE_DATA
mkdir ~/KFORCE_OUTPUT
mkdir ~/KFORCE_CACHE
```

#### 4.2 Configurar Variables de Entorno
```bash
# Windows (PowerShell):
$env:KFORCE_DEV_MODE = "false"
$env:KFORCE_LOG_LEVEL = "INFO"

# macOS/Linux:
export KFORCE_DEV_MODE=false
export KFORCE_LOG_LEVEL=INFO
```

### Paso 5: Verificación de Instalación

#### 5.1 Ejecutar Test de Instalación
```bash
# Ejecutar test de instalación
python -m pytest test_cli_flujo_completo_exhaustivo.py::test_1_inicializacion_componentes -v
```

#### 5.2 Verificar Componentes
```bash
# Verificar que todos los componentes están disponibles
python -c "
from src.gui_enhanced_rank import EnhancedRankGUI
from src.data_manager import DataManager
from src.core_engine_enhanced import FactorKElite96Enhanced
from src.asesor_financiero_inteligente import AsesorFinancieroInteligente
print('✅ Todos los componentes importados correctamente')
"
```

---

## 📁 Estructura de Directorios

```
KVAVSKFORCERATIO/
├── src/                          # Código fuente
│   ├── gui_enhanced_rank.py     # GUI principal
│   ├── data_manager.py          # Gestor de datos
│   ├── core_engine_enhanced.py  # Motor de análisis
│   ├── asesor_financiero_inteligente.py # Asesor
│   └── config_manager_enhanced.py # Configuración
├── tests/                       # Tests del sistema
├── docs/                        # Documentación
├── INPUTTEST/                   # Datos de prueba
├── config_produccion.py         # Configuración producción
└── requirements.txt             # Dependencias
```

---

## 🎯 Configuración para Producción

### Configuración Automática
```python
# Importar configuración de producción
from config_produccion import setup_produccion

# Configurar para producción
config = setup_produccion()
```

### Configuración Manual
```python
# Configurar logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kforce_produccion.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🚀 Ejecución del Sistema

### Ejecución Básica
```bash
# Ejecutar GUI principal
python src/gui_enhanced_rank.py
```

### Ejecución con Configuración Específica
```bash
# Ejecutar con configuración de producción
python -c "
from config_produccion import setup_produccion
from src.gui_enhanced_rank import EnhancedRankGUI
import tkinter as tk

# Configurar producción
config = setup_produccion()

# Ejecutar GUI
root = tk.Tk()
app = EnhancedRankGUI()
root.mainloop()
"
```

### Ejecución en Modo Desarrollo
```bash
# Ejecutar en modo desarrollo
export KFORCE_DEV_MODE=true
python src/gui_enhanced_rank.py
```

---

## 🔍 Solución de Problemas

### Problema: "ModuleNotFoundError"
```bash
# Solución: Instalar dependencias faltantes
pip install -r requirements.txt
```

### Problema: "PermissionError"
```bash
# Solución: Verificar permisos de directorios
chmod 755 ~/KFORCE_DATA
chmod 755 ~/KFORCE_OUTPUT
chmod 755 ~/KFORCE_CACHE
```

### Problema: "MemoryError"
```bash
# Solución: Reducir batch_size en configuración
# Editar config_produccion.py
BATCH_SIZE = 50  # Reducir de 100 a 50
```

### Problema: "TimeoutError"
```bash
# Solución: Aumentar timeout en configuración
# Editar config_produccion.py
TIMEOUT_ANALYSIS = 600  # Aumentar de 300 a 600 segundos
```

---

## 📊 Verificación de Rendimiento

### Test de Rendimiento Básico
```bash
# Ejecutar test de rendimiento
python -m pytest test_cli_flujo_completo_exhaustivo.py::test_10_rendimiento_y_estabilidad -v
```

### Verificación de Memoria
```python
import psutil
import os

# Verificar uso de memoria
process = psutil.Process(os.getpid())
memory_usage = process.memory_info().rss / 1024 / 1024  # MB
print(f"Uso de memoria: {memory_usage:.2f} MB")
```

---

## 📝 Configuración Avanzada

### Configuración de Logging
```python
# Configurar logging detallado
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kforce_detailed.log'),
        logging.StreamHandler()
    ]
)
```

### Configuración de Cache
```python
# Habilitar cache para mejor rendimiento
import os
os.environ['KFORCE_CACHE_ENABLED'] = 'true'
```

### Configuración de Monitoreo
```python
# Habilitar monitoreo de rendimiento
import os
os.environ['KFORCE_MONITORING_ENABLED'] = 'true'
```

---

## ✅ Checklist de Instalación

- [ ] Python 3.8+ instalado y verificado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas correctamente
- [ ] Sistema descargado e instalado
- [ ] Directorios de datos creados
- [ ] Variables de entorno configuradas
- [ ] Test de instalación ejecutado exitosamente
- [ ] Componentes verificados
- [ ] Configuración de producción aplicada
- [ ] Sistema ejecutado correctamente

---

## 📞 Soporte Técnico

### Información de Contacto
- **Email**: soporte@kforcevsqvaratios.com
- **Documentación**: [URL_DOCUMENTACION]
- **Issues**: [URL_GITHUB_ISSUES]

### Logs de Diagnóstico
```bash
# Generar logs de diagnóstico
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from src.gui_enhanced_rank import EnhancedRankGUI
print('Logs de diagnóstico generados')
"
```

---

*Guía de instalación v2.0 - KFORCEVSQVARATIOS*
*Fecha: 2025-07-11* 