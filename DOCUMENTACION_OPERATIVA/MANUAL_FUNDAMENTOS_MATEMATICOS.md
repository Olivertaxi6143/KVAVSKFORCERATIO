# 📊 MANUAL DE FUNDAMENTOS MATEMÁTICOS - KVAVSKFORCERATIO

## 🎯 **OBJETIVO DEL MANUAL**

Este documento proporciona los **fundamentos matemáticos específicos** de cada cálculo en KVAVSKFORCERATIO, incluyendo las fórmulas detalladas, derivaciones y justificaciones teóricas que respaldan cada métrica.

## 🔬 **FUNDAMENTOS ESTADÍSTICOS**

### **1. Normalización con Función Sigmoide**

#### **¿Qué es?**
La función sigmoide transforma cualquier valor real en un rango entre 0 y 1.

#### **Fórmula Matemática:**
```
σ(x) = 1 / (1 + e^(-x))
```

#### **¿Por qué se usa?**
- **Rango Controlado:** Limita valores entre 0 y 1
- **Suavizado:** Evita valores extremos
- **Interpretabilidad:** Facilita la comprensión

#### **Derivación:**
```
Para normalizar un valor x:
1. Calcular z-score: z = (x - μ) / σ
2. Aplicar sigmoide: σ(z) = 1 / (1 + e^(-z))
3. Resultado: Valor entre 0 y 1
```

### **2. Cálculo de CAGR (Compound Annual Growth Rate)**

#### **Fórmula Matemática:**
```
CAGR = ((Vf / Vi)^(1/n) - 1) × 100
```

Donde:
- **Vf:** Valor final
- **Vi:** Valor inicial  
- **n:** Número de años
- **CAGR:** Tasa de crecimiento anual compuesto

#### **Derivación Matemática:**
```
1. Valor futuro: Vf = Vi × (1 + r)^n
2. Despejar tasa: r = (Vf/Vi)^(1/n) - 1
3. Convertir a porcentaje: CAGR = r × 100
```

#### **Ejemplo Práctico:**
```
Valor inicial: $10,000
Valor final: $15,000
Período: 3 años

CAGR = ((15,000/10,000)^(1/3) - 1) × 100
CAGR = (1.5^(1/3) - 1) × 100
CAGR = (1.1447 - 1) × 100
CAGR = 14.47%
```

### **3. Sharpe Ratio**

#### **Fórmula Matemática:**
```
Sharpe = (Rp - Rf) / σp
```

Donde:
- **Rp:** Rendimiento del portfolio
- **Rf:** Tasa libre de riesgo
- **σp:** Desviación estándar del portfolio

#### **Cálculo de Desviación Estándar:**
```
σ = √(Σ(xi - μ)² / n)
```

Donde:
- **xi:** Rendimiento del período i
- **μ:** Rendimiento promedio
- **n:** Número de períodos

#### **Interpretación:**
- **Sharpe > 1:** Excelente (rentabilidad > riesgo)
- **Sharpe 0.5-1:** Bueno
- **Sharpe 0-0.5:** Regular
- **Sharpe < 0:** Deficiente

### **4. Maximum Drawdown**

#### **Fórmula Matemática:**
```
MaxDD = max((Pico - Valle) / Pico)
```

#### **Algoritmo de Cálculo:**
```python
def calculate_max_drawdown(equity_curve):
    peak = equity_curve[0]
    max_dd = 0
    
    for value in equity_curve:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_dd:
            max_dd = drawdown
    
    return max_dd
```

#### **Ejemplo:**
```
Equity Curve: [100, 110, 105, 120, 115, 130]
Picos: [100, 110, 110, 120, 120, 130]
Drawdowns: [0, 0, 0.045, 0, 0.042, 0]
MaxDD = 4.5%
```

### **5. Calmar Ratio**

#### **Fórmula Matemática:**
```
Calmar = CAGR / MaxDD
```

#### **Interpretación:**
- **Calmar > 3:** Excelente
- **Calmar 1-3:** Bueno
- **Calmar 0.5-1:** Regular
- **Calmar < 0.5:** Deficiente

### **6. System Quality Number (SQN)**

#### **Fórmula Matemática:**
```
SQN = (Expectancy / σ) × √N
```

Donde:
- **Expectancy:** Rendimiento esperado por trade
- **σ:** Desviación estándar de trades
- **N:** Número de trades

#### **Cálculo de Expectancy:**
```
Expectancy = (Win Rate × Avg Win) - ((1 - Win Rate) × Avg Loss)
```

#### **Interpretación:**
- **SQN > 2:** Excelente
- **SQN 1.5-2:** Muy Bueno
- **SQN 1-1.5:** Bueno
- **SQN < 1:** Deficiente

## 📊 **FUNDAMENTOS DEL FACTOR K 9.6**

### **Componente S (Stability) - Estabilidad**

#### **Fórmula Matemática:**
```
S = σ_normalized × (1 - MaxDD_normalized)
```

Donde:
- **σ_normalized:** Volatilidad normalizada (0-1)
- **MaxDD_normalized:** Drawdown normalizado (0-1)

#### **Lógica Matemática:**
- **Menor volatilidad:** Mayor estabilidad
- **Menor drawdown:** Mayor estabilidad
- **Producto:** Penaliza alta volatilidad Y alto drawdown

### **Componente G (Growth) - Crecimiento**

#### **Fórmula Matemática:**
```
G = CAGR_normalized × (1 + Profit Factor_normalized)
```

Donde:
- **CAGR_normalized:** Crecimiento normalizado
- **Profit Factor_normalized:** Eficiencia normalizada

#### **Lógica Matemática:**
- **CAGR alto:** Crecimiento sostenible
- **Profit Factor alto:** Eficiencia en ganancias
- **Suma ponderada:** Favorece crecimiento eficiente

### **Componente E (Efficiency) - Eficiencia**

#### **Fórmula Matemática:**
```
E = Sharpe_normalized × Calmar_normalized
```

#### **Lógica Matemática:**
- **Sharpe alto:** Buena relación riesgo-rendimiento
- **Calmar alto:** Buena recuperación de pérdidas
- **Producto:** Favorece eficiencia integral

### **Componente C (Consistency) - Consistencia**

#### **Fórmula Matemática:**
```
C = Win_Rate_normalized × SQN_normalized
```

#### **Lógica Matemática:**
- **Win Rate alto:** Consistencia en resultados
- **SQN alto:** Calidad del sistema
- **Producto:** Favorece consistencia de calidad

### **Componente T (Temporal) - Análisis Temporal**

#### **Fórmula Matemática:**
```
T = Stability_over_time × Trend_consistency
```

Donde:
- **Stability_over_time:** Estabilidad temporal
- **Trend_consistency:** Consistencia de tendencia

#### **Cálculo de Estabilidad Temporal:**
```
Stability_over_time = 1 - (σ_rolling / σ_total)
```

### **Componente P (Predictability) - Predictibilidad**

#### **Fórmula Matemática:**
```
P = R²_score × Forecast_accuracy
```

Donde:
- **R²_score:** Coeficiente de determinación
- **Forecast_accuracy:** Precisión de predicciones

## 🔄 **FUNDAMENTOS DEL QVA SCORE**

### **Subcomponente Rentabilidad**

#### **Fórmula Matemática:**
```
Rentabilidad = (CAGR_normalized × 0.4) + (Profit_Factor_normalized × 0.4) + (Net_Profit_normalized × 0.2)
```

#### **Pesos Justificados:**
- **CAGR (40%):** Crecimiento sostenible
- **Profit Factor (40%):** Eficiencia de ganancias
- **Net Profit (20%):** Rendimiento absoluto

### **Subcomponente Riesgo**

#### **Fórmula Matemática:**
```
Riesgo = (Sharpe_normalized × 0.4) + (MaxDD_normalized × 0.3) + (VaR_normalized × 0.3)
```

#### **Pesos Justificados:**
- **Sharpe (40%):** Eficiencia riesgo-rendimiento
- **MaxDD (30%):** Riesgo de pérdida máxima
- **VaR (30%):** Riesgo de cola

### **Subcomponente Consistencia**

#### **Fórmula Matemática:**
```
Consistencia = (Win_Rate_normalized × 0.4) + (Calmar_normalized × 0.3) + (SQN_normalized × 0.3)
```

#### **Pesos Justificados:**
- **Win Rate (40%):** Frecuencia de éxito
- **Calmar (30%):** Eficiencia de recuperación
- **SQN (30%):** Calidad del sistema

## 📈 **FUNDAMENTOS DE VALIDACIÓN TEMPORAL**

### **Walk-Forward Analysis**

#### **Algoritmo Matemático:**
```
Para cada ventana temporal:
1. Train_data = datos[inicio:fin_train]
2. Test_data = datos[fin_train:fin_test]
3. Modelo = entrenar(train_data)
4. Predicción = predecir(modelo, test_data)
5. Métrica = evaluar(predicción, test_data)
6. Resultado = agregar(métrica)
```

#### **Métricas de Validación:**
```
- Accuracy = (predicciones_correctas / total_predicciones)
- Sharpe_ratio = calcular_sharpe(rendimientos_predichos)
- MaxDD = calcular_maxdd(equity_curve_predicha)
```

### **Stress Testing**

#### **Escenarios Matemáticos:**
```
1. Crisis 2008: Simular condiciones de 2008
2. Volatilidad Extrema: σ × 3
3. Correlación Perfecta: ρ = 1 entre activos
4. Liquidez Cero: Spread infinito
```

#### **Cálculo de Impacto:**
```
Impacto = (Rendimiento_estresado - Rendimiento_normal) / Rendimiento_normal
```

## 🤖 **FUNDAMENTOS DE MACHINE LEARNING**

### **Feature Engineering**

#### **Métricas Técnicas:**
```
- RSI = 100 - (100 / (1 + RS))
- MACD = EMA_12 - EMA_26
- Bollinger_Bands = SMA ± (2 × σ)
- ATR = promedio(TR_1, TR_2, ..., TR_n)
```

#### **Métricas de Mercado:**
```
- Volatilidad = σ(rendimientos)
- Correlación = cov(X,Y) / (σ_X × σ_Y)
- Beta = cov(estrategia, mercado) / var(mercado)
```

### **Validación Cruzada**

#### **K-Fold Cross Validation:**
```
Para k = 1 a K:
1. Dividir datos en K folds
2. Entrenar en K-1 folds
3. Validar en 1 fold
4. Calcular métrica
Promedio = Σ(métricas) / K
```

#### **Time Series Cross Validation:**
```
Para cada punto temporal t:
1. Train = datos[0:t]
2. Test = datos[t:t+1]
3. Entrenar modelo en train
4. Predecir en test
5. Calcular error
```

## 📊 **FUNDAMENTOS DE OPTIMIZACIÓN**

### **Optimización de Portfolios**

#### **Markowitz Modern Portfolio Theory:**
```
Minimizar: σ²_p = Σ Σ w_i × w_j × σ_ij
Sujeto a: Σ w_i = 1
         w_i ≥ 0 (sin ventas cortas)
```

Donde:
- **w_i:** Peso del activo i
- **σ_ij:** Covarianza entre activos i y j
- **σ²_p:** Varianza del portfolio

#### **Optimización con Restricciones:**
```
Maximizar: Sharpe Ratio
Sujeto a: MaxDD ≤ límite_drawdown
         Concentración ≤ límite_concentración
         Correlación ≤ límite_correlación
```

### **Optimización de Hiperparámetros**

#### **Grid Search:**
```
Para cada combinación de parámetros:
1. Entrenar modelo
2. Validar performance
3. Seleccionar mejor combinación
```

#### **Bayesian Optimization:**
```
1. Definir espacio de parámetros
2. Muestrear puntos iniciales
3. Para cada iteración:
   - Ajustar modelo de probabilidad
   - Seleccionar siguiente punto (acquisition function)
   - Evaluar función objetivo
4. Retornar mejor parámetro
```

## 🔍 **FUNDAMENTOS DE DETECCIÓN DE ANOMALÍAS**

### **Método Estadístico (Z-Score)**

#### **Fórmula Matemática:**
```
Z = (x - μ) / σ
```

#### **Criterio de Detección:**
```
Si |Z| > 3: Anomalía (99.7% confianza)
Si |Z| > 2: Posible anomalía (95% confianza)
```

### **Método de Percentiles**

#### **Fórmula Matemática:**
```
Percentil = (rank - 0.5) / n × 100
```

#### **Criterio de Detección:**
```
Si percentil < 1% o > 99%: Anomalía
```

### **Método IQR (Interquartile Range)**

#### **Fórmula Matemática:**
```
Q1 = percentil_25(datos)
Q3 = percentil_75(datos)
IQR = Q3 - Q1
Límite_inferior = Q1 - 1.5 × IQR
Límite_superior = Q3 + 1.5 × IQR
```

#### **Criterio de Detección:**
```
Si x < límite_inferior o x > límite_superior: Anomalía
```

## 📋 **FUNDAMENTOS DE CATEGORIZACIÓN**

### **Umbrales de Factor K**

#### **Criterios Matemáticos:**
```
Elite: FactorK ≥ 9.2 (top 5%)
Excellent: FactorK ≥ 8.2 (top 15%)
Very Good: FactorK ≥ 7.2 (top 30%)
Good: FactorK ≥ 6.2 (top 50%)
Regular: FactorK ≥ 5.2 (top 70%)
Poor: FactorK < 5.2 (bottom 30%)
```

#### **Justificación Estadística:**
- **Percentiles:** Basado en distribución histórica
- **Significancia:** Diferencia estadísticamente significativa
- **Acción:** Cada categoría sugiere acciones específicas

### **Umbrales de QVA**

#### **Criterios Matemáticos:**
```
Elite: QVA ≥ 8.5
Excellent: QVA ≥ 7.5
Very Good: QVA ≥ 6.5
Good: QVA ≥ 5.5
Regular: QVA ≥ 4.5
Poor: QVA < 4.5
```

## 💡 **FUNDAMENTOS DE DECISIONES DE DISEÑO**

### **Arquitectura Modular**

#### **Principios Matemáticos:**
```
Cohesión = Σ(funciones_relacionadas) / total_funciones
Acoplamiento = Σ(dependencias_externas) / total_dependencias
```

#### **Objetivo:**
- **Alta cohesión:** Funciones relacionadas juntas
- **Bajo acoplamiento:** Mínimas dependencias externas

### **Optimización de Rendimiento**

#### **Complejidad Temporal:**
```
O(n log n): Algoritmos eficientes
O(n²): Evitar en datasets grandes
O(2^n): Evitar completamente
```

#### **Complejidad Espacial:**
```
O(n): Uso de memoria lineal
O(n²): Evitar en datasets grandes
O(1): Constante (ideal)
```

---

**🎯 CONCLUSIÓN:** Los fundamentos matemáticos de KVAVSKFORCERATIO están basados en principios estadísticos sólidos, teoría financiera probada y algoritmos de machine learning validados. Cada fórmula tiene una justificación teórica clara y una aplicación práctica específica.

**📊 VALOR:** Esta comprensión matemática profunda permite no solo usar el sistema, sino entender por qué cada cálculo es importante y cómo contribuye al análisis final de las estrategias de trading. 