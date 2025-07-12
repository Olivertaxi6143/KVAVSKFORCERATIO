# 📊 MANUAL OPERATIVO - CARPETA ML

## 🎯 **OBJETIVO PRINCIPAL**
La carpeta `src/ml/` contiene los **modelos de machine learning** del sistema KVAVSKFORCERATIO. Proporciona capacidades predictivas avanzadas, clasificación automática y optimización de portfolios basada en algoritmos de inteligencia artificial.

## 🔧 **COMPONENTES PRINCIPALES**

### **1. advanced_ml_validation.py**
**Función:** Validación avanzada de modelos ML
- **Cross-validation:** Validación cruzada robusta de modelos
- **Backtesting:** Pruebas retrospectivas de estrategias
- **Análisis de overfitting:** Detección de sobreajuste
- **Métricas de performance:** Evaluación de precisión y robustez

## 🔄 **FLUJO DE TRABAJO**

### **FASE 1: PREPARACIÓN DE DATOS**
1. **Feature engineering:** Creación de variables predictoras
2. **Normalización:** Estandarización de datos para ML
3. **División temporal:** Separación en train/validation/test
4. **Validación de calidad:** Verificación de integridad de datos

### **FASE 2: SELECCIÓN DE MODELOS**
1. **Análisis exploratorio:** Identificación de patrones en datos
2. **Selección de algoritmos:** Elección de modelos apropiados
3. **Configuración de hiperparámetros:** Optimización de parámetros
4. **Validación de supuestos:** Verificación de requisitos de modelos

### **FASE 3: ENTRENAMIENTO Y VALIDACIÓN**
1. **Entrenamiento:** Ajuste de modelos a datos históricos
2. **Validación cruzada:** Evaluación de robustez
3. **Análisis de overfitting:** Detección de sobreajuste
4. **Optimización:** Ajuste de hiperparámetros

### **FASE 4: EVALUACIÓN Y TESTING**
1. **Testing en datos no vistos:** Evaluación final de performance
2. **Análisis de errores:** Identificación de casos problemáticos
3. **Validación temporal:** Walk-forward testing
4. **Stress testing:** Pruebas en condiciones extremas

### **FASE 5: IMPLEMENTACIÓN Y MONITOREO**
1. **Despliegue:** Integración en sistema principal
2. **Monitoreo continuo:** Seguimiento de performance
3. **Actualización:** Re-entrenamiento periódico
4. **Documentación:** Registro de cambios y mejoras

## 📈 **TIPOS DE MODELOS**

### **Clasificación**
- **Random Forest:** Para clasificación de estrategias
- **Gradient Boosting:** Para predicción de rendimiento
- **Support Vector Machines:** Para clasificación no lineal
- **Neural Networks:** Para patrones complejos

### **Regresión**
- **Linear Regression:** Para predicción de métricas
- **Ridge/Lasso:** Para regresión con regularización
- **Elastic Net:** Para selección de features
- **Polynomial Regression:** Para relaciones no lineales

### **Clustering**
- **K-Means:** Para agrupación de estrategias
- **Hierarchical Clustering:** Para jerarquías de estrategias
- **DBSCAN:** Para detección de outliers
- **Gaussian Mixture:** Para modelos probabilísticos

### **Time Series**
- **ARIMA:** Para predicción temporal
- **LSTM:** Para patrones temporales complejos
- **Prophet:** Para forecasting de métricas
- **VAR:** Para series temporales multivariadas

## 🎨 **CARACTERÍSTICAS TÉCNICAS**

### **Robustez**
- **Validación cruzada:** Evaluación robusta de modelos
- **Análisis de overfitting:** Detección de sobreajuste
- **Regularización:** Prevención de overfitting
- **Ensemble methods:** Combinación de múltiples modelos

### **Escalabilidad**
- **Procesamiento paralelo:** Entrenamiento en múltiples núcleos
- **Optimización de memoria:** Gestión eficiente de datasets
- **Caché inteligente:** Almacenamiento de modelos entrenados
- **Incremental learning:** Aprendizaje continuo

### **Interpretabilidad**
- **Feature importance:** Importancia de variables predictoras
- **SHAP values:** Explicación de predicciones
- **Partial dependence plots:** Relaciones variables-target
- **Model interpretability:** Explicación de decisiones

## 🔍 **INTEGRACIÓN CON OTRAS CARPETAS**

### **Con CORE:**
- **Alimentación de datos:** Recibe datos procesados para ML
- **Validación de resultados:** Verifica predicciones de modelos
- **Enriquecimiento:** Añade predicciones a análisis básicos
- **Configuración:** Recibe parámetros de modelos

### **Con DATA:**
- **Feature engineering:** Prepara variables para ML
- **Validación de calidad:** Verifica integridad de datos
- **Preprocesamiento:** Normalización y limpieza
- **Exportación:** Genera datasets para entrenamiento

### **Con ANALYSIS:**
- **Validación científica:** Verifica resultados de ML
- **Análisis de performance:** Evalúa precisión de modelos
- **Comparación:** Compara ML vs métodos tradicionales
- **Documentación:** Registra metodologías ML

### **Con GUI:**
- **Visualización de predicciones:** Gráficos de resultados ML
- **Interfaz de modelos:** Controles para entrenamiento
- **Reportes ML:** Documentación de modelos
- **Exportación:** Genera reportes de ML

## 📋 **METODOLOGÍAS ML**

### **Supervised Learning**
- **Clasificación:** Predicción de categorías de estrategias
- **Regresión:** Predicción de métricas continuas
- **Time series forecasting:** Predicción temporal
- **Anomaly detection:** Detección de outliers

### **Unsupervised Learning**
- **Clustering:** Agrupación de estrategias similares
- **Dimensionality reduction:** Reducción de dimensionalidad
- **Association rules:** Descubrimiento de patrones
- **Topic modeling:** Análisis de temas en datos

### **Reinforcement Learning**
- **Portfolio optimization:** Optimización de portfolios
- **Trading strategy:** Estrategias de trading automático
- **Risk management:** Gestión de riesgo adaptativa
- **Dynamic allocation:** Asignación dinámica de capital

### **Deep Learning**
- **Neural networks:** Modelos de redes neuronales
- **LSTM/GRU:** Para series temporales
- **CNN:** Para análisis de patrones
- **Autoencoders:** Para reducción de dimensionalidad

## 🚀 **OPTIMIZACIONES IMPLEMENTADAS**

### **Rendimiento**
- **Vectorización:** Cálculos optimizados con NumPy
- **Paralelización:** Entrenamiento en múltiples núcleos
- **GPU acceleration:** Uso de GPUs para deep learning
- **Distributed computing:** Procesamiento distribuido

### **Precisión**
- **Hyperparameter tuning:** Optimización automática de parámetros
- **Cross-validation:** Validación robusta de modelos
- **Ensemble methods:** Combinación de múltiples modelos
- **Regularization:** Prevención de overfitting

### **Usabilidad**
- **AutoML:** Selección automática de mejores modelos
- **Pipeline automation:** Automatización de flujos ML
- **Model versioning:** Control de versiones de modelos
- **A/B testing:** Comparación de modelos

## 🔧 **CONFIGURACIÓN AVANZADA**

### **Parámetros de Modelos**
- **Hyperparameters:** Configuración de algoritmos
- **Validation strategy:** Estrategia de validación
- **Feature selection:** Selección de variables
- **Ensemble configuration:** Configuración de ensembles

### **Validaciones Específicas**
- **Cross-validation folds:** Número de folds
- **Test size:** Tamaño del conjunto de test
- **Random state:** Semilla para reproducibilidad
- **Scoring metrics:** Métricas de evaluación

### **Optimizaciones de Rendimiento**
- **Batch size:** Tamaño de lotes para entrenamiento
- **Learning rate:** Tasa de aprendizaje
- **Early stopping:** Parada temprana para evitar overfitting
- **Model checkpointing:** Guardado de mejores modelos

## 📊 **MÉTRICAS DE EVALUACIÓN**

### **Clasificación**
- **Accuracy:** Precisión general
- **Precision/Recall:** Precisión y recall por clase
- **F1-Score:** Media armónica de precisión y recall
- **ROC-AUC:** Área bajo curva ROC

### **Regresión**
- **MSE/RMSE:** Error cuadrático medio
- **MAE:** Error absoluto medio
- **R²:** Coeficiente de determinación
- **MAPE:** Error porcentual absoluto medio

### **Time Series**
- **MAPE:** Error porcentual absoluto medio
- **RMSE:** Raíz del error cuadrático medio
- **MAE:** Error absoluto medio
- **Directional accuracy:** Precisión direccional

---

**💡 NOTA:** Los modelos de ML deben ser validados exhaustivamente antes de su implementación. Es fundamental mantener un equilibrio entre complejidad del modelo y interpretabilidad. La documentación debe incluir metodologías, validaciones y limitaciones de cada modelo. 