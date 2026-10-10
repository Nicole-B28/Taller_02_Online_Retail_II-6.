import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("Pandas:", pd.__version__)
print("NumPy:", np.__version__)
print("Librerías de análisis cargadas correctamente")

# Ruta del archivo
archivo = "data/online_retail_II.xlsx"

# Cargar las dos hojas
df_2009_2010 = pd.read_excel(archivo, sheet_name="Year 2009-2010")
df_2010_2011 = pd.read_excel(archivo, sheet_name="Year 2010-2011")

# Unir ambos periodos
df = pd.concat([df_2009_2010, df_2010_2011], ignore_index=True)

# Auditoría inicial de calidad
auditoria = pd.DataFrame({
    "Indicador": [
        "Registros totales",
        "Duplicados exactos",
        "Facturas canceladas",
        "Customer ID nulo",
        "Descripción nula",
        "Cantidad <= 0",
        "Precio = 0",
        "Precio < 0"
    ],
    "Cantidad": [
        len(df),
        df.duplicated().sum(),
        df["Invoice"].astype(str).str.startswith("C").sum(),
        df["Customer ID"].isna().sum(),
        df["Description"].isna().sum(),
        (df["Quantity"] <= 0).sum(),
        (df["Price"] == 0).sum(),
        (df["Price"] < 0).sum()
    ]
})

print("\n=== AUDITORÍA INICIAL DEL DATASET ===")
print(auditoria.to_string(index=False))

print("\nPeriodo analizado:")
print(df["InvoiceDate"].min(), "hasta", df["InvoiceDate"].max())

print("\nDimensiones del dataset:")
print(df.shape)

# ============================================================
# LIMPIEZA DE DATOS
# ============================================================

print("\n=== INICIO DE LIMPIEZA ===")

# Crear copia para no modificar el dataset original
df_limpio = df.copy()

# 1. Eliminar duplicados exactos
antes = len(df_limpio)
df_limpio = df_limpio.drop_duplicates()
despues = len(df_limpio)

print("Duplicados eliminados:", antes - despues)


# 2. Separar las facturas canceladas
df_cancelaciones = df_limpio[
    df_limpio["Invoice"].astype(str).str.startswith("C")
].copy()

# Mantener únicamente transacciones que no sean cancelaciones
df_limpio = df_limpio[
    ~df_limpio["Invoice"].astype(str).str.startswith("C")
].copy()

print("Cancelaciones separadas:", len(df_cancelaciones))


# 3. Eliminar cantidades no válidas para ventas
antes = len(df_limpio)

df_limpio = df_limpio[
    df_limpio["Quantity"] > 0
].copy()

print("Registros eliminados por Quantity <= 0:", antes - len(df_limpio))


# 4. Eliminar precios no válidos para ventas
antes = len(df_limpio)

df_limpio = df_limpio[
    df_limpio["Price"] > 0
].copy()

print("Registros eliminados por Price <= 0:", antes - len(df_limpio))


# 5. Crear valor monetario de cada línea de compra
df_limpio["TotalAmount"] = (
    df_limpio["Quantity"] * df_limpio["Price"]
)


# 6. Convertir Customer ID a entero nullable
df_limpio["Customer ID"] = (
    df_limpio["Customer ID"].astype("Int64")
)


print("\n=== RESULTADO DE LA LIMPIEZA ===")
print("Registros finales:", len(df_limpio))
print("Duplicados restantes:", df_limpio.duplicated().sum())
print("Quantity <= 0:", (df_limpio["Quantity"] <= 0).sum())
print("Price <= 0:", (df_limpio["Price"] <= 0).sum())
print("Customer ID nulo:", df_limpio["Customer ID"].isna().sum())
print("Description nula:", df_limpio["Description"].isna().sum())

# ============================================================
# GUARDAR DATASET LIMPIO
# ============================================================

df_limpio.to_csv(
    "data/online_retail_II_limpio.csv",
    index=False
)

print("\nDataset limpio guardado correctamente.")

resumen_limpieza = pd.DataFrame({
    "Indicador": [
        "Registros",
        "Duplicados",
        "Quantity <= 0",
        "Price <= 0",
        "Description nula"
    ],
    "Antes": [
        len(df),
        df.duplicated().sum(),
        (df["Quantity"] <= 0).sum(),
        (df["Price"] <= 0).sum(),
        df["Description"].isna().sum()
    ],
    "Después": [
        len(df_limpio),
        df_limpio.duplicated().sum(),
        (df_limpio["Quantity"] <= 0).sum(),
        (df_limpio["Price"] <= 0).sum(),
        df_limpio["Description"].isna().sum()
    ]
})

print("\n=== COMPARACIÓN ANTES VS. DESPUÉS ===")
print(resumen_limpieza.to_string(index=False))

# ============================================================
# EDA 1: DISTRIBUCIÓN DE VARIABLES CLAVE
# ============================================================

print("\n=== RESUMEN ESTADÍSTICO DE VARIABLES CLAVE ===")

resumen_variables = df_limpio[
    ["Quantity", "Price", "TotalAmount"]
].describe(
    percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
).T

print(resumen_variables.round(2))

# Medianas, útiles porque las distribuciones pueden estar sesgadas
print("\nMedianas:")
print(
    df_limpio[
        ["Quantity", "Price", "TotalAmount"]
    ].median().round(2)
)

# ============================================================
# GRÁFICA: DISTRIBUCIÓN DE QUANTITY
# ============================================================

limite_quantity = df_limpio["Quantity"].quantile(0.99)

quantity_visual = df_limpio[
    df_limpio["Quantity"] <= limite_quantity
]

plt.figure(figsize=(11, 6))

plt.hist(
    quantity_visual["Quantity"],
    bins=50,
    edgecolor="black",
    alpha=0.75
)

plt.axvline(
    df_limpio["Quantity"].median(),
    linestyle="--",
    linewidth=2,
    label=f'Mediana = {df_limpio["Quantity"].median():.1f}'
)

plt.title(
    "Distribución de la cantidad comprada por transacción\n"
    "(visualización hasta el percentil 99)"
)

plt.xlabel("Cantidad de unidades")
plt.ylabel("Número de registros")
plt.legend()
plt.grid(alpha=0.20)
plt.tight_layout()

plt.savefig(
    "grafico_distribucion_quantity.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# GRÁFICA: DISTRIBUCIÓN DE PRICE
# ============================================================

limite_price = df_limpio["Price"].quantile(0.99)

price_visual = df_limpio[
    df_limpio["Price"] <= limite_price
]

plt.figure(figsize=(11, 6))

plt.hist(
    price_visual["Price"],
    bins=50,
    edgecolor="black",
    alpha=0.75
)

plt.axvline(
    df_limpio["Price"].median(),
    linestyle="--",
    linewidth=2,
    label=f'Mediana = £{df_limpio["Price"].median():.2f}'
)

plt.title(
    "Distribución del precio unitario\n"
    "(visualización hasta el percentil 99)"
)

plt.xlabel("Precio unitario (£)")
plt.ylabel("Número de registros")
plt.legend()
plt.grid(alpha=0.20)
plt.tight_layout()

plt.savefig(
    "grafico_distribucion_price.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

tabla_distribucion = pd.DataFrame({
    "Variable": ["Quantity", "Price", "TotalAmount"],
    "Media": [
        df_limpio["Quantity"].mean(),
        df_limpio["Price"].mean(),
        df_limpio["TotalAmount"].mean()
    ],
    "Mediana": [
        df_limpio["Quantity"].median(),
        df_limpio["Price"].median(),
        df_limpio["TotalAmount"].median()
    ],
    "Percentil 90": [
        df_limpio["Quantity"].quantile(0.90),
        df_limpio["Price"].quantile(0.90),
        df_limpio["TotalAmount"].quantile(0.90)
    ],
    "Percentil 99": [
        df_limpio["Quantity"].quantile(0.99),
        df_limpio["Price"].quantile(0.99),
        df_limpio["TotalAmount"].quantile(0.99)
    ]
}).round(2)

# ============================================================
# BASE ESPECÍFICA PARA ANÁLISIS DE PRODUCTOS
# ============================================================

conceptos_no_producto = [
    "Manual",
    "POSTAGE",
    "DOTCOM POSTAGE"
]

df_productos = df_limpio[
    ~df_limpio["Description"].isin(conceptos_no_producto)
].copy()

# ============================================================
# EDA 2: PRODUCTOS MÁS VENDIDOS
# ============================================================

productos_resumen = (
    df_productos
    .groupby(["StockCode", "Description"])
    .agg(
        Cantidad_total=("Quantity", "sum"),
        Ingresos_totales=("TotalAmount", "sum"),
        Facturas=("Invoice", "nunique")
    )
    .reset_index()
)

top_cantidad = (
    productos_resumen
    .sort_values("Cantidad_total", ascending=False)
    .head(10)
)

top_ingresos = (
    productos_resumen
    .sort_values("Ingresos_totales", ascending=False)
    .head(10)
)

print("\n=== TOP 10 PRODUCTOS POR CANTIDAD VENDIDA ===")
print(
    top_cantidad[
        ["Description", "Cantidad_total", "Ingresos_totales"]
    ].to_string(index=False)
)

print("\n=== TOP 10 PRODUCTOS POR INGRESOS ===")
print(
    top_ingresos[
        ["Description", "Cantidad_total", "Ingresos_totales"]
    ].to_string(index=False)
)

# ============================================================
# GRÁFICA: TOP 10 POR CANTIDAD
# ============================================================

plt.figure(figsize=(12, 7))

datos_plot = top_cantidad.sort_values("Cantidad_total")

plt.barh(
    datos_plot["Description"],
    datos_plot["Cantidad_total"]
)

plt.title("Top 10 productos por cantidad total vendida")
plt.xlabel("Cantidad total vendida")
plt.ylabel("Producto")
plt.grid(axis="x", alpha=0.2)
plt.tight_layout()

plt.savefig(
    "grafico_top_productos_cantidad.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# GRÁFICA: TOP 10 POR INGRESOS
# ============================================================

plt.figure(figsize=(12, 7))

datos_plot = top_ingresos.sort_values("Ingresos_totales")

plt.barh(
    datos_plot["Description"],
    datos_plot["Ingresos_totales"]
)

plt.title("Top 10 productos por ingresos generados")
plt.xlabel("Ingresos totales (£)")
plt.ylabel("Producto")
plt.grid(axis="x", alpha=0.2)
plt.tight_layout()

plt.savefig(
    "grafico_top_productos_ingresos.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# EDA 3: TENDENCIA MENSUAL DE LOS PRODUCTOS LÍDERES
# ============================================================

# Seleccionar los 5 productos con mayor cantidad vendida
top5_productos = top_cantidad["Description"].head(5).tolist()

# Crear una columna mensual
df_productos["Mes"] = (
    df_productos["InvoiceDate"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

# Filtrar únicamente los 5 productos principales
tendencia_top5 = (
    df_productos[
        df_productos["Description"].isin(top5_productos)
    ]
    .groupby(["Mes", "Description"])["Quantity"]
    .sum()
    .reset_index()
)

print("\n=== TENDENCIA MENSUAL DE LOS 5 PRODUCTOS PRINCIPALES ===")
print(tendencia_top5.head(15).to_string(index=False))

plt.figure(figsize=(13, 7))

for producto in top5_productos:
    datos_producto = tendencia_top5[
        tendencia_top5["Description"] == producto
    ]

    plt.plot(
        datos_producto["Mes"],
        datos_producto["Quantity"],
        marker="o",
        linewidth=2,
        label=producto
    )

plt.title(
    "Evolución mensual de los 5 productos con mayor volumen de ventas"
)

plt.xlabel("Mes")
plt.ylabel("Cantidad vendida")
plt.legend(
    title="Producto",
    fontsize=8
)
plt.grid(alpha=0.25)
plt.tight_layout()

plt.savefig(
    "grafico_tendencia_top5_productos.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# INVESTIGAR PICOS EXTRAORDINARIOS DE LOS PRODUCTOS TOP
# ============================================================

picos_productos = (
    tendencia_top5
    .sort_values("Quantity", ascending=False)
    .head(10)
)

print("\n=== MAYORES PICOS MENSUALES DE LOS PRODUCTOS TOP ===")
print(picos_productos.to_string(index=False))


# Transacciones individuales más grandes de esos productos
transacciones_extremas = (
    df_productos[
        df_productos["Description"].isin(top5_productos)
    ]
    .sort_values("Quantity", ascending=False)
    [
        [
            "Invoice",
            "InvoiceDate",
            "Description",
            "Quantity",
            "Price",
            "TotalAmount",
            "Customer ID",
            "Country"
        ]
    ]
    .head(15)
)

print("\n=== TRANSACCIONES INDIVIDUALES MÁS GRANDES ===")
print(transacciones_extremas.to_string(index=False))

# ============================================================
# CONCENTRACIÓN DE VENTAS POR PRODUCTO
# ============================================================

concentracion_productos = (
    df_productos[
        df_productos["Description"].isin(top5_productos)
    ]
    .groupby("Description")
    .agg(
        Cantidad_total=("Quantity", "sum"),
        Mayor_compra=("Quantity", "max"),
        Numero_facturas=("Invoice", "nunique")
    )
    .reset_index()
)

concentracion_productos["Porcentaje_mayor_compra"] = (
    concentracion_productos["Mayor_compra"]
    / concentracion_productos["Cantidad_total"]
    * 100
)

concentracion_productos = concentracion_productos.sort_values(
    "Porcentaje_mayor_compra",
    ascending=False
)

print("\n=== CONCENTRACIÓN DE VENTAS DE LOS PRODUCTOS TOP ===")
print(
    concentracion_productos.round(2).to_string(index=False)
)

# ============================================================
# EDA 4: ESTACIONALIDAD DE LAS VENTAS
# ============================================================

# Variables de tiempo
df_limpio["Anio"] = df_limpio["InvoiceDate"].dt.year
df_limpio["Mes_num"] = df_limpio["InvoiceDate"].dt.month
df_limpio["Mes_nombre"] = df_limpio["InvoiceDate"].dt.month_name()
df_limpio["Dia_semana"] = df_limpio["InvoiceDate"].dt.day_name()

# Ventas mensuales
ventas_mensuales = (
    df_limpio
    .groupby(["Anio", "Mes_num"])["TotalAmount"]
    .sum()
    .reset_index()
)

print("\n=== VENTAS MENSUALES ===")
print(
    ventas_mensuales
    .sort_values("TotalAmount", ascending=False)
    .head(10)
    .round(2)
    .to_string(index=False)
)


plt.figure(figsize=(12, 7))

for anio in ventas_mensuales["Anio"].unique():
    datos_anio = ventas_mensuales[
        ventas_mensuales["Anio"] == anio
    ]

    plt.plot(
        datos_anio["Mes_num"],
        datos_anio["TotalAmount"],
        marker="o",
        linewidth=2,
        label=str(anio)
    )

plt.title("Estacionalidad mensual de las ventas")
plt.xlabel("Mes")
plt.ylabel("Ventas totales (£)")

plt.xticks(
    range(1, 13),
    [
        "Ene", "Feb", "Mar", "Abr", "May", "Jun",
        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
    ]
)

plt.legend(title="Año")
plt.grid(alpha=0.25)
plt.tight_layout()

plt.savefig(
    "grafico_estacionalidad_mensual.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# EDA 5: MAPA DE CALOR DE ESTACIONALIDAD
# Año completo 2010
# ============================================================

df_2010 = df_limpio[
    df_limpio["InvoiceDate"].dt.year == 2010
].copy()

# Crear variables temporales
df_2010["Mes_num"] = df_2010["InvoiceDate"].dt.month
df_2010["Dia_num"] = df_2010["InvoiceDate"].dt.dayofweek

# Ventas por mes y día de la semana
ventas_heatmap = (
    df_2010
    .groupby(["Mes_num", "Dia_num"])["TotalAmount"]
    .sum()
    .unstack(fill_value=0)
)

print("\n=== VENTAS 2010 POR MES Y DÍA DE LA SEMANA ===")
print(ventas_heatmap.round(2))

# ============================================================
# GRÁFICA: HEATMAP MES X DÍA DE LA SEMANA
# ============================================================

plt.figure(figsize=(12, 7))

imagen = plt.imshow(
    ventas_heatmap,
    aspect="auto"
)

plt.colorbar(
    imagen,
    label="Ventas totales (£)"
)

plt.title(
    "Mapa de calor de ventas por mes y día de la semana - 2010"
)

plt.xlabel("Día de la semana")
plt.ylabel("Mes")

plt.xticks(
    range(7),
    [
        "Lun", "Mar", "Mié",
        "Jue", "Vie", "Sáb", "Dom"
    ]
)

plt.yticks(
    range(12),
    [
        "Ene", "Feb", "Mar", "Abr",
        "May", "Jun", "Jul", "Ago",
        "Sep", "Oct", "Nov", "Dic"
    ]
)

plt.tight_layout()

plt.savefig(
    "grafico_heatmap_estacionalidad_2010.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# PERIODOS DE MAYOR VENTA
# ============================================================

ventas_dia_semana = (
    df_2010
    .groupby("Dia_num")["TotalAmount"]
    .sum()
    .reset_index()
)

dias = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

ventas_dia_semana["Dia"] = (
    ventas_dia_semana["Dia_num"].map(dias)
)

ventas_dia_semana = ventas_dia_semana.sort_values(
    "TotalAmount",
    ascending=False
)

print("\n=== VENTAS POR DÍA DE LA SEMANA - 2010 ===")

print(
    ventas_dia_semana[
        ["Dia", "TotalAmount"]
    ]
    .round(2)
    .to_string(index=False)
)

# ============================================================
# PARTE 1: CLASIFICACIÓN DE CLIENTES
# PREPARAR BASE A NIVEL CLIENTE
# ============================================================

# Para analizar clientes necesitamos Customer ID válido
df_clientes_base = df_limpio.dropna(
    subset=["Customer ID"]
).copy()

print("\n=== BASE DE CLIENTES IDENTIFICADOS ===")
print("Registros utilizados:", len(df_clientes_base))
print(
    "Clientes únicos:",
    df_clientes_base["Customer ID"].nunique()
)
print(
    "Customer ID nulos:",
    df_clientes_base["Customer ID"].isna().sum()
)

# Fecha de referencia:
# un día después de la última compra registrada
fecha_referencia = (
    df_clientes_base["InvoiceDate"].max()
    + pd.Timedelta(days=1)
)

clientes = (
    df_clientes_base
    .groupby("Customer ID")
    .agg(
        Ultima_compra=("InvoiceDate", "max"),
        Frecuencia=("Invoice", "nunique"),
        Cantidad_total=("Quantity", "sum"),
        Gasto_total=("TotalAmount", "sum")
    )
    .reset_index()
)

# Recencia = días desde la última compra
clientes["Recencia"] = (
    fecha_referencia - clientes["Ultima_compra"]
).dt.days

print("\n=== BASE RESUMIDA POR CLIENTE ===")
print(clientes.head(10).to_string(index=False))


print("\n=== ESTADÍSTICAS DE CLIENTES ===")

print(
    clientes[
        [
            "Recencia",
            "Frecuencia",
            "Cantidad_total",
            "Gasto_total"
        ]
    ]
    .describe(
        percentiles=[
            0.25,
            0.50,
            0.75,
            0.80,
            0.90,
            0.95,
            0.99
        ]
    )
    .round(2)
)


# ============================================================
# DEFINICIÓN DE CLIENTES NORMAL Y PREMIUM
# ============================================================

# Percentil 80 del gasto total
umbral_premium = clientes["Gasto_total"].quantile(0.80)

print("\nUmbral para Cliente Premium:")
print(f"£{umbral_premium:,.2f}")

# Crear la categoría
clientes["Categoria"] = np.where(
    clientes["Gasto_total"] >= umbral_premium,
    "Premium",
    "Normal"
)

print("\n=== DISTRIBUCIÓN DE CLIENTES ===")

distribucion_clientes = (
    clientes["Categoria"]
    .value_counts()
    .reset_index()
)

distribucion_clientes.columns = [
    "Categoria",
    "Numero_clientes"
]

distribucion_clientes["Porcentaje"] = (
    distribucion_clientes["Numero_clientes"]
    / len(clientes)
    * 100
)

print(
    distribucion_clientes
    .round(2)
    .to_string(index=False)
)


# Comparar comportamiento de clientes Normal y Premium
comparacion_categoria = (
    clientes
    .groupby("Categoria")
    .agg(
        Clientes=("Customer ID", "count"),
        Recencia_media=("Recencia", "mean"),
        Frecuencia_media=("Frecuencia", "mean"),
        Cantidad_media=("Cantidad_total", "mean"),
        Gasto_medio=("Gasto_total", "mean")
    )
    .round(2)
)

print("\n=== PERFIL NORMAL VS PREMIUM ===")
print(comparacion_categoria)


clientes.to_csv(
    "data/clientes_clasificacion.csv",
    index=False
)

print("\nBase de clientes guardada correctamente.")