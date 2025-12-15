# 🦠 COVID-19 Data Explorer

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)

Una aplicación web interactiva desarrollada en Streamlit para explorar y analizar datos globales de la pandemia COVID-19, con énfasis en visualizaciones dinámicas y análisis de datos basado en evidencia.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)  
- [Uso](#-uso)
- [Secciones de la Aplicación](#-secciones-de-la-aplicación)
- [Fuente de Datos](#-fuente-de-datos)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Autor](#-autor)

## 🌟 Características

### Visualizaciones Interactivas
- **Mapas de calor globales** con múltiples métricas (casos, muertes, vacunación)
- **Gráficos animados** tipo "bar chart race" mostrando la evolución temporal
- **Comparaciones entre países** con filtros personalizables
- **Timeline interactivo** con eventos clave de la pandemia
- **Análisis socioeconómico** mediante scatter plots con regresión

### Análisis de Datos
- Datos de más de **200 países** desde enero 2020
- Actualización automática desde Our World in Data
- Métricas absolutas y normalizadas (per cápita, por millón)
- Promedios móviles de 7 días para suavizar tendencias
- Correlaciones entre variables socioeconómicas y vacunación

### Dashboard Analítico
- **Narrativa basada en datos** respondiendo preguntas clave sobre la pandemia
- Visualización de la evolución del COVID-19 por países
- Análisis del impacto de las vacunas en la mortalidad
- Estudio de desigualdades en el acceso a vacunación por nivel socioeconómico
- Seguimiento del progreso global de vacunación

### Características Técnicas
- Caché de datos para rendimiento óptimo
- Interfaz responsive y adaptable
- Filtros de fecha y selección múltiple
- Agregación temporal optimizada (semanal/mensual)
- Limpieza automática de datos agregados regionales

## 📁 Estructura del Proyecto

```
Visualization-Project/
│
├── README.md                    # Documentación del proyecto
├── requirements.txt             # Dependencias de Python
├── .gitignore                   # Archivos ignorados por Git
│
├── streamlit/                   # Aplicaciones Streamlit
│   ├── Covid_2.py              # Aplicación principal (versión completa)
│   └── covid_app.py            # Aplicación legacy (versión básica)
│
└── data/                        # Datos del proyecto
    └── owid-covid-data.csv     # Dataset COVID-19 (se descarga automáticamente)
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Conexión a internet (para descarga inicial de datos)

### Pasos de Instalación

1. **Clonar o descargar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd Visualization-Project
   ```

2. **Crear un entorno virtual** (recomendado)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verificar instalación**
   ```bash
   streamlit --version
   ```

## 💻 Uso

### Ejecución de la Aplicación Principal

1. **Navegar a la carpeta streamlit**
   ```bash
   cd streamlit
   ```

2. **Iniciar la aplicación**
   ```bash
   streamlit run Covid_2.py
   ```

3. **Acceder a la aplicación**
   - La aplicación se abrirá automáticamente en tu navegador
   - URL local: `http://localhost:8501`
   - URL de red: Se mostrará en la terminal para acceso desde otros dispositivos

4. **Detener la aplicación**
   - Presiona `Ctrl + C` en la terminal

### Alternativa: Versión Básica

Si deseas ejecutar la versión legacy (más simple):
```bash
cd streamlit
streamlit run covid_app.py
```

## 📊 Secciones de la Aplicación

### 1. 📊 Dashboard Global

Vista general de la pandemia con:
- Métricas globales (casos, muertes, vacunaciones, países afectados)
- Mapa de calor mundial interactivo con múltiples métricas
- Top 10 países por diferentes indicadores
- Evolución temporal de casos nuevos

**Uso recomendado**: Obtener una visión panorámica del impacto global de la pandemia.

### 2. 🌍 Comparación de Países

Análisis comparativo entre hasta 5 países simultáneamente:
- Selección flexible de países
- Múltiples métricas disponibles (casos, muertes, vacunación)
- Gráficos de serie temporal superpuestos
- Tabla de datos actuales comparativa

**Uso recomendado**: Comparar respuestas y resultados entre países específicos.

### 3. 📖 Historia de la Pandemia

Narrativa visual del desarrollo de la pandemia:
- **La Carrera de las Naciones**: Top 8 países animado mostrando cambios de epicentros
- **El Mapa del Contagio**: Mapa coroplético animado de propagación global
- **Hitos Decisivos**: Timeline con eventos clave (declaración de pandemia, primera vacuna, variantes)
- **Impacto Final**: Métricas globales acumuladas

**Uso recomendado**: Entender la progresión cronológica de la pandemia.

### 4. 📈 Dashboard Storytelling

Dashboard analítico respondiendo preguntas basadas en datos:

#### ¿Cómo fue la evolución del COVID?
- Bar chart race animado (Top 10 países)
- Selector de métrica (casos totales, muertes, casos per cápita)
- Análisis de cambios de epicentros y oleadas asimétricas

#### ¿Cómo afectó la vacuna al número de muertes?
- Timeline de mortalidad con hitos de vacunación
- Comparación pre/post vacunación
- Análisis de efectividad en el mundo real
- Evidencia cuantitativa del impacto

#### ¿Existe relación entre nivel socioeconómico y vacunación?
- Scatter plot: PIB per cápita / IDH vs. tasa de vacunación
- Línea de tendencia con coeficiente de correlación
- Tablas comparativas (países más y menos vacunados)
- Análisis de inequidad global

#### Progreso Global de Vacunación
- Evolución de dosis administradas globalmente
- Hitos de mil millones de dosis
- Métricas de la campaña global de inmunización

**Uso recomendado**: Análisis profundo basado en datos, storytelling, educación sobre la pandemia.

### 5. 🔍 Explorador de Datos

Interfaz para exploración detallada:
- Selección de país individual
- Estadísticas completas del país seleccionado
- Tabla de datos con filtros de fecha y columnas
- Descarga de datos en formato CSV
- Visualización de datos crudos

**Uso recomendado**: Análisis profundo de países específicos, extracción y descarga de datos.

## 📂 Fuente de Datos

### Our World in Data (OWID)

Los datos provienen del repositorio de [Our World in Data](https://ourworldindata.org/coronavirus), un proyecto de la Universidad de Oxford que recopila datos de múltiples fuentes oficiales:

- **Casos y muertes**: Johns Hopkins University, gobiernos nacionales
- **Vacunación**: Ministerios de salud nacionales, CDC, WHO
- **Variables socioeconómicas**: Banco Mundial, ONU, HDI

### Actualización de Datos

La aplicación descarga automáticamente la última versión del dataset en el primer uso. Para actualizar manualmente:

1. Elimina el archivo  `data/owid-covid-data.csv`
2. Reinicia la aplicación - descargará la versión más reciente

Alternativamente, descarga manual:
```bash
# Navegar a la carpeta data
cd data

# Descarga directa desde GitHub
curl -o owid-covid-data.csv https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv
```

### Estructura de Datos

El dataset incluye más de 60 columnas:
- **Identificación**: `date`, `location`, `iso_code`, `continent`
- **Casos y muertes**: `total_cases`, `new_cases`, `total_deaths`, `new_deaths`
- **Vacunación**: `total_vaccinations`, `people_vaccinated`, `people_fully_vaccinated`
- **Métricas normalizadas**: `*_per_million`, `*_per_hundred`
- **Socioeconómicas**: `population`, `gdp_per_capita`, `human_development_index`
- Y muchas más...

## 🛠 Tecnologías Utilizadas

### Core
- **[Python 3.8+](https://www.python.org/)**: Lenguaje de programación
- **[Streamlit](https://streamlit.io/)**: Framework de aplicaciones web interactivas
- **[Pandas](https://pandas.pydata.org/)**: Análisis y manipulación de datos

### Visualización
- **[Plotly](https://plotly.com/python/)**: Gráficos interactivos de alta calidad
- **[Plotly Express](https://plotly.com/python/plotly-express/)**: API de alto nivel para visualizaciones

## 👤 Autor

**David Moreda**, **Carlos Díaz**, **Pedro Martínez**

Proyecto desarrollado como parte del **Máster en Inteligencia Artificial** - Curso de Almacenamiento, Visualización y Procesamiento de Datos.

---

## 📚 Recursos Adicionales

### Enlaces Útiles

- [Our World in Data - COVID-19](https://ourworldindata.org/coronavirus)
- [Documentación de Streamlit](https://docs.streamlit.io/)
- [Plotly Python Graphing Library](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### Artículos de Referencia

- [COVID-19 Dashboard Development](https://towardsdatascience.com/)
- [Data Visualization Best Practices](https://www.storytellingwithdata.com/)
- [Interactive Dashboards with Streamlit](https://blog.streamlit.io/)

---

## 🙏 Agradecimientos

- **Our World in Data** por proporcionar datos abiertos, actualizados y de calidad
- **Streamlit** por el increíble framework de aplicaciones web
- **Comunidad de código abierto** por las herramientas y librerías utilizadas
- **Universidad de Oxford** por el trabajo de recopilación y validación de datos

---

<div align="center">

**Desarrollado con ❤️ y ☕**

*Análisis basado en datos • Visualización interactiva • Open Source*

</div>
