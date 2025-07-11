#!/usr/bin/env python3
"""
Script CLI para ejecutar el flujo completo del Asesor Financiero Inteligente.

Flujo:
1. Cargar datos con DataManager
2. Ejecutar análisis principal del core engine
3. Filtrar estrategias por percentil
4. Pasar estrategias filtradas al Asesor Financiero
5. Mostrar y guardar resultados

Uso:
    python cli_asesor_financiero.py [--percentil 90] [--output reporte.txt] [--config config.json]
"""

import argparse
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from data_manager import DataManager
    from core_engine_enhanced import FactorKElite96Enhanced
    from asesor_financiero_inteligente import ejecutar_analisis_completo
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de estar en el directorio raíz del proyecto")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cli_asesor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def cargar_configuracion(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Carga la configuración desde archivo o usa valores por defecto.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Diccionario con configuración
    """
    config_default = {
        "kpi_file": "DatabankExport_M1.csv",
        "market_file": "DATOSMQL5.csv",
        "strategies_folder": "INPUTTEST/M1_NDX_UP_MQL4_136_STOP",
        "output_folder": "INPUTTEST/TOP",
        "percentil": 90,
        "kpis_seleccionados": [
            "CAGR (IS)", "CAGR (OOS)", "Sharpe_Ratio (IS)", "Sharpe_Ratio (OOS)",
            "Sortino_Ratio", "SQN (IS)", "SQN (OOS)", "Drawdown (IS)", "Drawdown (OOS)",
            "Profit_Factor (IS)", "Profit_Factor (OOS)", "Recovery_Factor (IS)",
            "Recovery_Factor (OOS)", "Avg. Bars in Trade", "Total Trades (IS)",
            "Total Trades (OOS)", "Win Rate (IS)", "Win Rate (OOS)",
            "Avg. Trade (IS)", "Avg. Trade (OOS)", "Max. Consecutive Losses (IS)",
            "Max. Consecutive Losses (OOS)"
        ]
    }
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_user = json.load(f)
                config_default.update(config_user)
                logger.info(f"✅ Configuración cargada desde {config_path}")
        except Exception as e:
            logger.warning(f"⚠️ Error cargando configuración: {e}. Usando valores por defecto.")
    
    return config_default

def ejecutar_flujo_completo(config: Dict[str, Any], output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Ejecuta el flujo completo del análisis.
    
    Args:
        config: Configuración del análisis
        output_file: Archivo de salida opcional
        
    Returns:
        Diccionario con todos los resultados
    """
    try:
        logger.info("🚀 INICIANDO FLUJO COMPLETO DEL ASESOR FINANCIERO")
        logger.info("=" * 60)
        
        # Paso 1: Cargar datos con DataManager
        logger.info("📊 Paso 1: Cargando datos con DataManager...")
        dm = DataManager()
        
        # Cargar archivos de datos
        kpi_file = config["kpi_file"]
        market_file = config["market_file"]
        
        if not os.path.exists(kpi_file):
            logger.error(f"❌ Archivo de KPIs no encontrado: {kpi_file}")
            return {"error": f"Archivo de KPIs no encontrado: {kpi_file}"}
        
        if not os.path.exists(market_file):
            logger.error(f"❌ Archivo de mercado no encontrado: {market_file}")
            return {"error": f"Archivo de mercado no encontrado: {market_file}"}
        
        # Cargar datos usando los métodos correctos
        try:
            dm.load_kpis_data(kpi_file)
            dm.load_market_data(market_file)
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
            return {"error": f"Error cargando datos: {e}"}
        
        if dm.kpis_data is None:
            logger.error("❌ No se pudieron cargar los datos de KPIs")
            return {"error": "No se pudieron cargar los datos de KPIs"}
        
        logger.info(f"✅ Datos cargados: {len(dm.kpis_data)} estrategias")
        
        # Paso 2: Ejecutar análisis principal del core engine
        logger.info("🔧 Paso 2: Ejecutando análisis principal del core engine...")
        core_engine = FactorKElite96Enhanced()
        
        # Configurar parámetros del análisis
        percentil = config["percentil"]
        kpis_seleccionados = config["kpis_seleccionados"]
        
        # Ejecutar análisis principal
        resultados_analizados = core_engine.evaluate_strategies(dm.kpis_data)
        
        # Filtrar por percentil
        if 'Unified_Score' in resultados_analizados.columns:
            threshold = resultados_analizados['Unified_Score'].quantile(percentil / 100)
            estrategias_filtradas = resultados_analizados[resultados_analizados['Unified_Score'] >= threshold]
        else:
            # Si no hay Unified_Score, usar el primer score disponible
            score_columns = [col for col in resultados_analizados.columns if 'Score' in col or 'score' in col]
            if score_columns:
                score_col = score_columns[0]
                threshold = resultados_analizados[score_col].quantile(percentil / 100)
                estrategias_filtradas = resultados_analizados[resultados_analizados[score_col] >= threshold]
            else:
                # Si no hay scores, usar todas las estrategias
                estrategias_filtradas = resultados_analizados
        
        resultados_core = {
            'estrategias_filtradas': estrategias_filtradas,
            'total_estrategias': len(dm.kpis_data),
            'estrategias_filtradas_count': len(estrategias_filtradas),
            'percentil': percentil,
            'kpis_seleccionados': kpis_seleccionados
        }
        
        if len(estrategias_filtradas) == 0:
            logger.warning("⚠️ No hay estrategias que pasen el filtro de percentil")
            return {"error": "No hay estrategias que pasen el filtro de percentil"}
        
        logger.info(f"✅ Análisis principal completado: {len(estrategias_filtradas)} estrategias filtradas")
        
        # Paso 3: Ejecutar Asesor Financiero Inteligente
        logger.info("🤖 Paso 4: Ejecutando Asesor Financiero Inteligente...")
        
        resultados_asesor = ejecutar_analisis_completo(
            estrategias_filtradas=estrategias_filtradas,
            kpis_seleccionados=kpis_seleccionados
        )
        
        if "error" in resultados_asesor:
            logger.error(f"❌ Error en asesor financiero: {resultados_asesor['error']}")
            return resultados_asesor
        
        # Paso 5: Generar resumen ejecutivo
        logger.info("📋 Paso 5: Generando resumen ejecutivo...")
        
        # Combinar resultados
        resultados_completos = {
            "timestamp": datetime.now().isoformat(),
            "configuracion": config,
            "resultados_core": resultados_core,
            "resultados_asesor": resultados_asesor,
            "resumen_ejecutivo": generar_resumen_ejecutivo(resultados_core, resultados_asesor)
        }
        
        # Mostrar resultados en consola
        mostrar_resultados(resultados_completos)
        
        # Guardar resultados si se especifica archivo de salida
        if output_file:
            guardar_resultados(resultados_completos, output_file)
        
        logger.info("✅ FLUJO COMPLETO FINALIZADO EXITOSAMENTE")
        return resultados_completos
        
    except Exception as e:
        logger.error(f"❌ Error en flujo completo: {e}")
        return {"error": str(e)}

def generar_resumen_ejecutivo(resultados_core: Dict[str, Any], resultados_asesor: Dict[str, Any]) -> str:
    """
    Genera un resumen ejecutivo combinando resultados del core y asesor.
    
    Args:
        resultados_core: Resultados del análisis principal
        resultados_asesor: Resultados del asesor financiero
        
    Returns:
        Resumen ejecutivo formateado
    """
    resumen = []
    resumen.append("📋 RESUMEN EJECUTIVO COMPLETO")
    resumen.append("=" * 50)
    resumen.append("")
    
    # Información del análisis principal
    resumen.append("🔧 ANÁLISIS PRINCIPAL:")
    resumen.append(f"   • Estrategias analizadas: {resultados_core.get('total_estrategias', 'N/A')}")
    resumen.append(f"   • Estrategias filtradas: {len(resultados_core.get('estrategias_filtradas', []))}")
    resumen.append(f"   • Percentil aplicado: {resultados_core.get('percentil', 'N/A')}%")
    resumen.append(f"   • Score unificado promedio: {resultados_core.get('unified_score_promedio', 'N/A'):.2f}")
    resumen.append("")
    
    # Información del asesor financiero
    if 'resultados_asesor' in resultados_asesor:
        asesor = resultados_asesor['resultados_asesor']
        
        resumen.append("🤖 ASESOR FINANCIERO INTELIGENTE:")
        
        # Correlación IS/OOS
        if 'correlacion_is_oos' in asesor:
            corr = asesor['correlacion_is_oos']
            resumen.append(f"   • Consistencia IS/OOS: {corr.get('pairs_analyzed', 0)} métricas analizadas")
            resumen.append(f"   • Métricas consistentes: {corr.get('consistent_pairs', 0)}")
        
        # Outliers
        if 'outliers' in asesor:
            outliers = asesor['outliers']
            resumen.append(f"   • Outliers detectados: {len(outliers.get('outliers', []))}")
            resumen.append(f"   • Riesgo elevado: {len(outliers.get('malos_outliers', []))}")
            resumen.append(f"   • Rendimiento excepcional: {len(outliers.get('buenos_outliers', []))}")
        
        # Clustering
        if 'clustering' in asesor:
            cluster = asesor['clustering']
            resumen.append(f"   • Clustering: Score de calidad {cluster.get('silhouette_score', 0):.3f}")
        
        # Predicción
        if 'prediccion' in asesor:
            pred = asesor['prediccion']
            resumen.append(f"   • Capacidad predictiva: R² = {pred.get('r2_mean', 0):.3f}")
        
        resumen.append("")
    
    # Consejos principales
    resumen.append("💡 CONSEJOS PRINCIPALES:")
    if 'consejos_completos' in resultados_asesor:
        consejos = resultados_asesor['consejos_completos']
        for i, consejo in enumerate(consejos[:10], 1):  # Mostrar solo los primeros 10
            resumen.append(f"   {i}. {consejo}")
    
    resumen.append("")
    resumen.append("📅 Generado el: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return "\n".join(resumen)

def mostrar_resultados(resultados: Dict[str, Any]):
    """
    Muestra los resultados en la consola.
    
    Args:
        resultados: Resultados completos del análisis
    """
    print("\n" + "=" * 80)
    print("🎉 RESULTADOS DEL FLUJO COMPLETO")
    print("=" * 80)
    
    # Mostrar resumen ejecutivo
    if 'resumen_ejecutivo' in resultados:
        print(resultados['resumen_ejecutivo'])
    
    # Mostrar estadísticas adicionales
    print("\n📊 ESTADÍSTICAS ADICIONALES:")
    print("-" * 40)
    
    core = resultados.get('resultados_core', {})
    asesor = resultados.get('resultados_asesor', {}).get('resultados_asesor', {})
    
    print(f"   • Tiempo de ejecución: {resultados.get('timestamp', 'N/A')}")
    print(f"   • Configuración: Percentil {core.get('percentil', 'N/A')}%")
    print(f"   • KPIs analizados: {len(core.get('kpis_seleccionados', []))}")
    
    if 'outliers' in asesor:
        outliers = asesor['outliers']
        print(f"   • Outliers: {len(outliers.get('outliers', []))} detectados")
    
    if 'prediccion' in asesor:
        pred = asesor['prediccion']
        print(f"   • Predicción: R² = {pred.get('r2_mean', 0):.3f}")
    
    print("\n✅ Análisis completado exitosamente!")

def guardar_resultados(resultados: Dict[str, Any], output_file: str):
    """
    Guarda los resultados en un archivo.
    
    Args:
        resultados: Resultados completos del análisis
        output_file: Ruta del archivo de salida
    """
    try:
        # Crear directorio si no existe
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar como JSON
        json_file = output_file.replace('.txt', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
        
        # Guardar resumen ejecutivo como texto
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(resultados.get('resumen_ejecutivo', 'Sin resumen disponible'))
        
        logger.info(f"✅ Resultados guardados:")
        logger.info(f"   • JSON: {json_file}")
        logger.info(f"   • Texto: {output_file}")
        
    except Exception as e:
        logger.error(f"❌ Error guardando resultados: {e}")

def main():
    """
    Función principal del script CLI.
    """
    parser = argparse.ArgumentParser(
        description="Script CLI para ejecutar el flujo completo del Asesor Financiero Inteligente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python cli_asesor_financiero.py
  python cli_asesor_financiero.py --percentil 95 --output reporte.txt
  python cli_asesor_financiero.py --config mi_config.json --output resultados/reporte.txt
        """
    )
    
    parser.add_argument(
        '--percentil',
        type=int,
        default=90,
        help='Percentil para filtrar estrategias (default: 90)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Archivo de salida para guardar resultados (opcional)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Archivo de configuración JSON (opcional)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    args = parser.parse_args()
    
    # Configurar logging según verbosidad
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Cargar configuración
    config = cargar_configuracion(args.config)
    
    # Actualizar configuración con argumentos de línea de comandos
    config['percentil'] = args.percentil
    
    # Ejecutar flujo completo
    resultados = ejecutar_flujo_completo(config, args.output)
    
    if 'error' in resultados:
        logger.error(f"❌ Error en el flujo: {resultados['error']}")
        sys.exit(1)
    
    logger.info("🎉 Flujo completado exitosamente!")

if __name__ == "__main__":
    main() 