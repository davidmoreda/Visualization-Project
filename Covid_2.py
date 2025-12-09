import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="COVID-19 Explorer",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# LIMPIEZA DE GRUPOS DE PAÍSES
# ============================================================
def clean_country_groups(df):
    """
    Limpia el dataset eliminando agregaciones regionales y grupos.
    Solo mantiene países individuales (excluye códigos OWID_* excepto World para algunas visualizaciones).
    """
    # Filtrar filas donde iso_code NO contiene 'OWID' (excepto mantendremos 'World' según necesidad)
    # Los códigos OWID representan agregaciones como continentes, grupos de ingresos, etc.
    df_clean = df.copy()
    
    # Lista de códigos a excluir (agregaciones regionales y grupos)
    exclude_codes = [
        'OWID_AFR',  # África
        'OWID_ASI',  # Asia
        'OWID_EUR',  # Europa
        'OWID_EUN',  # Unión Europea
        'OWID_INT',  # Internacional
        'OWID_NAM',  # Norteamérica
        'OWID_OCE',  # Oceanía
        'OWID_SAM',  # Sudamérica
        'OWID_WRL',  # World (lo manejaremos por separado)
        'OWID_HIC',  # Países de ingresos altos
        'OWID_LIC',  # Países de ingresos bajos
        'OWID_LMC',  # Países de ingresos medios-bajos
        'OWID_UMC',  # Países de ingresos medios-altos
    ]
    
    # Marcar filas que contengan códigos OWID (son agregaciones)
    df_clean['is_aggregate'] = df_clean['iso_code'].str.contains('OWID', na=False)
    
    return df_clean

@st.cache_data
def load_data():
    """Carga los datos de COVID-19 con caché para mejor rendimiento"""
    url = "owid-covid-data.csv"
    
    # Intentar cargar archivo local, si no existe, descargarlo
    if os.path.exists(url):
        df = pd.read_csv(url)
    else:
        url_online = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
        df = pd.read_csv(url_online)
        df.to_csv("owid-covid-data.csv", index=False)
    
    df['date'] = pd.to_datetime(df['date'])
    
    # Limpiar grupos de países
    df = clean_country_groups(df)
    
    return df

# Cargar datos
with st.spinner('Cargando datos de COVID-19...'):
    df = load_data()

# Header principal
st.markdown('<p class="main-header">🦠 COVID-19 Data Explorer</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Explora la historia global de la pandemia a través de datos</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Configuración")
st.sidebar.markdown("---")

# Navegación
page = st.sidebar.radio(
    "Navegar",
    ["📊 Dashboard Global", "🌍 Comparación de Países", "📖 Historia de la Pandemia", "🔍 Explorador de Datos"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Sobre esta app:**
Aplicación interactiva para explorar datos de COVID-19 utilizando información de Our World in Data.
""")

# ============================================================
# PÁGINA 1: DASHBOARD GLOBAL
# ============================================================
if page == "📊 Dashboard Global":
    st.header("📊 Dashboard Global")
    
    # Filtro de fecha
    # Reducir la cota superior por defecto en 20 días
    default_max_date = df['date'].max() - pd.Timedelta(days=20)
    date_range = st.slider(
        "Selecciona el rango de fechas",
        min_value=df['date'].min().to_pydatetime(),
        max_value=df['date'].max().to_pydatetime(),
        value=(df['date'].min().to_pydatetime(), default_max_date.to_pydatetime()),
        format="DD/MM/YYYY"
    )
    
    # Filtrar datos por fecha
    mask = (df['date'] >= pd.Timestamp(date_range[0])) & (df['date'] <= pd.Timestamp(date_range[1]))
    df_filtered = df[mask]
    
    # Métricas globales
    st.subheader("📈 Métricas Globales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcular totales excluyendo agregaciones (usando la nueva columna is_aggregate)
    countries_only = df_filtered[df_filtered['is_aggregate'] == False]
    
    with col1:
        total_cases = countries_only['total_cases'].sum()
        st.metric("Casos Totales", f"{total_cases:,.0f}")
    
    with col2:
        total_deaths = countries_only['total_deaths'].sum()
        st.metric("Muertes Totales", f"{total_deaths:,.0f}")
    
    with col3:
        total_vaccinations = countries_only['total_vaccinations'].sum()
        st.metric("Vacunas Aplicadas", f"{total_vaccinations:,.0f}")
    
    with col4:
        countries = countries_only['location'].nunique()
        st.metric("Países Afectados", f"{countries}")
    
    st.markdown("---")
    
    # Mapa de calor mundial
    st.subheader("🌍 Mapa Mundial de Calor")
    
    # Selector de variable para el mapa
    map_metric = st.selectbox(
        "Selecciona la variable a visualizar en el mapa",
        options=[
            'total_cases_per_million',
            'total_deaths_per_million',
            'people_fully_vaccinated_per_hundred',
            'total_cases',
            'total_deaths',
            'total_vaccinations',
            'new_cases_smoothed_per_million',
            'new_deaths_smoothed_per_million'
        ],
        format_func=lambda x: {
            'total_cases_per_million': 'Casos Totales por Millón',
            'total_deaths_per_million': 'Muertes Totales por Millón',
            'people_fully_vaccinated_per_hundred': 'Población Totalmente Vacunada (%)',
            'total_cases': 'Casos Totales',
            'total_deaths': 'Muertes Totales',
            'total_vaccinations': 'Vacunaciones Totales',
            'new_cases_smoothed_per_million': 'Casos Nuevos por Millón (7 días)',
            'new_deaths_smoothed_per_million': 'Muertes Nuevas por Millón (7 días)'
        }[x]
    )
    
    # Crear el mapa de calor
    latest_data_map = df_filtered[
        (df_filtered['date'] == df_filtered['date'].max()) & 
        (df_filtered['is_aggregate'] == False)
    ]
    
    # Nombres de métricas para labels
    metric_labels = {
        'total_cases_per_million': 'Casos por Millón',
        'total_deaths_per_million': 'Muertes por Millón',
        'people_fully_vaccinated_per_hundred': '% Vacunación',
        'total_cases': 'Casos Totales',
        'total_deaths': 'Muertes Totales',
        'total_vaccinations': 'Vacunaciones Totales',
        'new_cases_smoothed_per_million': 'Casos Nuevos por Millón',
        'new_deaths_smoothed_per_million': 'Muertes Nuevas por Millón'
    }
    
    # Seleccionar escala de colores apropiada
    color_scales = {
        'total_cases_per_million': 'Reds',
        'total_deaths_per_million': 'Reds',
        'people_fully_vaccinated_per_hundred': 'Greens',
        'total_cases': 'Oranges',
        'total_deaths': 'Reds',
        'total_vaccinations': 'Blues',
        'new_cases_smoothed_per_million': 'YlOrRd',
        'new_deaths_smoothed_per_million': 'Reds'
    }
    
    fig_map = px.choropleth(
        latest_data_map,
        locations='iso_code',
        color=map_metric,
        hover_name='location',
        hover_data={
            'iso_code': False,
            map_metric: ':,.0f' if 'per' not in map_metric else ':,.1f',
            'total_cases': ':,.0f',
            'total_deaths': ':,.0f'
        },
        color_continuous_scale=color_scales[map_metric],
        labels={
            map_metric: metric_labels[map_metric],
            'total_cases': 'Casos Totales',
            'total_deaths': 'Muertes Totales'
        },
        title=f'Distribución Mundial: {metric_labels[map_metric]}'
    )
    
    fig_map.update_layout(
        height=600,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        )
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown("---")
    
    # Top 10 países
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Países por Casos por Millón")
        latest_data = countries_only[countries_only['date'] == countries_only['date'].max()]
        top_cases = latest_data.nlargest(10, 'total_cases_per_million')[['location', 'total_cases_per_million']]
        
        fig = px.bar(
            top_cases, 
            x='total_cases_per_million', 
            y='location',
            orientation='h',
            labels={'total_cases_per_million': 'Casos por Millón', 'location': 'País'},
            color='total_cases_per_million',
            color_continuous_scale='Reds'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💉 Top 10 Países por Vacunación (% Población)")
        top_vax = latest_data.nlargest(10, 'people_fully_vaccinated_per_hundred')[['location', 'people_fully_vaccinated_per_hundred']]
        
        fig = px.bar(
            top_vax, 
            x='people_fully_vaccinated_per_hundred', 
            y='location',
            orientation='h',
            labels={'people_fully_vaccinated_per_hundred': '% Población Vacunada', 'location': 'País'},
            color='people_fully_vaccinated_per_hundred',
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Evolución temporal global
    st.subheader("📉 Evolución Temporal de Casos Nuevos")
    
    world_data = df_filtered[df_filtered['location'] == 'World']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=world_data['date'], 
        y=world_data['new_cases_smoothed'],
        fill='tozeroy',
        name='Casos Nuevos (promedio 7 días)',
        line=dict(color='#1f77b4')
    ))
    
    fig.update_layout(
        title='Casos Nuevos Diarios a Nivel Mundial',
        xaxis_title='Fecha',
        yaxis_title='Casos Nuevos',
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PÁGINA 2: COMPARACIÓN DE PAÍSES
# ============================================================
elif page == "🌍 Comparación de Países":
    st.header("🌍 Comparación entre Países")
    
    # Selector de países
    available_countries = sorted(df[df['is_aggregate'] == False]['location'].unique())
    
    selected_countries = st.multiselect(
        "Selecciona países para comparar (máximo 5)",
        options=available_countries,
        default=['Spain', 'Italy', 'Germany', 'France'],
        max_selections=5
    )
    
    if selected_countries:
        # Selector de métrica
        metric = st.selectbox(
            "Selecciona métrica",
            ['new_cases_smoothed', 'new_deaths_smoothed', 'total_cases', 'total_deaths', 
             'total_vaccinations', 'people_fully_vaccinated_per_hundred']
        )
        
        metric_names = {
            'new_cases_smoothed': 'Casos Nuevos (promedio 7 días)',
            'new_deaths_smoothed': 'Muertes Nuevas (promedio 7 días)',
            'total_cases': 'Casos Totales',
            'total_deaths': 'Muertes Totales',
            'total_vaccinations': 'Vacunas Totales',
            'people_fully_vaccinated_per_hundred': 'Población Totalmente Vacunada (%)'
        }
        
        # Filtrar datos
        df_comparison = df[df['location'].isin(selected_countries)]
        
        # Gráfico de comparación
        fig = px.line(
            df_comparison,
            x='date',
            y=metric,
            color='location',
            title=f'Comparación: {metric_names[metric]}',
            labels={'date': 'Fecha', metric: metric_names[metric], 'location': 'País'}
        )
        
        fig.update_layout(
            hovermode='x unified',
            height=600,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla comparativa
        st.subheader("📋 Datos Actuales")
        
        latest_comparison = df_comparison[df_comparison['date'] == df_comparison['date'].max()]
        comparison_table = latest_comparison[[
            'location', 'total_cases', 'total_deaths', 'total_vaccinations',
            'people_fully_vaccinated_per_hundred'
        ]].copy()
        
        comparison_table.columns = ['País', 'Casos Totales', 'Muertes Totales', 
                                   'Vacunas Totales', '% Población Vacunada']
        
        st.dataframe(comparison_table, use_container_width=True, hide_index=True)
    else:
        st.warning("Por favor, selecciona al menos un país para comparar")

# ============================================================
# PÁGINA 3: HISTORIA DE LA PANDEMIA
# ============================================================
elif page == "📖 Historia de la Pandemia":
    st.header("📖 La Historia de la Pandemia de COVID-19")
    
    st.markdown("""
    ### 🌍 El Comienzo (Diciembre 2019 - Marzo 2020)
    
    En diciembre de 2019, los primeros casos de una misteriosa neumonía fueron reportados en Wuhan, China. 
    Lo que comenzó como un brote local rápidamente se convirtió en una pandemia global.
    """)
    
    # Visualización del inicio
    world_data = df[df['location'] == 'World']
    early_data = world_data[world_data['date'] < '2020-06-01']
    
    fig = px.area(
        early_data,
        x='date',
        y='new_cases_smoothed',
        title='Los Primeros Meses: Propagación Inicial',
        labels={'date': 'Fecha', 'new_cases_smoothed': 'Casos Nuevos Diarios'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### 📊 Las Olas de la Pandemia
    
    La pandemia no fue uniforme: vino en oleadas, cada una con sus características únicas.
    Cada ola reflejó diferentes variantes del virus, medidas de contención y temporadas del año.
    """)
    
    # Marcar las olas principales
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=world_data['date'],
        y=world_data['new_cases_smoothed'],
        fill='tozeroy',
        name='Casos Nuevos'
    ))
    
    # Añadir anotaciones para eventos importantes
    events = [
        ('2020-03-11', 'OMS declara\npandemia', world_data[world_data['date'] == '2020-03-11']['new_cases_smoothed'].values[0] if len(world_data[world_data['date'] == '2020-03-11']) > 0 else 0),
        ('2020-12-08', 'Primera vacuna\naprobada', world_data[world_data['date'] == '2020-12-08']['new_cases_smoothed'].values[0] if len(world_data[world_data['date'] == '2020-12-08']) > 0 else 0),
        ('2021-11-26', 'Variante\nÓmicron', world_data[world_data['date'] == '2021-11-26']['new_cases_smoothed'].values[0] if len(world_data[world_data['date'] == '2021-11-26']) > 0 else 0),
    ]
    
    for date, text, y in events:
        fig.add_vline(x=date, line_dash="dash", line_color="red", opacity=0.5)
        fig.add_annotation(x=date, y=y, text=text, showarrow=True)
    
    fig.update_layout(
        title='Las Diferentes Olas de COVID-19',
        xaxis_title='Fecha',
        yaxis_title='Casos Nuevos Diarios',
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### 💉 La Era de las Vacunas
    
    El desarrollo de vacunas en tiempo récord fue un hito científico sin precedentes.
    A finales de 2020, comenzó la mayor campaña de vacunación de la historia.
    """)
    
    # Gráfico de vacunación
    vax_data = world_data[world_data['date'] >= '2020-12-01']
    
    fig = px.area(
        vax_data,
        x='date',
        y='people_fully_vaccinated_per_hundred',
        title='Progreso de la Vacunación Mundial',
        labels={'date': 'Fecha', 'people_fully_vaccinated_per_hundred': '% Población Vacunada'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 Lecciones Aprendidas y el Futuro
    
    La pandemia de COVID-19 transformó al mundo de maneras que aún estamos comprendiendo:
    
    - **Ciencia acelerada**: El desarrollo de vacunas de ARNm en menos de un año.
    - **Transformación digital**: Trabajo remoto, telemedicina y educación online.
    - **Desigualdad global**: Las diferencias en el acceso a vacunas entre países.
    - **Preparación futura**: Nuevos sistemas de vigilancia y respuesta epidemiológica.
    
    Aunque la fase aguda de la pandemia ha quedado atrás, sus efectos perdurarán por generaciones.
    """)

# ============================================================
# PÁGINA 4: EXPLORADOR DE DATOS
# ============================================================
elif page == "🔍 Explorador de Datos":
    st.header("🔍 Explorador de Datos")
    
    st.markdown("""
    Explora los datos crudos y crea tus propias visualizaciones.
    """)
    
    # Selector de país
    country = st.selectbox(
        "Selecciona un país",
        options=sorted(df[df['is_aggregate'] == False]['location'].unique())
    )
    
    if country:
        df_country = df[df['location'] == country]
        
        # Mostrar estadísticas básicas
        st.subheader(f"📊 Estadísticas de {country}")
        
        col1, col2, col3 = st.columns(3)
        
        latest = df_country[df_country['date'] == df_country['date'].max()].iloc[0]
        
        with col1:
            st.metric(
                "Casos Totales",
                f"{latest['total_cases']:,.0f}" if pd.notna(latest['total_cases']) else "N/A"
            )
            st.metric(
                "Muertes Totales",
                f"{latest['total_deaths']:,.0f}" if pd.notna(latest['total_deaths']) else "N/A"
            )
        
        with col2:
            st.metric(
                "Vacunas Aplicadas",
                f"{latest['total_vaccinations']:,.0f}" if pd.notna(latest['total_vaccinations']) else "N/A"
            )
            st.metric(
                "% Población Vacunada",
                f"{latest['people_fully_vaccinated_per_hundred']:.1f}%" if pd.notna(latest['people_fully_vaccinated_per_hundred']) else "N/A"
            )
        
        with col3:
            st.metric(
                "Casos por Millón",
                f"{latest['total_cases_per_million']:,.0f}" if pd.notna(latest['total_cases_per_million']) else "N/A"
            )
            st.metric(
                "Muertes por Millón",
                f"{latest['total_deaths_per_million']:,.0f}" if pd.notna(latest['total_deaths_per_million']) else "N/A"
            )
        
        st.markdown("---")
        
        # Tabla de datos
        st.subheader("📋 Datos Detallados")
        
        # Seleccionar columnas para mostrar
        all_columns = df_country.columns.tolist()
        selected_columns = st.multiselect(
            "Selecciona columnas para visualizar",
            options=all_columns,
            default=['date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths']
        )
        
        if selected_columns:
            # Filtro de fecha para la tabla
            date_filter = st.date_input(
                "Rango de fechas",
                value=(df_country['date'].min(), df_country['date'].max()),
                min_value=df_country['date'].min().to_pydatetime(),
                max_value=df_country['date'].max().to_pydatetime()
            )
            
            df_display = df_country[
                (df_country['date'] >= pd.Timestamp(date_filter[0])) & 
                (df_country['date'] <= pd.Timestamp(date_filter[1]))
            ][selected_columns]
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Botón de descarga
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar datos como CSV",
                data=csv,
                file_name=f'covid_data_{country}_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>Datos proporcionados por <a href='https://ourworldindata.org/coronavirus' target='_blank'>Our World in Data</a></p>
    <p>Última actualización: {}</p>
</div>
""".format(df['date'].max().strftime('%d/%m/%Y')), unsafe_allow_html=True)
