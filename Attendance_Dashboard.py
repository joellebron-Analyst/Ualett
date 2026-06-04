import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Attendance",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def cargar_datos():
    return pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSL8e5uoUExt5a-LDPCw0rEcFTm0SqAhLz8sYT8sbkYtse1pvMHY9Qij547diNhlP__DYxtuT8XojRO/pub?gid=1596580014&single=true&output=csv')

historic = cargar_datos()
historic['datestamp'] = pd.to_datetime(historic['datestamp'])

nombre_meses = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# ── SIDEBAR ──────────────────────────────
st.sidebar.title('Filtros')

año_seleccionado = st.sidebar.selectbox(
    'Año:', sorted(historic['datestamp'].dt.year.unique()))

meses_disponibles = sorted(historic[
    historic['datestamp'].dt.year == año_seleccionado
]['datestamp'].dt.month.unique())

mes_seleccionado = st.sidebar.selectbox(
    'Mes:', meses_disponibles,
    format_func=lambda x: nombre_meses[x])

lob_seleccionado = st.sidebar.selectbox(
    'LOB:', historic.loc[
        (historic['datestamp'].dt.year == año_seleccionado) &
        (historic['datestamp'].dt.month == mes_seleccionado) &
        (historic['Status'] == 'Late'), 'LOB'
    ].dropna().unique())

nombre = st.sidebar.selectbox(
    'Nombre:', historic.loc[
        (historic['datestamp'].dt.year == año_seleccionado) &
        (historic['datestamp'].dt.month == mes_seleccionado) &
        (historic['LOB'] == lob_seleccionado) &
        (historic['Status'] == 'Late'), 'Full Name'
    ].unique())

# ── HEADER ───────────────────────────────
st.markdown('# Attendance Dashboard')
st.markdown(f'### {nombre} — {nombre_meses[mes_seleccionado]} {año_seleccionado}')

# ── METRICAS ─────────────────────────────
resultado = historic.loc[
    (historic['LOB'] == lob_seleccionado) &
    (historic['datestamp'].dt.year == año_seleccionado) &
    (historic['datestamp'].dt.month == mes_seleccionado) &
    (historic['Full Name'] == nombre) &
    (historic['Status'] == 'Late'),
    ['datestamp', 'Full Name', 'LOB', 'Schedule In', 'Schedule Out', 
     'Clock in time', 'Clock out time', 'Status']
]

col1, col2, col3 = st.columns(3)
col1.metric('Total Tardanzas', len(resultado))
col2.metric('LOB', lob_seleccionado)
col3.metric('Mes', nombre_meses[mes_seleccionado])

# ── TABLA ────────────────────────────────
resultado['datestamp'] = resultado['datestamp'].dt.strftime('%m/%d/%Y')
resultado = resultado.rename(columns={
    'datestamp': 'Fecha',
    'Full Name': 'Nombre',
    'Schedule In': 'Entrada Programada',
    'Schedule Out': 'Salida Programada',
    'Clock in time': 'Entrada Real',
    'Clock out time': 'Salida Real'
})

st.dataframe(resultado, hide_index=True, use_container_width=True)
