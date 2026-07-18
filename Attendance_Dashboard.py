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

historic = historic.loc[
historic['datestamp'].dt.year >= 2026
]

nombre_meses = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}
# ── SIDEBAR ──────────────────────────────
st.sidebar.title('Filtros')



fecha_min = historic['datestamp'].min().date()
fecha_max = historic['datestamp'].max().date()

rango_fechas = st.sidebar.date_input(
        'Fecha', value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        format="MM/DD/YYYY"
)

if len(rango_fechas) != 2:
    st.stop()

fecha_inicio, fecha_fin = rango_fechas
fecha_inicio = pd.Timestamp(fecha_inicio)
fecha_fin = pd.Timestamp(fecha_fin)


lob_disponibles = historic.loc[
        (historic['datestamp']>= fecha_inicio)
         &
        (historic['datestamp'] <= fecha_fin) , 'LOB'
    ].dropna().unique()

lob_seleccionado = st.sidebar.multiselect(
                                        'LOB',
                                        options=lob_disponibles,
                                        default =lob_disponibles
)

status_disponibles = historic.loc[
        (historic['datestamp']>= fecha_inicio)
         &
        (historic['datestamp'] <= fecha_fin)
        , 'Status'
    ].dropna().unique()

status_seleccionado = st.sidebar.multiselect('Status:',
                                           options = status_disponibles,
                                             default = status_disponibles
                                            )


nombres_disponibles = historic.loc[
        (historic['datestamp']>= fecha_inicio)
         &
        (historic['datestamp'] <= fecha_fin) &
        (historic['LOB'].isin(lob_seleccionado))  &
        (historic['Status'].isin(status_seleccionado)), 'Full Name'
    ].dropna().unique()

nombres_seleccionados = st.sidebar.multiselect(
    'Nombre:',
    options=nombres_disponibles,
    default= []  # ninguno seleccionado por defecto
)
# Si no selecciona ninguno → muestra todos
if not nombres_seleccionados:
    nombres_seleccionados = nombres_disponibles
# ── HEADER ───────────────────────────────
st.markdown('# 🚶‍♀️‍➡️🏢 Attendance Dashboard')
st.markdown('## General View')

resultado = historic.loc[
    (historic['LOB'].isin(lob_seleccionado)) &
    (historic['datestamp']>= fecha_inicio)
         &
        (historic['datestamp'] <= fecha_fin)&
    (historic['Full Name'].isin (nombres_seleccionados))  &
        (historic['Status'].isin(status_seleccionado)),
    ['datestamp', 'Full Name', 'LOB', 'Status', 'Schedule In', 'Schedule Out',
     'Clock in time', 'Clock out time', 'Total work time']
]

resultado['datestamp'] = resultado['datestamp'].dt.strftime('%m/%d/%Y')
resultado = resultado.rename(columns={
    'datestamp': 'Fecha',
    'Full Name': 'Nombre',
    'Schedule In': 'Entrada Programada',
    'Schedule Out': 'Salida Programada',
    'Clock in time': 'Entrada Real',
    'Clock out time': 'Salida Real',
    'Total work time' : 'Horas Trabajadas'
})
st.dataframe(resultado, hide_index=True, use_container_width=True)

