import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, time
from supabase import create_client

# --- 1. CONFIGURACIÓN SUPABASE ---
SUPABASE_URL = "https://gqwxrxszojvphfbnkcfv.supabase.co"
SUPABASE_KEY = "sb_publishable_Y-CKD8q9mg8pBQ-CIJ88Bw_v83hmqOL"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Configuración de página
st.set_page_config(page_title="C5 - Registro Maestro", layout="wide", initial_sidebar_state="expanded")

# --- CSS PARA ESTILOS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #0a0e17; }
    h1, h2, h3, span, p, label { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Inicializar estados
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if 'lat_f' not in st.session_state: st.session_state.lat_f = ""
if 'lon_f' not in st.session_state: st.session_state.lon_f = ""

def calcular_minutos(t_inicio, t_evento):
    d1 = datetime.combine(date.today(), t_inicio)
    d2 = datetime.combine(date.today(), t_evento)
    return round((d2 - d1).total_seconds() / 60, 2)

def pantalla_login():
    st.title("🔐 CENTRO DE OPERACION NACIONAL - C5")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        usuarios_permitidos = {"CONC5": "12345", "ELMER RODRIGUEZ": "ELIZAharol31"}
        if user in usuarios_permitidos and usuarios_permitidos[user] == password:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

if not st.session_state.autenticado:
    pantalla_login()
else:
    st.title("🛡️ REGISTROS POSITIVOS DEL C.O.N - C5")

    st.markdown('<p class="author-text">Creado por= Cabo 1° Elmer Rodriguez</p>', unsafe_allow_html=True)
    
    # Mapa con estilo Google Satellite Hybrid (Satélite + Calles)
    m = folium.Map(location=[8.9824, -79.5199], zoom_start=12)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Maps Satellite',
        name='Google Satellite Hybrid',
        overlay=True,
        control=True
    ).add_to(m)
    
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=400, width=1200)

    if map_data and map_data.get('last_clicked'):
        st.session_state.lat_f = map_data['last_clicked']['lat']
        st.session_state.lon_f = map_data['last_clicked']['lng']

    col_a, col_b = st.columns(2)
    col_a.text_input("Latitud capturada", value=st.session_state.lat_f, disabled=True)
    col_b.text_input("Longitud capturada", value=st.session_state.lon_f, disabled=True)

    st.divider()
    modo = st.radio("SELECCIONE EL TIPO DE REGISTRO:", ["PREVENTIVO", "POSITIVO"], horizontal=True)
    st.divider()

    with st.form("registro_maestro_total", clear_on_submit=False):
        st.subheader("📍 Ubicación y Recursos")
        col_loc1, col_loc2, col_loc3 = st.columns(3)
        provincia = col_loc1.selectbox("PROVINCIA", ["SELECCIONAR", "LOS SANTOS", "VERAGUAS", "PANAMA", "COLÓN"])
        distrito = col_loc2.selectbox("DISTRITO", ["SELECCIONAR", "COLÓN"])
        corregimiento = col_loc3.selectbox("CORREGIMIENTO", ["SELECCIONAR", "BARRIO NORTE", "ACHIOTE", "AGUA BUENA"])
        
        col_loc4, col_loc5, col_loc6 = st.columns(3)
        referencia = col_loc4.text_input("REFERENCIA")
        zp_policial = col_loc5.selectbox("ZP POLICIALES / ENLACE", ["SELECCIONAR", "3RA ZP COLON", "4TA ZP CHIRIQUI"])
        recursos = col_loc6.selectbox("RECURSOS", ["SELECCIONAR", "PATRULLA", "LINCE", "CICLISTA"])

        st.subheader("⏱️ Tiempos, Unidades y Cámaras")
        c1, c2, c3, c4 = st.columns(4)
        fecha = c1.date_input("FECHA")
        centro_mando = c1.selectbox("CENTRO DE MANDO", ["SELECCIONAR", "CORCOL", "CON"])
        unidad_vv = c1.selectbox("UNIDAD DE VV/104", ["SELECCIONAR", "ELMER RODRIGUEZ"])
        canal = c2.selectbox("CANAL DE ENTRADA", ["SELECCIONAR", "CLL-104", "VIDEO-VIGILANCIA"])
        unidad_despacho = c2.selectbox("UNIDAD DE DESPACHO", ["SELECCIONAR", "ISMAEL PEÑA"])
        t_inicial = c3.time_input("T. INICIAL", step=60)
        
        h_despacho = c3.time_input("H. DESPACHO", step=60)
        v_despacho = calcular_minutos(t_inicial, h_despacho)
        
        camara_id = c3.text_input("CAMARA/ID")
        c3.number_input("V. DESPACHO (min)", value=v_despacho, disabled=True)
        
        h_atencion = c4.time_input("H. ATENCION", step=60)
        v_atencion = calcular_minutos(t_inicial, h_atencion)
        c4.number_input("V. ATENCION (min)", value=v_atencion, disabled=True)
        
        h_cierre = c4.time_input("H. CIERE", step=60)
        v_cierre = calcular_minutos(t_inicial, h_cierre)
        c4.number_input("V. CIERRE (min)", value=v_cierre, disabled=True)

        st.subheader("📋 Incidentes")
        lista_maestra_a = ["SELECCIONAR", "ACCIDENTE DE TRÁNSITO", "ACCIDENTES", "ALERTAS"]
        lista_maestra_b = ["SELECCIONAR", "A LOCAL COMERCIAL", "A RESIDENCIA", "A PROPIEDAD"]
        c8, c9 = st.columns(2)
        tipo_inc = c8.selectbox("TIPO DE INCIDENTES", lista_maestra_a)
        subtipo_inc = c9.selectbox("SUBTIPO DE INCIDENTES", lista_maestra_b)

        cierre_tipo, cierre_subtipo = "N/A", "N/A"
        p1, p2, p3, p4, p5, p6 = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        
        if modo == "POSITIVO":
            c_cierre1, c_cierre2 = st.columns(2)
            cierre_tipo = c_cierre1.selectbox("CIERRE TIPO", lista_maestra_a)
            cierre_subtipo = c_cierre2.selectbox("CIERRE SUBTIPO", lista_maestra_b)
            cols = st.columns(6)
            lista_pos = ["SELECCIONAR", "APOYO AL CIUDADANO", "ARTICULOS RECUPERADOS"]
            p1, p2, p3, p4, p5, p6 = cols[0].selectbox("P1", lista_pos), cols[1].selectbox("P2", lista_pos), cols[2].selectbox("P3", lista_pos), cols[3].selectbox("P4", lista_pos), cols[4].selectbox("P5", lista_pos), cols[5].selectbox("P6", lista_pos)

        narrativa = st.text_input("REPORTE/NARRATIVA")
        link_video = st.text_input("ENLACE DE VÍDEO")
        
        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            campos_faltantes = []
            if provincia == "SELECCIONAR": campos_faltantes.append("Provincia")
            if distrito == "SELECCIONAR": campos_faltantes.append("Distrito")
            if corregimiento == "SELECCIONAR": campos_faltantes.append("Corregimiento")
            if tipo_inc == "SELECCIONAR": campos_faltantes.append("Tipo de Incidente")
            if not narrativa.strip(): campos_faltantes.append("Narrativa/Reporte")
            if not link_video.strip(): campos_faltantes.append("Enlace de Vídeo")
            if not camara_id.strip(): campos_faltantes.append("ID de Cámara")
            if not referencia.strip(): campos_faltantes.append("Referencia")
            if st.session_state.lat_f == "": campos_faltantes.append("Ubicación en el Mapa")
            
            if campos_faltantes:
                st.error(f"❌ Falta completar: {', '.join(campos_faltantes)}")
            else:
                nuevo_registro = {
                    "FECHA_HORA": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "MODO": modo, "PROVINCIA": provincia, "DISTRITO": distrito, "CORREGIMIENTO": corregimiento,
                    "REFERENCIA": referencia, "ZP_POLICIAL": zp_policial, "RECURSOS": recursos,
                    "FECHA": str(fecha), "CENTRO_DE_MANDO": centro_mando, "UNIDAD_VV": unidad_vv,
                    "CANAL_ENTRADA": canal, "UNIDAD_DESPACHO": unidad_despacho, "T_INICIAL": str(t_inicial),
                    "H_DESPACHO": str(h_despacho), "CAMARA_ID": camara_id, "H_ATENCION": str(h_atencion),
                    "H_CIERRE": str(h_cierre), "TIPO_INCIDENTE": tipo_inc, "SUBTIPO_INCIDENTE": subtipo_inc,
                    "CIERRE_TIPO": cierre_tipo, "CIERRE_SUBTIPO": cierre_subtipo,
                    "P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6,
                    "NARRATIVA": narrativa, "LINK_VIDEO": link_video,
                    "LATITUD": str(st.session_state.lat_f), "LONGITUD": str(st.session_state.lon_f),
                    "VARIANZA_DESPACHO": v_despacho, "VARIANZA_ATENCION": v_atencion, "VARIANZA_CIERRE": v_cierre
                }
                try:
                    supabase.table("registros_c5").insert(nuevo_registro).execute()
                    st.success("✔️ Registro guardado exitosamente.")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
