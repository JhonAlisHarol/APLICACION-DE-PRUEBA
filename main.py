import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from datetime import datetime
from supabase import create_client

# --- 1. CONFIGURACIÓN SUPABASE ---
# Coloca aquí tus datos reales de la sección API de tu proyecto
SUPABASE_URL = "https://gqwxrxszojvphfbnkcfv.supabase.co"
SUPABASE_KEY = "sb_publishable_Y-CKD8q9mg8pBQ-CIJ88Bw_v83hmqOL"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Configuración de página
st.set_page_config(page_title="C5 - Registro Maestro", layout="wide")

# 3. Inicializar estados
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if 'lat_f' not in st.session_state: st.session_state.lat_f = ""
if 'lon_f' not in st.session_state: st.session_state.lon_f = ""

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
    tab_registro, tab_visor = st.tabs(["📝 Formulario de Registro", "📊 Visor de Base de Datos y Exportación"])

    # --- VENTANA 1: FORMULARIO DE REGISTRO ---
    with tab_registro:
        # Mapa
        m = folium.Map(location=[8.9824, -79.5199], zoom_start=10, 
                       tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri")
        folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}", attr="Esri", name="Labels", overlay=True).add_to(m)
        m.add_child(folium.LatLngPopup())
        map_data = st_folium(m, height=600, width=1600)

        if map_data and map_data.get('last_clicked'):
            st.session_state.lat_f = map_data['last_clicked']['lat']
            st.session_state.lon_f = map_data['last_clicked']['lng']

        col_a, col_b = st.columns(2)
        col_a.text_input("Latitud capturada", value=st.session_state.lat_f, disabled=True)
        col_b.text_input("Longitud capturada", value=st.session_state.lon_f, disabled=True)

        st.divider()
        modo = st.radio("SELECCIONE EL TIPO DE REGISTRO:", ["PREVENTIVO", "POSITIVO"], horizontal=True, key="modo_selector")
        st.divider()

        # --- FORMULARIO ---
        with st.form("registro_maestro_total", clear_on_submit=True):
            
            # UBICACIÓN Y RECURSOS
            st.subheader("📍 Ubicación y Recursos")
            col_loc1, col_loc2, col_loc3 = st.columns(3)
            provincia = col_loc1.selectbox("PROVINCIA", ["SELECCIONAR", "LOS SANTOS", "VERAGUAS", "PANAMA", "COLÓN"])
            distrito = col_loc2.selectbox("DISTRITO", ["SELECCIONAR", "COLÓN"])
            corregimiento = col_loc3.selectbox("CORREGIMIENTO", ["SELECCIONAR", "BARRIO NORTE", "ACHIOTE", "AGUA BUENA"])
            
            col_loc4, col_loc5, col_loc6 = st.columns(3)
            referencia = col_loc4.text_input("REFERENCIA")
            zp_policial = col_loc5.selectbox("ZP POLICIALES / ENLACE", ["SELECCIONAR", "3RA ZP COLON", "4TA ZP CHIRIQUI"])
            recursos = col_loc6.selectbox("RECURSOS", ["SELECCIONAR", "PATRULLA", "LINCE", "CICLISTA"])

            # TIEMPOS, UNIDADES Y CÁMARAS
            st.subheader("⏱️ Tiempos, Unidades y Cámaras")
            c1, c2, c3, c4 = st.columns(4)
            fecha = c1.date_input("FECHA")
            centro_mando = c1.selectbox("CENTRO DE MANDO", ["SELECCIONAR", "CORCOL", "CON"])
            unidad_vv = c1.selectbox("UNIDAD DE VV/104", ["SELECCIONAR", "ELMER RODRIGUEZ"])
            canal = c2.selectbox("CANAL DE ENTRADA", ["SELECCIONAR", "CLL-104", "VIDEO-VIGILANCIA"])
            unidad_despacho = c2.selectbox("UNIDAD DE DESPACHO", ["SELECCIONAR", "ISMAEL PEÑA"])
            t_inicial = c3.time_input("T. INICIAL", step=60)
            h_despacho = c3.time_input("H. DESPACHO", step=60)
            camara_id = c3.text_input("CAMARA/ID")
            h_atencion = c4.time_input("H. ATENCION", step=60)
            h_cierre = c4.time_input("H. CIERE", step=60)

            # INCIDENTES
            st.subheader("📋 Incidentes y Cierre")
            lista_maestra_a = ["SELECCIONAR", "ACCIDENTE DE TRÁNSITO", "ACCIDENTES", "ALERTAS"]
            lista_maestra_b = ["SELECCIONAR", "A LOCAL COMERCIAL", "A RESIDENCIA", "A PROPIEDAD"]
            c8, c9 = st.columns(2)
            tipo_inc = c8.selectbox("TIPO DE INCIDENTES", lista_maestra_a)
            subtipo_inc = c9.selectbox("SUBTIPO DE INCIDENTES", lista_maestra_b)

            # LOGICA POSITIVOS
            cierre_tipo, cierre_subtipo = "N/A", "N/A"
            p1, p2, p3, p4, p5, p6 = "", "", "", "", "", ""
            
            if modo == "POSITIVO":
                c_cierre1, c_cierre2 = st.columns(2)
                cierre_tipo = c_cierre1.selectbox("CIERRE TIPO", lista_maestra_a)
                cierre_subtipo = c_cierre2.selectbox("CIERRE SUBTIPO", lista_maestra_b)

                st.subheader("✅ Selección de Positivos")
                cols = st.columns(6)
                lista_pos = ["SELECCIONAR", "APOYO AL CIUDADANO", "ARTICULOS RECUPERADOS"]
                p1 = cols[0].selectbox("P1", lista_pos)
                p2 = cols[1].selectbox("P2", lista_pos)
                p3 = cols[2].selectbox("P3", lista_pos)
                p4 = cols[3].selectbox("P4", lista_pos)
                p5 = cols[4].selectbox("P5", lista_pos)
                p6 = cols[5].selectbox("P6", lista_pos)

            # CAMPOS FINALES
            narrativa = st.text_input("REPORTE/NARRATIVA")
            link_video = st.text_input("ENLACE DE VÍDEO")
            
            submitted = st.form_submit_button("Guardar Registro")
            
        if submitted:
            nuevo_registro = {
                "FECHA_HORA": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "MODO": modo,
                "PROVINCIA": provincia,
                "DISTRITO": distrito,
                "CORREGIMIENTO": corregimiento,
                "REFERENCIA": referencia,
                "ZP_POLICIAL": zp_policial,
                "RECURSOS": recursos,
                "FECHA": str(fecha),
                "CENTRO_DE_MANDO": centro_mando,
                "UNIDAD_VV": unidad_vv,
                "CANAL_ENTRADA": canal,
                "UNIDAD_DESPACHO": unidad_despacho,
                "T_INICIAL": str(t_inicial),
                "H_DESPACHO": str(h_despacho),
                "CAMARA_ID": camara_id,
                "H_ATENCION": str(h_atencion),
                "H_CIERRE": str(h_cierre),
                "TIPO_INCIDENTE": tipo_inc,
                "SUBTIPO_INCIDENTE": subtipo_inc,
                "CIERRE_TIPO": cierre_tipo,
                "CIERRE_SUBTIPO": cierre_subtipo,
                "P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6,
                "NARRATIVA": narrativa,
                "LINK_VIDEO": link_video,
                "LATITUD": str(st.session_state.lat_f),
                "LONGITUD": str(st.session_state.lon_f)
            }
            
            # 2. Intentar guardar únicamente cuando el formulario ha sido enviado
            try:
                # Esta es la línea que falta para que se vaya a la nube
                supabase.table("registros_c5").insert(nuevo_registro).execute()
                st.success("✔️ Registro guardado exitosamente en la nube.")
            except Exception as e:
                st.error(f"Error al guardar en la nube: {e}")

    # --- VENTANA 2: VISOR ---
    with tab_visor:
        st.subheader("📊 Visor de Base de Datos")
        
        # Leemos directamente de la nube al presionar el botón
        if st.button("🔄 Cargar datos desde la nube"):
            try:
                response = supabase.table("registros_c5").select("*").execute()
                df = pd.DataFrame(response.data)
                
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    # Descarga para Excel
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Descargar a CSV", csv, "registros_nube.csv", "text/csv")
                else:
                    st.info("No hay registros en la base de datos.")
            except Exception as e:
                st.error(f"Error al conectar con Supabase: {e}")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
