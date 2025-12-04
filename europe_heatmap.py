import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuración
url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
nombre_archivo_local = "owid-covid-data.csv"

# Países europeos con sus códigos ISO
paises_europa = [
    'Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina',
    'Bulgaria', 'Croatia', 'Cyprus', 'Czechia', 'Denmark', 'Estonia', 'Finland',
    'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy',
    'Kosovo', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Monaco',
    'Montenegro', 'Netherlands', 'North Macedonia', 'Norway', 'Poland', 'Portugal',
    'Romania', 'Russia', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain',
    'Sweden', 'Switzerland', 'Ukraine', 'United Kingdom', 'Vatican'
]

# --- LÓGICA DE CACHÉ ---
if os.path.exists(nombre_archivo_local):
    print(f"✅ Archivo local '{nombre_archivo_local}' encontrado. Cargando...")
    df = pd.read_csv(nombre_archivo_local)
else:
    print(f"⚠️ Descargando datos de internet (puede tardar)...")
    df = pd.read_csv(url)
    print("💾 Guardando copia local...")
    df.to_csv(nombre_archivo_local, index=False)

# Convertir fecha
df['date'] = pd.to_datetime(df['date'])

# Filtrar solo países europeos
df_europa = df[df['location'].isin(paises_europa)].copy()

# Eliminar filas sin datos de casos
df_europa = df_europa[df_europa['total_cases'].notna()]

print(f"Datos procesados. Rango de fechas: {df_europa['date'].min()} a {df_europa['date'].max()}")

# Crear mapa de calor con slider temporal
fig = px.choropleth(
    df_europa,
    locations='iso_code',
    color='total_cases',
    hover_name='location',
    hover_data={
        'total_cases': ':,.0f',
        'new_cases': ':,.0f',
        'iso_code': False
    },
    animation_frame=df_europa['date'].dt.strftime('%Y-%m-%d'),
    color_continuous_scale='YlOrRd',
    labels={'total_cases': 'Casos totales'},
    title='Casos de COVID-19 en Europa (Mapa de calor interactivo)',
    scope='europe'
)

# Ajustar diseño
fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth'
    ),
    height=700,
    font=dict(size=14)
)

# Configurar animación más lenta
fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 200
fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 100

# Mostrar
print("🗺️ Generando mapa interactivo...")
fig.show()

print("""
✅ Mapa generado con éxito!

📌 Cómo usar:
- Usa el slider inferior para moverte por las fechas
- Haz clic en 'Play' para ver la animación temporal
- Pasa el ratón sobre cada país para ver detalles
- Usa los zoom y drag controls para navegar

💡 Los colores más intensos indican mayor número de casos
""")
