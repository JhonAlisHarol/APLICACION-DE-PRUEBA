import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, time
import pytz
from supabase import create_client
import base64

# --- 1. CONFIGURACIÓN SUPABASE ---
SUPABASE_URL = "https://gqwxrxszojvphfbnkcfv.supabase.co"
SUPABASE_KEY = "sb_publishable_Y-CKD8q9mg8pBQ-CIJ88Bw_v83hmqOL"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Configuración de página
st.set_page_config(page_title="C5 - Registro Maestro", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# --FONDO EN MOVIMIENTO PARA TODO EL DOCUMENTO

st.markdown(
    """
    <style>
    /* 1. Fondo de video total */
    .video-background {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        z-index: -9999;
        overflow: hidden;
    }
    .video-background video {
        width: 100vw; height: 100vh;
        object-fit: cover;
    }

    /* 2. Limpiar fondos base */
    .stApp, .block-container {
        background-color: transparent !important;
    }

    /* 3. Estilo para el Sidebar y cajas (RECUPERANDO EL NEÓN) */
    [data-testid="stSidebar"], div[data-testid="stVerticalBlock"] {
        background-color: rgba(10, 15, 25, 0.7) !important; /* Fondo oscuro semi-transparente */
        border: 2px solid #00d4ff !important;            /* El borde neón */
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);      /* El brillo del neón */
    }

    /* 4. Textos */
    h1, h2, h3, label, p {
        color: white !important;
    }
    </style>

    <div class="video-background">
        <video autoplay loop muted playsinline>
            <source src="https://raw.githubusercontent.com/JhonAlisHarol/APLICACION-DE-PRUEBA/main/Fondo%20Animado%20De%20La%20Tierra%20Girando%20Para%20Tu%20PC.mp4" type="video/mp4">
        </video>
    </div>
    """,
    unsafe_allow_html=True
)
# --- 4. ESTADOS ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if 'lat_f' not in st.session_state: st.session_state.lat_f = ""
if 'lon_f' not in st.session_state: st.session_state.lon_f = ""

def calcular_minutos(t_inicio, t_evento):
    d1 = datetime.combine(date.today(), t_inicio)
    d2 = datetime.combine(date.today(), t_evento)
    return round((d2 - d1).total_seconds() / 60, 2)

# --- 5. INTERFAZ DE LOGIN ---
def pantalla_login():
    st.title("🔐 CENTRO DE OPERACION NACIONAL - C5")
    
    st.markdown('<p class="author">DESARROLLADO POR: [CABO 1° ELMER RODRIGUEZ]</p>', unsafe_allow_html=True)

    # Base de datos local de usuarios
    usuarios_permitidos = {
        "CONC5": "12345",
        "ALISJHON": "199432",
        "ISMAEL SAMUDIO": "20626", "DAMIAN NAVARRO": "DAMIAN26"
    }

    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        # Verificamos si el usuario existe y si la contraseña coincide
        if user in usuarios_permitidos and usuarios_permitidos[user] == password:
            st.session_state.autenticado = True
            st.session_state.usuario_actual = user  # Útil para saber quién inició sesión
            st.success(f"Bienvenido {user}")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

if not st.session_state.autenticado:
    pantalla_login()
else:
    # --- 6. DASHBOARD PRINCIPAL ---
    st.markdown('<p class="author">DESARROLLADO POR: [CABO 1° ELMER RODRIGUEZ]</p>', unsafe_allow_html=True)    
    st.title("🛡️ REGISTROS POSITIVOS DEL C.O.N - C5")
    
    m = folium.Map(location=[8.9824, -79.5199], zoom_start=12)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Hybrid').add_to(m)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=500, width=1300)

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
        provincia = col_loc1.selectbox("PROVINCIA", ["SELECCIONAR", "BOCAS DEL TORO", "COCLÉ", "COLÓN", "CHIRIQUÍ", "DARIÉN", "HERRERA", "LOS SANTOS", "PANAMÁ", "VERAGUAS", "PANAMÁ OESTE", "COMARCA GUNA YALA", "COMARCA EMBERÁ-WOUNAAN", "COMARCA NGÄBE-BUGLÉ", "COMARCA NASO TJËR DI"])
        distrito = col_loc2.selectbox("DISTRITO", ["SELECCIONAR", "AGUADULCE", "ALANJE", "ALMIRANTE", "ANTÓN", "ARRAIJÁN", "ATALAYA", "BALBOA", "BARÚ", "BESIKÓ", "BOCAS DEL TORO", "BOQUERÓN", "BOQUETE", "BUGABA", "CALOBRE", "CAÑAZAS", "CAPIRA", "CÉMACO", "CHAGRES", "CHAME", "CHANGUINOLA", "CHEPIGANA", "CHEPO", "CHIMÁN", "CHIRIRQUÍ GRANDE", "CHITRÉ", "COLÓN", "DAVID", "DOLEGA", "DONOSO", "GUALACA", "GUARARÉ", "JIRONDAI", "KANKINTÚ", "KUSAPÍN", "LA CHORRERA", "LA MESA", "LA PINTADA", "LAS MINAS", "LAS PALMAS", "LAS TABLAS", "LOS POZOS", "LOS SANTOS", "MACARACAS", "MARIATO", "MIRONÓ", "MONTIJO", "MÜNA", "NASO TJËR DI", "NATÁ", "NOLE DÜIMA", "ÑÜRÜM", "OCÚ", "OLÁ", "OMAR TORRIJOS HERRERA", "PANAMÁ", "PARITA", "PEDASÍ", "PENONOMÉ", "PESÉ", "PINOGANA", "POCRÍ", "PORTOBELO", "REMEDIOS", "RENACIMIENTO", "RÍO DE JESÚS", "SAMBÚ", "SAN CARLOS", "SAN FÉLIX", "SAN FRANCISCO", "SAN LORENZO", "SAN MIGUELITO", "SANTA CATALINA O CALOVÉBORA", "SANTA FE (DARIÉN)", "SANTA FE (VERAGUAS)", "SANTA ISABEL", "SANTA MARÍA", "SANTIAGO", "SONÁ", "TABOGA", "TIERRAS ALTAS", "TOLÉ", "TONOSÍ"])
        corregimiento = col_loc3.selectbox("CORREGIMIENTO", ["SELECCIONAR", "24 DE DICIEMBRE", "ACHIOTE", "AGUA BUENA", "AGUA DE SALUD", "AGUA FRÍA", "AILIGANDÍ", "ALANJE", "ALCALDE DÍAZ", "ALMIRANTE", "ALTO BILINGÜE", "ALTO BOQUETE", "ALTO CABALLERO", "ALTO DE JESÚS", "ALTOS DE GÜERA", "AMADOR", "AMELIA DENIS DE ICAZA", "AGUADULCE", "ANCÓN", "ANTÓN", "ARENAS", "ARNULFO ARIAS", "AROSEMENA", "ARRAIJÁN", "ASERRÍO DE GARICHÉ", "ATALAYA", "BACO", "BÁGALA", "BAHÍA AZUL", "BAHÍA HONDA", "BAJO BOQUETE", "BAJO CEDRO", "BAJO CORRAL", "BAJO CULUBRE", "BAJOS DE GÜERA", "BAKAMA", "BARNIZAL", "BARRANCO ADENTRO", "BARRIADA 4 DE ABRIL", "BARRIADA GUAYMÍ", "BARRIO BALBOA", "BARRIO COLÓN", "CAÑAVERAL", "BARRIO FRANCÉS", "BARRIO NORTE", "BARRIO SUR", "BARRIOS UNIDOS", "BASTIMENTOS", "BAYANO", "BEJUCO", "BELISARIO FRÍAS", "BELISARIO PORRAS", "BELLA VISTA", "BETANIA", "BIJAGUAL", "BISIRA", "BISVALLES", "BOCA CHICA", "BOCA DE BALSA", "BOCA DE CUPE", "BOCA DE TUCUÉ", "BOCA DEL DRAGO", "BOCA DEL MONTE", "BOCAS DEL TORO", "BONYIK", "BOQUERÓN", "BORÓ", "BREÑÓN", "BRUJAS", "BUENA VISTA", "BUENOS AIRES", "BUGABA", "BURÍ", "BURUNGA", "CABALLERO", "CABUYA", "CACIQUE", "CAIMITILLO", "CAIMITO", "CALANTE", "CALDERA", "CALIDONIA", "CALOBRE", "CALOVÉBORA", "CAMARÓN ARRIBA", "CAMBUTAL", "CAMOGANTÍ", "CAMPANA", "CANDELARIO OVALLE", "CANTA GALLO", "CANTO DEL LLANO", "CAÑAS", "CAÑAS GORDAS", "CAÑAVERAL", "CAÑAZAS", "CAÑITA", "CAPELLANÍA", "CAPIRA", "CARLOS SANTANA ÁVILA", "CASCABEL", "CATIVÁ", "CATIVÉ", "CATORCE DE NOVIEMBRE", "CAUCHERO", "CÉBACO", "CEIBA", "CERMEÑO", "CERRO BANCO", "CERRO CAÑA", "CERRO DE CASA", "CERRO DE PLATA", "CERRO IGLESIAS", "CERRO LARGO", "CERRO PATENA", "CERRO PELADO", "CERRO PUERCO", "CERRO PUNTA", "CERRO SILVESTRE", "CERRO VIEJO", "CHAME", "CHANGUINOLA", "CHEPIGANA", "CHEPILLO", "CHEPO", "CHICÁ", "CHICHICA", "CHIGUIRÍ ARRIBA", "CHILIBRE", "CHIMÁN", "CHIRIQUÍ", "CHIRIQUÍ GRANDE", "CHITRA", "CHITRÉ", "CHUMICAL", "CHUPÁ", "CHUPAMPA", "CIRÍ DE LOS SOTOS", "CIRÍ GRANDE", "CIRICITO", "CIRILO GUAYNORA", "COCHEA", "COCHIGRO", "COCLÉ", "COCLÉ DEL NORTE", "COLÓN CRISTÓBAL ESTE", "CORDILLERA", "COROZAL", "CORRAL FALSO", "COSTA HERMOSA", "CRISTÓBAL", "CRISTÓBAL ESTE", "CUANGO", "DOS RÍOS", "EDWIN FÁBREGA", "EL ALTO", "EL ARADO", "EL AROMILLO", "EL BALE", "EL BARRERO", "EL BARRITO", "EL BEBEDERO", "EL BONGO", "EL CACAO", "EL CALABACITO", "EL CAÑAFÍSTULO", "EL CAÑO", "EL CAPURÍ", "EL CARATE", "EL CEDRO", "EL CHIRÚ", "EL CHORRILLO", "EL CIRUELO", "EL COCAL", "EL COCLA", "EL COCO", "EL COPÉ", "EL CORTEZO", "EL CRISTO", "EL CUAY", "EL EJIDO", "EL EMPALME", "EL ESPINAL", "EL ESPINO", "EL GUABO", "EL GUÁSIMO", "EL HARINO", "EL HATO", "EL HATO DE SAN JUAN DE DIOS", "EL HIGO", "EL LÍBANO", "EL LIMÓN", "EL LLANO", "EL MACANO", "EL MANANTIAL", "EL MARAÑÓN", "EL MARÍA", "EL MUÑOZ", "EL NANCITO", "EL PÁJARO", "EL PALMAR", "EL PANTANO", "EL PAREDÓN", "EL PEDREGOSO", "EL PEÑÓN", "EL PICACHO", "EL PICADOR", "EL PIRO", "EL PIRO N°2", "EL PORVENIR", "EL POTRERO", "EL PRADO", "EL PUERTO", "EL REAL DE SANTA MARÍA", "EL RETIRO", "EL RINCÓN", "EL ROBLE", "EL SESTEADERO", "EL SILENCIO", "EL TEJAR", "EL TERIBE", "EL TIJERA", "EL TORO", "EL VALLE", "EMPLANADA DE CHORCHA", "ENTRADERO DEL CASTILLO", "ERNESTO CÓRDOBA CAMPOS", "ESCOBAL", "ESPINO AMARILLO", "FEUILLET", "FINCA 12", "FINCA 30", "FINCA 4", "FINCA 51", "FINCA 6", "FINCA 60", "FINCA 66", "FLORES", "GAIGIRGORDUB", "GARACHINÉ", "GARROTE", "GATUNCITO", "GOBEA", "GOBERNADORA", "GÓMEZ", "GONZALO VÁSQUEZ", "GUABAL", "GUABITO", "GUACÁ", "GUADALUPE", "GUALACA", "GUÁNICO", "GUARARÉ", "GUARARÉ ARRIBA", "GUARIVIARA", "GUARUMAL", "GUAYABAL", "GUAYBITO", "GÜIBALE", "GUORONÍ", "GUZMÁN", "HATO CHAMÍ", "HATO COROTÚ", "HATO CULANTRO", "HATO JOBO", "HATO JULÍ", "HATO PILÓN", "HERRERA", "HICACO", "HORCONCITOS", "HORNITO", "HURTADO", "ISLA DE CAÑAS", "ISLA GRANDE", "ITURRALDE", "JÄDEBERI", "JAQUÉ", "JARAMILLO", "JINGURUDÓ", "JOSÉ DOMINGO ESPINAR", "JUAN DEMÓSTENES AROSEMENA", "JUAN DÍAS", "JUAY", "JUSTO FIDEL PALACIOS", "KANKINTÚ", "KIKARI", "KRÜA", "KUSAPÍN", "LA ARENA", "LA CARRILLO", "LA COLORADA", "LA CONCEPCIÓN", "LA ENCANTADA", "LA ENEA", "LA ENSENADA", "LA ERMITA", "LA ESMERALDA", "LA ESPIGADILLA", "LA ESTRELLA", "LA GARCEANA", "LA GLORIA", "LA GUINEA", "LA LAGUNA", "LA LAJA", "LA MESA", "LA MIEL", "LA MONTAÑUELA", "LA PALMA", "LA PASERA", "LA PAVA", "LA PEÑA", "LA PINTADA", "LA PITALOZA", "LA RAYA DE CALOBRE", "LA RAYA DE SANTA MARÍA", "LA REPRESA", "LA SOLEDAD", "LA TETILLA", "LA TIZA", "LA TRINCHERA", "LA TRINIDAD", "LA TRONOSA", "LA VILLA DE LOS SANTOS", "LA YEGUADA", "LAJAMINA", "LAJAS ADENTRO", "LAJAS BLANCAS", "LAJAS DE TOLÉ", "LAJERO", "LAS CABRAS", "LAS CRUCES", "LAS CUMBRES", "LAS DELICIAS", "LAS GARZAS", "LAS GUABAS", "LAS GUÍAS", "LAS HUACAS", "LAS LAJAS", "LAS LLANAS", "LAS LOMAS", "LAS MAÑANITAS", "LAS MARGARITAS", "LAS MINAS", "LAS OLLAS ARRIBA", "LAS PALMAS", "LAS PALMITAS", "LAS TABLAS", "LAS TABLAS ABAJO", "LAS TRANCAS", "LAS UVAS", "LEONES", "LÍDICE", "LIMÓN", "LIMONES", "LLANO ABAJO", "LLANO BONITO", "LLANO DE LA CRUZ", "LLANO DE PIEDRAS", "LLANO GRANDE", "LLANO LARGO", "LLANO NORTE", "LOLÁ", "LOMA YUCA", "LOS ALGARROBOS", "LOS ANASTACIOS", "LOS ÁNGELES", "LOS ASIENTOS", "LOS CANELOS", "LOS CASTILLOS", "LOS CERRITOS", "LOS CERROS DE PAJA", "LOS DÍAZ", "LOS HATILLOS", "LOS LLANITOS", "LOS LLANOS", "LOS MILAGROS", "LOS NARANJOS", "LOS OLIVOS", "LOS POZOS", "LOS VALLES", "MACARACAS", "MADUGANDÍ", "MAN CREEK", "MANACA", "MANUEL E. AMADOR TERRERO", "MANUEL ORTEGA", "MARACA", "MARÍA CHIQUITA", "MARIABÉ", "MARIATO", "MATEO ITURRALDE", "MENCHACA", "MENDOZA", "METETÍ", "MIGUEL DE LA BORDA", "MIRAFLORES", "MIRAMAR", "MOGOLLÓN", "MONAGRILLO", "MONJARÁS", "MONTE LIRIO", "MONTIJO", "MREENI", "MÜNÜNÍ", "NÄMNONÍ", "NANCE DE RISCÓ", "NARGANÁ", "NATÁ", "NIBA", "NIBRA", "NOMBRE DE DIOS", "NUARIO", "NUEVA CALIFORNIA", "NUEVA ESPERANZA", "NUEVA GORGONA", "NUEVA PROVIDENCIA", "NUEVO CHAGRES", "NUEVO EMPERADOR", "NUEVO MÉXICO", "NUEVO SANTIAGO", "OBALDÍA", "OCÚ", "OLÁ", "OMAR TORRIJOS", "ORIA ARRIBA", "OTOQUE OCCIDENTE", "OTOQUE ORIENTE", "PACORA", "PAJA DE SOMBRERO", "PAJONAL", "PALENQUE", "PALMAS BELLAS", "PALMIRA", "PALO GRANDE", "PARAÍSO", "PARÍS", "PARITA", "PARITILLA", "PARQUE LEFEVRE", "PÁSIGA", "PASO ANCHO", "PAYA", "PEDASÍ", "PEDREGAL", "PEDRO GONZÁLEZ", "PENONOMÉ", "PEÑA BLANCA", "PEÑAS CHATAS", "PERALES", "PESÉ", "PIEDRA ROJA", "PIEDRAS GORDAS", "PILÓN", "PINOGANA", "PIÑA", "PIXVAE", "PLAYA CHIQUITA", "PLAYA LEONA", "PLAZA DE CAISÁN", "POCRÍ", "PONUGA", "PORTOBELILLO", "PORTOBELO", "POTRERILLOS", "POTRERILLOS ABAJO", "POTRERO DE CAÑA", "POTUGA", "PROGRESO", "PÚCURO", "PUEBLO NUEVO", "PUEBLOS UNIDOS", "PUERTO ARMUELLES", "PUERTO CAIMITO", "PUERTO INDIO", "PUERTO OBALDÍA", "PUERTO PILÓN", "PUERTO PIÑA", "PUERTO VIDAL", "PUNTA CHAME", "PUNTA LAUREL", "PUNTA PEÑA", "PUNTA ROBALO", "PURIO", "QUEBRADA DE LORO", "QUEBRADA DE ORO", "QUEBRADA DE PIEDRA", "QUEBRADA DEL ROSARIO", "QUEBRADA EL CIPRIÁN", "QUEBRO", "QUERÉVALO", "RAMBALA", "REMANCE", "REMEDIOS", "RIECITO", "RINCÓN", "RINCÓN HONDO", "RÍO ABAJO", "RÍO CHIRIQUÍ", "RÍO CONGO", "RÍO CONGO ARRIBA", "RÍO DE JESÚS", "RÍO GRANDE", "RÍO HATO", "RÍO HONDO", "RÍO IGLESIAS", "RÍO INDIO", "RÍO LUIS", "RÍO SABALO", "RÍO SERENO", "RODEO VIEJO", "RODOLFO AGUILAR DELGADO", "RODRIGO LUQUE", "ROKA", "ROVIRA", "RUBÉN CANTÚ", "RUFINA ALFARO", "SABANAGRANDE", "SABANITAS", "SABOGA", "SAJALICES", "SALAMANCA", "SALTO DUPÍ", "SALUD", "SAMBOA", "SAMBÚ", "SAN ANDRÉS", "SAN ANTONIO", "SAN BARTOLO", "SAN CARLOS", "SAN CRISTÓBAL", "SAN FELIPE", "SAN FÉLIX", "SAN FRANCISCO", "SAN ISIDRO", "SAN JOSÉ", "SAN JOSÉ DEL GENERAL", "SAN JUAN", "SAN JUAN BAUTISTA", "SAN JUAN DE DIOS", "SAN JUAN DE TURBE", "SAN LORENZO", "SAN MARCELO", "SAN MARTÍN", "SAN MARTÍN DE PORRES", "SAN MIGUEL", "SAN PABLO NUEVO", "SAN PABLO VIEJO", "SAN PEDRITO", "SAN PEDRO DEL ESPINO", "SAN SAN DRUI", "SANTA ANA", "SANTA CATALINA", "SANTA CLARA", "SANTA CRUZ", "SANTA CRUZ DE CHININA", "SANTA FE", "SANTA ISABEL", "SANTA LUCÍA", "SANTA MARÍA", "SANTA MARTA", "SANTA RITA", "SANTA ROSA", "SANTIAGO", "SANTIAGO ESTE", "SANTIAGO SUR", "SANTO DOMINGO", "SANTO TOMÁS", "SETEGANTÍ", "SIEYIC", "SITIO PRADO", "SOLANO", "SOLOY", "SONÁ", "SORÁ", "SORTOVÁ", "SUSAMA", "TABOGA", "TAIMATÍ", "TEBARIO", "TIERRA OSCURA", "TIJERAS", "TINAJAS", "TOABRÉ", "TOBOBÉ", "TOCUMEN", "TOCUMEN TOCUMEN TOLE", "TOLOTE", "TONOSÍ", "TORTÍ", "TOZA", "TRES QUEBRADAS", "TUBUALÁ", "TUCUTÍ", "TULÚ", "TUWAI", "UMANÍ", "UNIÓN CHOCÓ", "UNIÓN DEL NORTE", "UNIÓN SANTEÑA", "URRACÁ", "UTIRA", "VACAMONTE", "VALLE BONITO", "VALLE DE AGUAS ARRIBA", "VALLE DE RISCÓ", "VALLE RICO", "VALLERRIQUITO", "VELADERO", "VERACRUZ", "VICTORIANO LORENZO", "VIENTO FRÍO", "VIGUÍ", "VILLA CARMEN", "VILLA LOURDES", "VILLA ROSARIO", "VILLARREAL", "VIRGEN DEL CARMEN", "VISTA ALEGRE", "VOLCÁN", "WARGANDÍ", "YAPE", "YAVIZA", "ZAPALLAL", "ZAPOTILLO"])
        
        col_loc4, col_loc5, col_loc6 = st.columns(3)
        referencia = col_loc4.text_input("REFERENCIA")
        zp_policial = col_loc5.selectbox("ZP POLICIALES / ENLACE", ["SELECCIONAR", "3RA ZP COLON", "4TA ZP CHIRIQUI"])
        recursos = col_loc6.selectbox("RECURSOS", ["SELECCIONAR", "PATRULLA", "LINCE", "CICLISTA"])

        st.subheader("⏱️ Tiempos, Unidades y Cámaras")
        c1, c2, c3, c4 = st.columns(4)
        fecha = c1.date_input("FECHA")
        centro_mando = c1.selectbox("CENTRO DE MANDO", ["SELECCIONAR", "CON", "CORCOL", "COMCH", "COMAR", "COMDA", "COMCHEP", "CEVIBO", "COMSAM"])
        unidad_vv = c1.selectbox("UNIDAD DE VV/104", ["SELECCIONAR", "ELMER RODRIGUEZ"])
        canal = c2.selectbox("CANAL DE ENTRADA", ["SELECCIONAR", "CLL-104", "VIDEO-VIGILANCIA", "BOTON DE PANICO", "RADIO FRECUENCIA"])
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
        lista_maestra_a = ["SELECCIONAR", "ACCIDENTE DE TRANSITO", "ACCIDENTES", "ALERTAS"]
        lista_maestra_b = ["SELECCIONAR", "PERSONAS EN ACTITUD INUSUAL", "VEHICULO SOSPECHOSO", "COLISION MENOR"]
        c8, c9 = st.columns(2)
        tipo_inc = c8.selectbox("TIPO DE INCIDENTES", lista_maestra_a)
        subtipo_inc = c9.selectbox("SUBTIPO DE INCIDENTES", lista_maestra_b)

        # --- AQUI VA EL BLOQUE NUEVO ---
        vehiculos_verificados = 0
        personas_verificadas = 0

        if modo == "PREVENTIVO":
            st.subheader("🛡️ Detalles Preventivos")
            col_v, col_p = st.columns(2)
            vehiculos_verificados = col_v.number_input("VEHICULOS VERIFICADOS", min_value=0, step=1)
            personas_verificadas = col_p.number_input("PERSONAS VERIFICADAS", min_value=0, step=1)
        # ------------------------------

        cierre_tipo, cierre_subtipo = "N/A", "N/A"
        p1, p2, p3, p4, p5, p6 = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        # --- BLOQUE DE POSITIVOS ---
        if modo == "POSITIVO":
            c_cierre1, c_cierre2 = st.columns(2)
            cierre_tipo = c_cierre1.selectbox("CIERRE TIPO", lista_maestra_a)
            cierre_subtipo = c_cierre2.selectbox("CIERRE SUBTIPO", lista_maestra_b)
            
            # Definimos la lista una sola vez para los 6 campos
            lista_pos = ["SELECCIONAR", "APOYO AL CIUDADANO", "CIUDADANO APREHENDIDO POR OFICIO DE CONDUCCIÓN", "CIUDADANO APREHENDIDO POR OFICIO DE CAPTURA"]
            
            st.write("Selección de Categorías:")
            
            # Fila 1: P1, P2, P3
            cols_top = st.columns(3)
            p1 = cols_top[0].selectbox("P1", lista_pos)
            p2 = cols_top[1].selectbox("P2", lista_pos)
            p3 = cols_top[2].selectbox("P3", lista_pos)
            
            # Fila 2: P4, P5, P6
            cols_bottom = st.columns(3)
            p4 = cols_bottom[0].selectbox("P4", lista_pos)
            p5 = cols_bottom[1].selectbox("P5", lista_pos)
            p6 = cols_bottom[2].selectbox("P6", lista_pos)

        narrativa = st.text_input("REPORTE/NARRATIVA")
        link_video = st.text_input("ENLACE DE VÍDEO")
        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            # --- VALIDACIÓN ESTRICTA ---
            campos_faltantes = []
            if provincia == "SELECCIONAR": campos_faltantes.append("Provincia")
            if distrito == "SELECCIONAR": campos_faltantes.append("Distrito")
            if corregimiento == "SELECCIONAR": campos_faltantes.append("Corregimiento")
            if zp_policial == "SELECCIONAR": campos_faltantes.append("ZP Policial")
            if recursos == "SELECCIONAR": campos_faltantes.append("Recursos")
            if centro_mando == "SELECCIONAR": campos_faltantes.append("Centro de Mando")
            if unidad_vv == "SELECCIONAR": campos_faltantes.append("Unidad VV/104")
            if canal == "SELECCIONAR": campos_faltantes.append("Canal de Entrada")
            if unidad_despacho == "SELECCIONAR": campos_faltantes.append("Unidad de Despacho")
            if tipo_inc == "SELECCIONAR": campos_faltantes.append("Tipo de Incidente")
            if subtipo_inc == "SELECCIONAR": campos_faltantes.append("Subtipo de Incidente")
            if not camara_id.strip(): campos_faltantes.append("ID Cámara")
            if not narrativa.strip(): campos_faltantes.append("Narrativa")
            if not link_video.strip(): campos_faltantes.append("Enlace de Video")
            if not st.session_state.lat_f: campos_faltantes.append("Ubicación en el Mapa") 

            # . VALIDACIÓN DE MODO POSITIVO ---
            if modo == "POSITIVO":
                if cierre_tipo == "SELECCIONAR": campos_faltantes.append("Cierre Tipo")
                if cierre_subtipo == "SELECCIONAR": campos_faltantes.append("Cierre Subtipo")
                if p1 == "SELECCIONAR": campos_faltantes.append("P1")
            
            if campos_faltantes:
                st.error(f"❌ Faltan datos obligatorios: {', '.join(campos_faltantes)}")
            else:
                nuevo_registro = {
                    "MODO": modo,
                    "FECHA_EVENTO": str(fecha),
                    "PROVINCIA": provincia, "DISTRITO": distrito, "CORREGIMIENTO": corregimiento,
                    "REFERENCIA": referencia, "ZP_POLICIAL": zp_policial, "RECURSOS": recursos,
                    "FECHA_HORA": datetime.now(pytz.timezone('America/Panama')).strftime("%Y-%m-%d %H:%M:%S"),
                    "CENTRO_DE_MANDO": centro_mando, "UNIDAD_VV": unidad_vv, "CANAL_ENTRADA": canal,
                    "UNIDAD_DESPACHO": unidad_despacho, "T_INICIAL": str(t_inicial), "H_DESPACHO": str(h_despacho),
                    "CAMARA_ID": camara_id, "H_ATENCION": str(h_atencion), "H_CIERRE": str(h_cierre),
                    "TIPO_INCIDENTE": tipo_inc, "SUBTIPO_INCIDENTE": subtipo_inc, "CIERRE_TIPO": cierre_tipo,
                    "CIERRE_SUBTIPO": cierre_subtipo, "P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6,
                    "NARRATIVA": narrativa, "LINK_VIDEO": link_video, "LATITUD": str(st.session_state.lat_f),
                    "LONGITUD": str(st.session_state.lon_f), "VARIANZA_DESPACHO": v_despacho,
                    "VARIANZA_ATENCION": v_atencion, "VARIANZA_CIERRE": v_cierre,
                    "VEHICULOS_VERIFICADOS": vehiculos_verificados,
                    "PERSONAS_VERIFICADAS": personas_verificadas
                }
                try:
                    supabase.table("registros_c5").insert(nuevo_registro, returning='minimal').execute()
                    st.success("✔️ Registro guardado con éxito.")
                       
                except Exception as e:
                    st.error(f"Error: {e}")

   # --- 7. BARRA LATERAL (Sidebar) ---
with st.sidebar:
    # 1. Mostrar usuario
    if st.session_state.get("autenticado", False):
        st.write(f"👤 Operador: **{st.session_state.get('usuario_actual', 'Usuario')}**")
        
        # 2. Reloj en tiempo real
        st.subheader("🕒 Hora Actual")
        reloj_placeholder = st.empty()
        
        # Inyectamos un pequeño script de JavaScript para que el reloj avance solo
        # sin recargar la página completa.
        import streamlit.components.v1 as components
        
        components.html(
            """
            <div id="reloj" style="font-size: 24px; font-weight: bold; color: #F4FF00;"></div>
            <script>
                function actualizarReloj() {
                    const ahora = new Date();
                    const opciones = { timeZone: 'America/Panama', hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' };
                    document.getElementById('reloj').innerText = ahora.toLocaleTimeString('es-PA', opciones);
                }
                setInterval(actualizarReloj, 1000);
                actualizarReloj();
            </script>
            """,
            height=40
        )
        
        # 3. Botón de Cerrar Sesión (Ahora es totalmente estable)
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.usuario_actual = None 
            st.rerun()
