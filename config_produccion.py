# ⚙️ CONFIGURACIÓN DE PRODUCCIÓN - KFORCEVSQVARATIOS v2.0
# Archivo de configuración optimizado para entorno de producción

import os
import logging
from pathlib import Path

class ConfiguracionProduccion:
    """
    Configuración optimizada para entorno de producción
    """
    
    def __init__(self):
        # Configuración de logging para producción
        self.LOG_LEVEL = logging.INFO
        self.LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.LOG_FILE = 'kforce_produccion.log'
        
        # Configuración de rendimiento
        self.MAX_MEMORY_USAGE = 1024  # MB
        self.TIMEOUT_ANALYSIS = 300   # segundos
        self.BATCH_SIZE = 100         # estrategias por lote
        
        # Configuración de análisis
        self.SCIENTIFIC_IMPROVEMENTS_ENABLED = True
        self.DEFAULT_STYLE = "CONSERVADOR"
        self.DEFAULT_PERCENTIL = 20
        self.DEFAULT_TOP_N = 10
        self.DEFAULT_SELECTED_KPIS = 5
        
        # Configuración de validación
        self.STRICT_VALIDATION = True
        self.ALLOW_MISSING_VALUES = False
        self.MAX_DRAWDOWN_THRESHOLD = 0.15
        self.MIN_SHARPE_RATIO = 0.5
        
        # Configuración de rutas
        self.DATA_DIRECTORY = Path.home() / "KFORCE_DATA"
        self.OUTPUT_DIRECTORY = Path.home() / "KFORCE_OUTPUT"
        self.CACHE_DIRECTORY = Path.home() / "KFORCE_CACHE"
        
        # Configuración de cache
        self.ENABLE_CACHE = True
        self.CACHE_EXPIRY = 3600  # segundos (1 hora)
        
        # Configuración de seguridad
        self.ENABLE_DATA_ENCRYPTION = False
        self.LOG_SENSITIVE_DATA = False
        
        # Configuración de monitoreo
        self.ENABLE_PERFORMANCE_MONITORING = True
        self.MONITORING_INTERVAL = 60  # segundos
        
    def setup_logging(self):
        """
        Configura logging para producción
        """
        logging.basicConfig(
            level=self.LOG_LEVEL,
            format=self.LOG_FORMAT,
            handlers=[
                logging.FileHandler(self.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        
    def create_directories(self):
        """
        Crea directorios necesarios para producción
        """
        directories = [
            self.DATA_DIRECTORY,
            self.OUTPUT_DIRECTORY,
            self.CACHE_DIRECTORY
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def validate_configuration(self):
        """
        Valida la configuración de producción
        """
        # Verificar directorios
        if not self.DATA_DIRECTORY.exists():
            raise ValueError(f"Directorio de datos no existe: {self.DATA_DIRECTORY}")
            
        # Verificar permisos
        if not os.access(self.DATA_DIRECTORY, os.R_OK):
            raise PermissionError(f"Sin permisos de lectura en: {self.DATA_DIRECTORY}")
            
        # Verificar parámetros
        if self.DEFAULT_TOP_N <= 0:
            raise ValueError("DEFAULT_TOP_N debe ser mayor que 0")
            
        if self.DEFAULT_PERCENTIL < 0 or self.DEFAULT_PERCENTIL > 100:
            raise ValueError("DEFAULT_PERCENTIL debe estar entre 0 y 100")
            
        return True

# Configuración global de producción
PRODUCCION_CONFIG = ConfiguracionProduccion()

def get_produccion_config():
    """
    Retorna la configuración de producción
    """
    return PRODUCCION_CONFIG

def setup_produccion():
    """
    Configura el sistema para producción
    """
    config = get_produccion_config()
    
    # Configurar logging
    config.setup_logging()
    
    # Crear directorios
    config.create_directories()
    
    # Validar configuración
    config.validate_configuration()
    
    logging.info("✅ Configuración de producción inicializada correctamente")
    return config 