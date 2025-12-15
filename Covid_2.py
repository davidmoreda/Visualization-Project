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

@st.cache_data
def prepare_animation_data(df):
    """
    Prepara datos para animaciones con mayor frecuencia (semanal).
    Un compromiso entre fluidez (diario) y rendimiento.
    """
    # Filtrar solo países reales (no agregaciones)
    df_countries = df[df['is_aggregate'] == False].copy()
    
    # Rellenar datos faltantes hacia adelante para continuidad
    # Nota: groupby().ffill() elimina las columnas de agrupación, hay que restaurarlas
    df_sorted = df_countries.sort_values(['location', 'date'])
    df_countries = df_sorted.groupby('location').ffill()
    df_countries['location'] = df_sorted['location']
    df_countries['iso_code'] = df_sorted['iso_code']
    
    # Añadir columna para agrupación temporal (Semanal para fluidez sin colapsar)
    df_countries['period'] = df_countries['date'].dt.to_period('W')
    
    # Agrupar por país y periodo
    anim_data = df_countries.groupby(['location', 'iso_code', 'period']).agg({
        'total_cases': 'max',
        'total_deaths': 'max',
        'total_vaccinations': 'max',
        'total_cases_per_million': 'max',
        'new_cases_per_million': 'mean',
        'people_fully_vaccinated_per_hundred': 'max',
        'population': 'first'
    }).reset_index()
    
    # Convertir periodo de vuelta a datetime
    anim_data['date'] = anim_data['period'].dt.to_timestamp()
    
    # Rellenar NaNs con 0
    anim_data = anim_data.fillna(0)
    
    return anim_data

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
    # Para vacunación, usar datos recientes ya que en fechas tempranas no había vacunas
    if 'vaccin' in map_metric.lower():
        # Usar el dataset completo y tomar el último registro válido de cada país
        latest_data_map = df[df['is_aggregate'] == False].groupby('location').last().reset_index()
        # Filtrar solo países con datos de vacunación válidos
        latest_data_map = latest_data_map[latest_data_map[map_metric].notna()]
        st.info("📅 Mostrando datos de vacunación más recientes disponibles (independiente del filtro de fechas)")
    else:
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
        # Usar datos del dataset completo - último registro válido por país
        vax_data = df[df['is_aggregate'] == False].groupby('location').last().reset_index()
        # Filtrar solo países con datos de vacunación válidos
        vax_data = vax_data[vax_data['people_fully_vaccinated_per_hundred'].notna()]
        
        top_vax = vax_data.nlargest(10, 'people_fully_vaccinated_per_hundred')[['location', 'people_fully_vaccinated_per_hundred']]
        
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
# PÁGINA 3: HISTORIA DE LA PANDEMIA (NARRATIVA VISUAL)
# ============================================================
# ============================================================
# PÁGINA 3: HISTORIA DE LA NARRATIVA VISUAL)
# ============================================================
elif page == "📖 Historia de la Pandemia":
    st.header("🎥 La Historia de la Pandemia de COVID-19")
    st.markdown("""
    **Una historia visual del evento que cambió al mundo**
    
    Acomódate y observa cómo se desplegó la pandemia semana a semana. 
    Esta es la historia de cómo COVID-19 transformó nuestro planeta.
    """)
    
    # Preparar datos animados
    with st.spinner('Preparando visualizaciones (optimizadas)...'):
        anim_df = prepare_animation_data(df)
    
    st.markdown("---")
    
    # ============================================================
    # SECCIÓN 1: LA CARRERA DE LAS NACIONES (Bar Chart Race)
    # ============================================================
    with st.container():
        st.subheader("🏁 La Carrera de las Naciones")
        st.markdown("""
        Observa cómo los epicentros cambiaron con el tiempo. 
        **Mostrando Top 8 países por casos acumulados.**
        """)
        
        # Selector de métrica
        metric_race = st.selectbox(
            "Selecciona la métrica a visualizar",
            options=['total_cases', 'total_cases_per_million', 'people_fully_vaccinated_per_hundred', 'total_deaths'],
            format_func=lambda x: {
                'total_cases': 'Casos Totales',
                'total_cases_per_million': 'Casos por Millón de Habitantes',
                'people_fully_vaccinated_per_hundred': '% Población Totalmente Vacunada',
                'total_deaths': 'Muertes Totales'
            }[x],
            key='metric_race_selector'
        )
        
        # Títulos y formatos según métrica
        metric_info = {
            'total_cases': {'title': 'Casos Totales', 'format': '{:,.0f}'},
            'total_cases_per_million': {'title': 'Casos por Millón', 'format': '{:,.1f}'},
            'people_fully_vaccinated_per_hundred': {'title': '% Vacunación', 'format': '{:.1f}%'},
            'total_deaths': {'title': 'Muertes Totales', 'format': '{:,.0f}'}
        }
        
        # Preparar datos para bar chart race - Solo Top 8
        # Asegurar formato fecha string para consistencia en frames
        anim_df['date_str'] = anim_df['date'].dt.strftime('%Y-%m-%d')
        
        # Preparar datos por fecha
        dates_sorted = sorted(anim_df['date_str'].unique())
        
        # Crear figura base con el primer frame
        first_date = dates_sorted[0]
        first_data = anim_df[anim_df['date_str'] == first_date].nlargest(8, metric_race).sort_values(metric_race)
        first_max = first_data[metric_race].max()
        
        # Crear figura manualmente con go.Figure para control total
        fig_race = go.Figure()
        
        # Añadir el primer frame como datos iniciales
        fig_race.add_trace(go.Bar(
            x=first_data[metric_race],
            y=first_data['location'],
            orientation='h',
            marker=dict(
                color=first_data['location'].astype('category').cat.codes,
                colorscale='Viridis'
            ),
            text=first_data[metric_race].apply(lambda x: metric_info[metric_race]['format'].format(x)),
            textposition='outside'
        ))
        
        # Construir frames manualmente
        frames = []
        for date_str in dates_sorted:
            frame_data = anim_df[anim_df['date_str'] == date_str].nlargest(8, metric_race).sort_values(metric_race)
            frame_max = frame_data[metric_race].max()
            
            # Crear frame con layout específico para autoescale
            frame = go.Frame(
                data=[go.Bar(
                    x=frame_data[metric_race],
                    y=frame_data['location'],
                    orientation='h',
                    marker=dict(
                        color=frame_data['location'].astype('category').cat.codes,
                        colorscale='Viridis'
                    ),
                    text=frame_data[metric_race].apply(lambda x: metric_info[metric_race]['format'].format(x)),
                    textposition='outside'
                )],
                name=date_str,
                layout=go.Layout(
                    xaxis=dict(range=[0, frame_max * 1.15])
                )
            )
            frames.append(frame)
        
        fig_race.frames = frames
        
        # Configurar layout general
        fig_race.update_layout(
            title=f'Top 8 Países por {metric_info[metric_race]["title"]}',
            xaxis=dict(
                title=metric_info[metric_race]['title'],
                range=[0, first_max * 1.15]
            ),
            yaxis=dict(title=''),
            showlegend=False,
            height=500,
            bargap=0.1,
            margin=dict(l=150, r=50, t=50, b=50),
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': '▶ Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 400, 'redraw': True},  # Más lento: 400ms
                        'fromcurrent': True,
                        'transition': {'duration': 300, 'easing': 'linear'}  # Transición suave
                    }]
                }, {
                    'label': '⏸ Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                }],
                'x': 0.1,
                'y': -0.05,
                'xanchor': 'left',
                'yanchor': 'top'
            }],
            sliders=[{
                'active': 0,
                'steps': [{
                    'args': [[f.name], {
                        'frame': {'duration': 0, 'redraw': True},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }],
                    'label': f.name,
                    'method': 'animate'
                } for f in frames],
                'x': 0.1,
                'len': 0.9,
                'y': -0.15,
                'xanchor': 'left',
                'yanchor': 'top'
            }]
        )
        
        st.plotly_chart(fig_race, use_container_width=True)
    
    st.markdown("---")
    
    # ============================================================
    # SECCIÓN 2: EL MAPA DEL CONTAGIO (Animated Choropleth)
    # ============================================================
    with st.container():
        st.subheader("🌍 El Mapa del Contagio")
        st.markdown("""
        **Evolución geográfica de la pandemia.**
        """)
        
        # Crear mapa animado
        fig_map_animated = px.choropleth(
            anim_df,
            locations='iso_code',
            color='total_cases',
            hover_name='location',
            animation_frame='date',
            color_continuous_scale='Reds',
            range_color=[1, anim_df['total_cases'].max()],
            labels={'total_cases': 'Casos Totales'},
            title='Propagación Global de COVID-19',
            height=600
        )
        
        fig_map_animated.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth'
            )
        )
        
        fig_map_animated.update_traces(
            colorbar=dict(title='Casos<br>Totales'),
            zmin=0,
            colorscale='Reds'
        )
        
        # Configurar velocidad
        fig_map_animated.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 150
        
        st.plotly_chart(fig_map_animated, use_container_width=True)
    
    st.markdown("---")
    
    # ============================================================
    # SECCIÓN 3: HITOS DECISIVOS (Timeline Interactivo)
    # ============================================================
    with st.container():
        st.subheader("📍 Hitos Decisivos: Cronología Interactiva")
        st.markdown("Explora los hitos comparando el mundo con países específicos.")
        
        col_filtro1, col_filtro2 = st.columns(2)
        
        # Preparar lista de países incluyendo 'World'
        all_locs = ['World'] + sorted(df[df['is_aggregate'] == False]['location'].unique().tolist())
        
        with col_filtro1:
            sel_locations = st.multiselect(
                "Selecciona Ubicaciones",
                options=all_locs,
                default=['World', 'United States', 'China'],
                max_selections=5
            )
            
        with col_filtro2:
            sel_metric_time = st.selectbox(
                "Métrica",
                ['new_cases_smoothed', 'new_deaths_smoothed', 'people_fully_vaccinated_per_hundred'],
                format_func=lambda x: {
                    'new_cases_smoothed': 'Casos Nuevos Diarios',
                    'new_deaths_smoothed': 'Muertes Nuevas Diarias',
                    'people_fully_vaccinated_per_hundred': '% Vacunación'
                }[x]
            )
        
        # Crear gráfico dinámico
        timeline_df = df[df['location'].isin(sel_locations)]
        
        fig_timeline = px.line(
            timeline_df,
            x='date',
            y=sel_metric_time,
            color='location',
            title='Cronología Interactiva',
            labels={'date': 'Fecha', sel_metric_time: 'Valor'}
        )
        
        # Eventos fijos
        key_events = [
            ('2020-03-11', 'Pandemia', 'red'),
            ('2020-12-08', 'Vacuna', 'green'),
            ('2021-11-26', 'Ómicron', 'orange'),
            ('2023-05-05', 'Fin', 'blue')
        ]
        
        for date, txt, color in key_events:
            fig_timeline.add_vline(x=date, line_dash="dash", line_color=color, opacity=0.5)
            # Solo añadir anotación si está en rango
            fig_timeline.add_annotation(
                x=date, y=0, text=txt, showarrow=False, yref='paper', yanchor='bottom',
                font=dict(color=color)
            )
            
        fig_timeline.update_layout(height=500, hovermode='x unified')
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("---")
    
    # ============================================================
    # RESUMEN FINAL: MÉTRICAS BIG NUMBER
    # ============================================================
    with st.container():
        st.subheader("📊 El Impacto Final")
        
        # Calcular métricas globales finales obteniendo maximos de acumulados
        # Esto evita NaNs si el último día no tiene reporte
        world_df = df[df['location'] == 'World']
        
        # Usar el máximo valor histórico para métricas acumuladas
        total_c = world_df['total_cases'].max()
        total_d = world_df['total_deaths'].max()
        total_v = world_df['total_vaccinations'].max()
        total_p = world_df['people_fully_vaccinated_per_hundred'].max()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌍 Casos Totales", f"{total_c:,.0f}" if pd.notna(total_c) else "N/A")
        
        with col2:
            st.metric("💔 Muertes Totales", f"{total_d:,.0f}" if pd.notna(total_d) else "N/A")
        
        with col3:
            st.metric("💉 Vacunas", f"{total_v:,.0f}" if pd.notna(total_v) else "N/A")
        
        with col4:
            st.metric("🛡️ % Vacunado", f"{total_p:.1f}%" if pd.notna(total_p) else "N/A")
        
        st.markdown("""
        ---
        **"Los datos cuentan la historia, pero las personas vivieron la realidad."**
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
