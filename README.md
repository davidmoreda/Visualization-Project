# 🦠 COVID-19 Data Explorer

Aplicación interactiva en Streamlit para explorar datos de la pandemia de COVID-19.

## 🚀 Características

- **Dashboard Global**: Métricas principales y visualizaciones de tendencias mundiales
- **Comparación de Países**: Compara hasta 5 países simultáneamente
- **Historia de la Pandemia**: Narrativa visual de los eventos más importantes
- **Explorador de Datos**: Accede y descarga datos específicos en formato CSV

## 📦 Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

Para ejecutar la aplicación:

```bash
streamlit run covid_app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📊 Datos

Los datos provienen de [Our World in Data](https://ourworldindata.org/coronavirus), una fuente confiable y actualizada regularmente.

La aplicación descargará automáticamente los datos la primera vez que se ejecute y los guardará localmente para cargas más rápidas.

## 🎨 Funcionalidades

### Dashboard Global
- Métricas principales (casos, muertes, vacunaciones)
- Top 10 países por casos y vacunación
- Gráficos de evolución temporal

### Comparación de Países
- Selecciona múltiples países
- Diferentes métricas disponibles
- Gráficos interactivos con Plotly

### Historia de la Pandemia
- Narrativa visual de la pandemia
- Eventos importantes marcados
- Análisis de las diferentes olas

### Explorador de Datos
- Estadísticas detalladas por país
- Tabla personalizable de datos
- Descarga de datos en CSV

## 🛠️ Tecnologías

- **Streamlit** (última versión): Framework de aplicaciones web
- **Pandas**: Procesamiento de datos
- **Plotly**: Visualizaciones interactivas

## 📝 Notas

- La primera carga puede tardar unos minutos mientras se descargan los datos
- Los datos se actualizan periódicamente en la fuente original
- La aplicación usa caché para mejorar el rendimiento
