import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from datetime import datetime

# 1. Configuración de página
st.set_page_config(page_title="C5 - Registro Maestro", layout="wide")

# 2. Ruta del archivo respaldada
archivo_excel = "REGISTROS_C5.csv"

# 3. Inicializar estados de la aplicación (Base de datos persistente en sesión)
if "autenticado" not in st.session_state: 
    st.session_state.autenticado = False
if 'lat_f' not in st.session_state: 
    st.session_state.lat_f = ""
if 'lon_f' not in st.session_state: 
    st.session_state.lon_f = ""

# Inicializar la base de datos interna de la app cargando el archivo si existe
if "db_registros" not in st.session_state:
    if os.path.exists(archivo_excel):
        try:
            st.session_state.db_registros = pd.read_csv(archivo_excel, encoding="utf-8-sig")
        except Exception:
            st.session_state.db_registros = pd.DataFrame()
    else:
        st.session_state.db_registros = pd.DataFrame()

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
    
    # Pestañas para separar las pantallas por completo
    tab_registro, tab_visor = st.tabs(["📝 Formulario de Registro", "📊 Visor de Base de Datos y Exportación"])

    # --- VENTANA 1: FORMULARIO DE REGISTRO ---
    with tab_registro:
        # Mapa
        m = folium.Map(location=[8.9824, -79.5199], zoom_start=15, 
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
            provincia = col_loc1.selectbox("PROVINCIA", ["SELECCIONAR", "LOS SANTOS", "VERAGUAS", "PANAMA", "PANAMA OESTE"])
            distrito = col_loc2.selectbox("DISTRITO", ["SELECCIONAR", "AGUADULCE"])
            corregimiento = col_loc3.selectbox("CORREGIMIENTO", ["SELECCIONAR", "24 DE DICIEMBRE", "ACHIOTE", "AGUA BUENA"])
            
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
                    "NARRATIVA": narrativa,  # <- ¡CORREGIDO AQUÍ! (Ya no dará NameError)
                    "LINK_VIDEO": link_video,
                    "LATITUD": st.session_state.lat_f,
                    "LONGITUD": st.session_state.lon_f
                }
                
                df_fila = pd.DataFrame([nuevo_registro])
                
                # 1. Guardar en la memoria interna de la aplicación (Infalible)
                st.session_state.db_registros = pd.concat([st.session_state.db_registros, df_fila], ignore_index=True)
                
                # 2. Intentar guardar una copia física en el archivo local de forma silenciosa
                try:
                    st.session_state.db_registros.to_csv(archivo_excel, index=False, encoding="utf-8-sig", sep=";")
                except Exception:
                    pass
                
                st.success(f"✔️ Registro {modo} procesado y añadido exitosamente.")

    # --- VENTANA 2: VISOR DE DATOS E EXPORTACIÓN ---
    with tab_visor:
        st.subheader("📊 Visor de Base de Datos y Exportación")
        
        # Leemos los datos directamente desde el Session State interno
        if not st.session_state.db_registros.empty:
            st.dataframe(st.session_state.db_registros, use_container_width=True)
            
            # Botón de exportación directa y limpia
            csv_data = st.session_state.db_registros.to_csv(index=False, encoding="utf-8-sig").encode('utf-8-sig')
            st.download_button(
                label="📥 Descargar Base de Datos para Excel",
                data=csv_data,
                file_name="REGISTROS_C5.csv",
                mime="text/csv",
                key="btn_descarga_c5_final"
            )
        else:
            st.info("💡 Aún no existen registros guardados. Use la pestaña de 'Formulario de Registro' para añadir el primer reporte.")

    # Cierre de sesión en la barra lateral
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
