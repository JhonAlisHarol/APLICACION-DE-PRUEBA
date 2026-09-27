import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import HeatMap, MarkerCluster, Fullscreen
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Centro de Operación Nacional | Dashboard Analítico",
    page_icon="🛡️",
    layout="wide"
)

# --- ESTILOS CSS CON ANIMACIÓN DE NEONES GIRATORIOS / EN MOVIMIENTO ---
st.markdown("""
    <style>
    /* Fondo general oscuro estilo centro de control */
    .stApp {
        background-color: #0b0f19;
        color: #ffffff;
    }
    
    /* Animación fluida de desplazamiento para la cinta de colores de neón */
    @keyframes neonBorderMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Contenedor del Título Principal con Cinta Neón en Movimiento */
    .neon-title-container {
        border: 4px solid transparent;
        background: linear-gradient(135deg, #101828 0%, #0b0f19 100%), 
                    linear-gradient(90deg, #ff0055, #00ffff, #00ff66, #ffae00, #bd00ff, #ff0055);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        background-size: 300% 300%;
        animation: neonBorderMove 6s ease infinite;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.5), inset 0 0 20px rgba(255, 0, 85, 0.3);
        margin-bottom: 30px;
    }
    
    .neon-title-text {
        color: #00ffff;
        font-size: 28px;
        font-weight: 800;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 1.5px;
        text-shadow: 0 0 15px rgba(0, 255, 255, 0.9), 0 0 25px rgba(255, 0, 85, 0.6);
    }
    
    .neon-sub-text {
        color: #ffae00;
        font-size: 14px;
        font-style: italic;
        margin-top: 10px;
        text-shadow: 0 0 10px rgba(255, 174, 0, 0.8);
    }

    /* Contenedores con Marcos de Neón Multicolor en Movimiento para las Secciones */
    .neon-section-box {
        border: 3px solid transparent;
        background: rgba(16, 24, 40, 0.7), 
                    linear-gradient(90deg, #00ffff, #bd00ff, #ff0055, #00ff66, #00ffff);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        background-size: 300% 300%;
        animation: neonBorderMove 6s ease infinite;
        padding: 18px;
        border-radius: 10px;
        margin-top: 25px;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
    }

    .neon-section-title {
        color: #00ff66;
        font-size: 19px;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 255, 102, 0.8), 0 0 20px rgba(0, 255, 255, 0.5);
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO PRINCIPAL CON EFECTO NEÓN MULTICOLOR EN MOVIMIENTO ---
st.markdown("""
    <div class="neon-title-container">
        <div class="neon-title-text">🛡️ CENTRO DE OPERACIÓN NACIONAL | ESTUDIO DE DELITOS DE ALTO IMPACTO</div>
        <div class="neon-sub-text">DESARROLLADO BY: CABO 1° ELMER RODRIGUEZ</div>
    </div>
""", unsafe_allow_html=True)

# --- CONEXIÓN DIRECTA AL GOOGLE SHEET ---
@st.cache_data(ttl=600)
def cargar_datos_zonas():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTGwA9lT4NcdV9kosXlRP-yPUgZjPrAEIorpOL1Zb5vmHLB4RRilqAazcSDCvnWtA/pub?output=csv&gid=412219270"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df = cargar_datos_zonas()

    # --- PROCESAMIENTO ROBUSTO DE FECHA, HORA Y COORDENADAS ---
    if 'FECHA' in df.columns:
        df['Fecha_dt'] = pd.to_datetime(df['FECHA'], format='mixed', dayfirst=True, errors='coerce')
        
        df['Mes_Num'] = df['Fecha_dt'].dt.month
        meses_es = {1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO', 
                    7: 'JULIO', 8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'}
        df['Mes_Nombre'] = df['Mes_Num'].map(meses_es)
        
        dias_es = {0: 'LUNES', 1: 'MARTES', 2: 'MIÉRCOLES', 3: 'JUEVES', 4: 'VIERNES', 5: 'SÁBADO', 6: 'DOMINGO'}
        df['Dia_Semana'] = df['Fecha_dt'].dt.dayofweek.map(dias_es)
    
    if 'Hora' in df.columns:
        df['Hora_int'] = pd.to_datetime(df['Hora'], format='%H:%M:%S', errors='coerce').dt.hour
        df['Hora_int'] = df['Hora_int'].fillna(
            pd.to_numeric(df['Hora'].astype(str).str.split(':').str[0], errors='coerce')
        )

    # Limpieza blindada de coordenadas (comas por puntos)
    if 'LATITUD' in df.columns and 'LONGITUD' in df.columns:
        df['Lat_clean'] = pd.to_numeric(
            df['LATITUD'].astype(str).str.replace(',', '.', regex=False).str.replace(r'[^0-9.\-]', '', regex=True), 
            errors='coerce'
        )
        df['Lon_clean'] = pd.to_numeric(
            df['LONGITUD'].astype(str).str.replace(',', '.', regex=False).str.replace(r'[^0-9.\-]', '', regex=True), 
            errors='coerce'
        )

    col_zona = 'DescripcionZonaPolicial' if 'DescripcionZonaPolicial' in df.columns else 'ZonaPolicial'
    
    # --- PANEL DE CONTROL LATERAL: FILTROS, FECHAS Y ZONAS ---
    st.sidebar.markdown("### 🔍 Fechas y Horas")
    
    if 'Fecha_dt' in df.columns and not df['Fecha_dt'].dropna().empty:
        min_date = df['Fecha_dt'].min().date()
        max_date = df['Fecha_dt'].max().date()
        
        fecha_desde = st.sidebar.date_input("Desde:", value=min_date, min_value=min_date, max_value=max_date)
        fecha_hasta = st.sidebar.date_input("Hasta:", value=max_date, min_value=min_date, max_value=max_date)
    else:
        fecha_desde, fecha_hasta = None, None

    hora_inicial = st.sidebar.selectbox("Hora Inicial:", list(range(24)), index=0)
    hora_final = st.sidebar.selectbox("Hora Final:", list(range(24)), index=23)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Filtros Específicos")
    
    tipo_delito_seleccionado = st.sidebar.selectbox(
        "Filtrar por Tipo de Delito:", 
        ['Todos'] + list(df['Tipo'].dropna().unique()) if 'Tipo' in df.columns else ['Todos']
    )

    zonas_disponibles = ['Todas'] + list(df[col_zona].dropna().unique()) if col_zona in df.columns else ['Todas']
    zona_seleccionada = st.sidebar.selectbox("Filtrar por Zona Policial:", zonas_disponibles)

    dias_disponibles = ['Todos', 'LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
    dia_seleccionado = st.sidebar.selectbox("Filtrar por Día de la Semana:", dias_disponibles)

    # --- APLICACIÓN DE FILTROS AL DATAFRAME ---
    df_filtrado = df.copy()

    if tipo_delito_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_delito_seleccionado]

    if zona_seleccionada != 'Todas' and col_zona in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado[col_zona] == zona_seleccionada]

    if dia_seleccionado != 'Todos' and 'Dia_Semana' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Dia_Semana'] == dia_seleccionado]

    if fecha_desde and fecha_hasta and 'Fecha_dt' in df_filtrado.columns:
        df_filtrado = df_filtrado[
            (df_filtrado['Fecha_dt'].dt.date >= fecha_desde) & 
            (df_filtrado['Fecha_dt'].dt.date <= fecha_hasta)
        ]

    if 'Hora_int' in df_filtrado.columns:
        df_filtrado = df_filtrado[
            (df_filtrado['Hora_int'] >= hora_inicial) & 
            (df_filtrado['Hora_int'] <= hora_final)
        ]

    st.sidebar.markdown("---")
    st.sidebar.metric(label="Casos en Filtro Actual", value=f"{len(df_filtrado):,}")

    # --- SECCIÓN 1: BARRAS VERTICALES DE LOS TIPOS DE DELITOS ---
    st.markdown("""
        <div class="neon-section-box">
            <div class="neon-section-title">📊 DISTRIBUCIÓN GENERAL DE DELITOS DE ALTO IMPACTO</div>
        </div>
    """, unsafe_allow_html=True)
    
    if 'Tipo' in df_filtrado.columns:
        conteo_delitos = df_filtrado['Tipo'].value_counts().reset_index()
        conteo_delitos.columns = ['Tipo de Delito', 'Cantidad']
        
        fig_bar = px.bar(
            conteo_delitos,
            x='Tipo de Delito',
            y='Cantidad',
            text='Cantidad',
            color='Tipo de Delito',
            color_discrete_sequence=['#00ffff', '#00ff66', '#ff3333', '#ffa500', '#bd00ff', '#ffff00']
        )
        
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(showgrid=False, title='Tipo de Delito'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Total de Casos'),
            margin=dict(t=20, b=20, l=20, r=20),
            height=360,
            showlegend=False
        )
        fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- SECCIÓN 2: GRÁFICO EJECUTIVO DE ZONAS POLICIALES ---
    st.markdown("""
        <div class="neon-section-box">
            <div class="neon-section-title">🏙️ INCIDENTES POR ZONA POLICIAL (ORDEN EJECUTIVO DE MAYOR A MENOR)</div>
        </div>
    """, unsafe_allow_html=True)
    
    if col_zona in df_filtrado.columns:
        conteo_zonas = df_filtrado[col_zona].value_counts().reset_index()
        conteo_zonas.columns = ['Zona Policial', 'Total Casos']
        conteo_zonas = conteo_zonas.sort_values(by='Total Casos', ascending=False)
        
        fig_zonas = px.bar(
            conteo_zonas,
            x='Zona Policial',
            y='Total Casos',
            text='Total Casos',
            color='Total Casos',
            color_continuous_scale=['#00d2ff', '#0072ff', '#bd00ff', '#ff3366', '#ff9900', '#00ffcc']
        )
        
        fig_zonas.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(showgrid=False, title='Zona Policial', tickangle=-20),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Cantidad de Casos'),
            margin=dict(t=20, b=40, l=20, r=20),
            height=380,
            coloraxis_showscale=False
        )
        
        fig_zonas.update_traces(
            textfont_size=13, 
            textangle=0, 
            textposition="outside", 
            cliponaxis=False,
            marker=dict(line=dict(width=1.5, color='#00ffff'))
        )
        
        st.plotly_chart(fig_zonas, use_container_width=True)

    # --- SECCIÓN 3: DOS GRÁFICOS HORIZONTALES (MESES Y DÍAS) ---
    col_h1, col_h2 = st.columns(2)

    with col_h1:
        st.markdown("""
            <div class="neon-section-box">
                <div class="neon-section-title">📅 TOTAL DE CASOS POR MESES</div>
            </div>
        """, unsafe_allow_html=True)
        
        if 'Mes_Num' in df_filtrado.columns and 'Mes_Nombre' in df_filtrado.columns:
            conteo_meses = df_filtrado.groupby(['Mes_Num', 'Mes_Nombre']).size().reset_index(name='Total Casos')
            conteo_meses = conteo_meses.sort_values(by='Mes_Num', ascending=True)
            
            fig_meses = px.bar(
                conteo_meses,
                x='Total Casos',
                y='Mes_Nombre',
                orientation='h',
                text='Total Casos',
                color='Total Casos',
                color_continuous_scale=['#00ff66', '#00d2ff', '#0072ff']
            )
            
            orden_meses_fijo = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
            fig_meses.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Total de Casos'),
                yaxis=dict(showgrid=False, title='', categoryorder='array', categoryarray=orden_meses_fijo[::-1]),
                margin=dict(t=10, b=20, l=10, r=20),
                height=350,
                coloraxis_showscale=False
            )
            fig_meses.update_traces(textfont_size=12, textposition="inside", marker=dict(line=dict(width=1, color='#00ff66')))
            st.plotly_chart(fig_meses, use_container_width=True)

    with col_h2:
        st.markdown("""
            <div class="neon-section-box">
                <div class="neon-section-title">📆 TOTAL DE CASOS POR DÍA DE LA SEMANA</div>
            </div>
        """, unsafe_allow_html=True)
        
        if 'Dia_Semana' in df_filtrado.columns:
            orden_dias = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
            conteo_dias = df_filtrado['Dia_Semana'].value_counts().reindex(orden_dias).reset_index()
            conteo_dias.columns = ['Día', 'Total Casos']
            conteo_dias['Total Casos'] = conteo_dias['Total Casos'].fillna(0)
            
            fig_dias = px.bar(
                conteo_dias,
                x='Total Casos',
                y='Día',
                orientation='h',
                text='Total Casos',
                color='Total Casos',
                color_continuous_scale=['#ffae00', '#ff3333', '#bd00ff']
            )
            
            fig_dias.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Total de Casos'),
                yaxis=dict(showgrid=False, title='', categoryorder='array', categoryarray=orden_dias[::-1]),
                margin=dict(t=10, b=20, l=10, r=20),
                height=350,
                coloraxis_showscale=False
            )
            fig_dias.update_traces(textfont_size=12, textposition="inside", marker=dict(line=dict(width=1, color='#ffae00')))
            st.plotly_chart(fig_dias, use_container_width=True)

    # --- SECCIÓN 4: ESTUDIO TEMPORAL DE HORAS ---
    st.markdown("""
        <div class="neon-section-box">
            <div class="neon-section-title">⏰ ESTUDIO DE INCIDENCIA POR FRANJA HORARIA (00:00 A 23:59 HRS)</div>
        </div>
    """, unsafe_allow_html=True)

    if 'Hora_int' in df_filtrado.columns:
        conteo_horas = df_filtrado['Hora_int'].value_counts().reindex(range(24), fill_value=0).reset_index()
        conteo_horas.columns = ['Hora', 'Total Casos']
        conteo_horas['Hora_Str'] = conteo_horas['Hora'].astype(str).str.zfill(2) + ":00 hrs"

        fig_horas = px.area(
            conteo_horas,
            x='Hora_Str',
            y='Total Casos',
            markers=True,
            text='Total Casos',
            color_discrete_sequence=['#00ffff']
        )

        fig_horas.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(showgrid=False, title='Franja Horaria del Día'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Cantidad de Casos'),
            margin=dict(t=20, b=20, l=20, r=20),
            height=380,
            showlegend=False
        )
        
        fig_horas.update_traces(
            mode='lines+markers+text',
            textposition='top center',
            textfont_size=11,
            line=dict(width=3, color='#00ffff'),
            marker=dict(size=8, color='#ff0055', line=dict(width=2, color='#ffffff')),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 255, 0.15)'
        )
        
        st.plotly_chart(fig_horas, use_container_width=True)

    # --- SECCIÓN 5: CENTRO DE CONTROL GEOESPACIAL (MAPA HÍBRIDO + PANTALLA COMPLETA + CALOR) ---
    st.markdown("""
        <div class="neon-section-box">
            <div class="neon-section-title">🛰️ CENTRO DE CONTROL GEOESPACIAL Y MAPA TÁCTICO MASIVO</div>
        </div>
    """, unsafe_allow_html=True)

    modo_mapa = st.radio(
        "Seleccione la Capa de Visualización del Mapa:",
        ["🔥 3. Mapa de Calor (Density)", "📍 2. Mapa de Incidentes (Puntos)", "🌐 1. Mapa por Grupo (Cluster / Agrupado)"],
        horizontal=True
    )

    if 'Lat_clean' in df_filtrado.columns and 'Lon_clean' in df_filtrado.columns:
        df_geo = df_filtrado.dropna(subset=['Lat_clean', 'Lon_clean']).copy()
        df_geo = df_geo[(df_geo['Lat_clean'] != 0) & (df_geo['Lon_clean'] != 0)]
        
        if not df_geo.empty:
            lat_centro = df_geo['Lat_clean'].mean()
            lon_centro = df_geo['Lon_clean'].mean()

            # Mapa base con vista satelital híbrida Google
            m = folium.Map(location=[lat_centro, lon_centro], zoom_start=10)
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                attr='Google Hybrid',
                name='Google Hybrid',
                overlay=False,
                control=True
            ).add_to(m)

            # Botón de pantalla completa limpio y operativo
            Fullscreen(position="topright", title="Pantalla Completa", title_cancel="Salir de Pantalla Completa").add_to(m)

            if modo_mapa == "🔥 3. Mapa de Calor (Density)":
                heat_data = df_geo[['Lat_clean', 'Lon_clean']].values.tolist()
                HeatMap(
                    heat_data,
                    min_opacity=0.4,
                    max_zoom=14,
                    radius=18,
                    blur=22,
                    gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red'}
                ).add_to(m)

            elif modo_mapa == "📍 2. Mapa de Incidentes (Puntos)":
                muestra_geo = df_geo.head(3000)
                for _, row in muestra_geo.iterrows():
                    folium.CircleMarker(
                        location=[row['Lat_clean'], row['Lon_clean']],
                        radius=4,
                        color='#ff0055',
                        fill=True,
                        fill_color='#00ffff',
                        fill_opacity=0.8,
                        popup=f"<b>Delito:</b> {row.get('Tipo', 'N/A')}<br><b>Zona:</b> {row.get(col_zona, 'N/A')}"
                    ).add_to(m)

            else:
                marker_cluster = MarkerCluster().add_to(m)
                muestra_geo = df_geo.head(3000)
                for _, row in muestra_geo.iterrows():
                    folium.Marker(
                        location=[row['Lat_clean'], row['Lon_clean']],
                        popup=f"<b>Tipo:</b> {row.get('Tipo', 'N/A')}"
                    ).add_to(marker_cluster)

            st_folium(m, width=1250, height=600, key="mapa_tactico_limpio_final")
            st.success(f"🗺️ **Mapa Operativo Activado:** Visualizando **{len(df_geo):,} casos** con mapa de calor fluido y controles activos.")
        else:
            st.warning("No hay coordenadas válidas disponibles para los filtros seleccionados.")
    else:
        st.error("No se detectaron las columnas de coordenadas en el conjunto de datos.")

except Exception as e:
    st.error(f"Error al procesar el sistema geoespacial: {e}")
