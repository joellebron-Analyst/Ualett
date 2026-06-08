import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Attendance",
    layout="wide",
    initial_sidebar_state="expanded")

@st.cache_data
def cargar_datos():
    return pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSL8e5uoUExt5a-LDPCw0rEcFTm0SqAhLz8sYT8sbkYtse1pvMHY9Qij547diNhlP__DYxtuT8XojRO/pub?gid=1596580014&single=true&output=csv')
historic = cargar_datos()

st.markdown('# Lateness Report')
st.markdown('### Overview')

historic['datestamp'] = pd.to_datetime(historic['datestamp'], format='mixed')

historic = historic[['datestamp', 'Full Name', 'LOB', 'Status', 'Schedule In',
       'Schedule Out', 'Scheduled Hours', 'Clock in time', 'away', 'Lunch',
       'Clock out time', 'Total work time', 'Holiday', 'Active', 'Exception']]

historic = historic.loc[
historic['datestamp'].dt.year == 2026
]


nombre_meses = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

st.sidebar.title('Filtros')


años = historic['datestamp'].dt.year.unique()

año_seleccionado = st.sidebar.selectbox(
'Año', options= años
)

meses_disponibles = sorted(
    historic['datestamp'].dt.month.unique() 
    
    )

mes_seleccionado = st.sidebar.selectbox(
    'Mes:', meses_disponibles,
    format_func=lambda x: nombre_meses[x])


fechas_disponibles = historic.loc[
    
    historic['datestamp'].dt.month == mes_seleccionado, 'datestamp'


].dropna().unique()
                                  
fecha_seleccionada = st.sidebar.multiselect(
    'Fecha:',
    options=sorted(fechas_disponibles),
    default=sorted(fechas_disponibles),
    format_func=lambda x: x.strftime('%m/%d/%Y'
    )
)

status_disponibles = historic.loc[
        (historic['datestamp'].dt.year == año_seleccionado) &
        (historic['datestamp'].dt.month ==mes_seleccionado)&
        (historic['Status'].isin(['Late', 'Late In', 'Called Out']))
        , 'Status'
    ].dropna().unique()

status_seleccionado = st.sidebar.multiselect('Status:',
                                           options = status_disponibles,
                                             default = status_disponibles
                                            )

datos  = historic.loc[historic['datestamp'].dt.month == mes_seleccionado]

tardanzas_por_LOB = datos.loc[historic['Status'].isin(status_seleccionado) ].groupby('LOB').size().reset_index(name='Total Tardanza').sort_values('Total Tardanza', ascending= False)
tardanzas_por_fecha = datos.loc[datos['Status'].isin(status_seleccionado)].groupby('datestamp').size().reset_index(name='Total Tardanza').sort_values('datestamp')

col1, col2 = st.columns(2)

with col1:
  st.subheader('Tardanzas por LOB')    
  fig, ax = plt.subplots(figsize=(10, 6))
  ax.bar(tardanzas_por_LOB['LOB'], tardanzas_por_LOB['Total Tardanza'], color='red')
  ax.set_title('Tardanzas por LOB')
  ax.set_xlabel('LOB')
  ax.set_ylabel('Total Tardanzas')
  plt.xticks(rotation=45, ha='right')
  plt.tight_layout()

  st.pyplot(fig)

with col2:
    st.subheader('Tardanzas por dia del mes')    

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(tardanzas_por_fecha['datestamp'], tardanzas_por_fecha['Total Tardanza'], 
            color='red', marker='o', linewidth=2, markersize=5)

    # Etiquetas en cada punto
    for x, y in zip(tardanzas_por_fecha['datestamp'], tardanzas_por_fecha['Total Tardanza']):
        ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 8), ha='center', fontsize=10)

    ax.set_title('Tardanzas por Día — Mayo 2026', fontsize=14)
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Total Tardanzas')
    ax.set_xticks(tardanzas_por_fecha['datestamp'])
    plt.xticks(rotation=90, ha='right', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=1)
    plt.tight_layout()
    st.pyplot(fig)
    
