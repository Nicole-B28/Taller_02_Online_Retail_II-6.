# Taller 02 - Online Retail II

## Descripción del proyecto

Este proyecto analiza el conjunto de datos Online Retail II, que contiene transacciones de una empresa de comercio minorista entre diciembre de 2009 y diciembre de 2011.

El trabajo se desarrolló en tres etapas principales:

1. Clasificación de clientes en clientes normales y clientes Premium.
2. Segmentación de clientes mediante K-Means y Mean Shift.
3. Predicción de ventas futuras mediante Random Forest.

Antes del modelado se realizó un proceso de limpieza, exploración y transformación de los datos.

---

## Estructura del proyecto

- `01_limpieza_eda.py`: limpieza, análisis exploratorio y generación de gráficos.
- `02_modelado_online_retail_II.ipynb`: clasificación, clustering y predicción de ventas.
- `data/online_retail_II.xlsx`: dataset original.
- `data/online_retail_II_limpio.csv`: dataset limpio utilizado para modelado.
- Archivos `.png`: visualizaciones generadas durante el análisis.

---

## Limpieza de datos

El dataset original contenía:

- registros duplicados;
- transacciones canceladas;
- cantidades menores o iguales a cero;
- precios menores o iguales a cero;
- valores nulos en algunas variables.

Luego del proceso de limpieza se obtuvo una base preparada para el análisis y el modelado.

---

## Parte 1: Clasificación de clientes

Se creó una nueva variable para clasificar a los clientes como:

- Normal
- Premium

Se consideró Premium al 20 % de clientes con mayor gasto total.

La base final contenía:

| Categoría | Clientes |
|---|---:|
| Normal | 4702 |
| Premium | 1176 |

Se utilizó un modelo Random Forest Classifier usando como variables:

- Recencia
- Frecuencia
- Cantidad total comprada

### Resultados

| Métrica | Resultado |
|---|---:|
| Accuracy | 93,54 % |
| Precision Premium | 0,84 |
| Recall Premium | 0,84 |
| F1-score Premium | 0,84 |

La variable más importante para identificar clientes Premium fue la cantidad total comprada.

---

## Parte 2: Segmentación de clientes

Se utilizaron las variables:

- Recencia
- Frecuencia
- Gasto total

Antes del clustering se aplicó transformación logarítmica y estandarización para reducir el efecto de valores extremos.

### K-Means

Se seleccionaron cuatro clusters:

1. Inactivos - Bajo valor
2. Recientes ocasionales
3. Alto valor
4. Intermedios - En riesgo

El Silhouette Score obtenido fue:

**0,3650**

### Mean Shift

Mean Shift identificó automáticamente tres clusters.

El Silhouette Score obtenido fue:

**0,3519**

### Comparación

| Algoritmo | Número de clusters | Silhouette |
|---|---:|---:|
| K-Means | 4 | 0,3650 |
| Mean Shift | 3 | 0,3519 |

K-Means produjo una segmentación más equilibrada e interpretable desde el punto de vista comercial.

---

## Parte 3: Predicción de ventas

Se construyó una serie diaria continua de ventas y se crearon características temporales como:

- día de la semana;
- mes;
- semana del año;
- trimestre;
- ventas del día anterior;
- ventas de hace 7, 14 y 28 días;
- medias móviles de 7 y 28 días.

Se utilizó un Random Forest Regressor respetando el orden cronológico de los datos.

### Resultados del modelo final

| Métrica | Resultado |
|---|---:|
| MAE | £10.809,01 |
| RMSE | £18.934,37 |
| R² | 0,5409 |

El modelo superó a dos modelos base basados en las ventas del día anterior y de la semana anterior.

Las variables más importantes fueron:

1. Media móvil de 7 días
2. Ventas de hace 7 días
3. Indicador de fin de semana
4. Día de la semana
5. Ventas del día anterior

---

## Conclusiones

El análisis permitió identificar diferentes perfiles de clientes y patrones de comportamiento comercial.

La clasificación permitió distinguir clientes Premium con una precisión elevada.

La segmentación mostró que K-Means generó grupos más útiles para la toma de decisiones comerciales que Mean Shift.

Finalmente, el modelo predictivo logró capturar una parte importante del comportamiento de las ventas diarias, aunque presentó dificultades para anticipar algunos picos de ventas extraordinarios.