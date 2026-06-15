import plotly.express as px
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import os

# =====================================================================
# 🗃️ CARGA DEL GLOSARIO REAL DE AERONAVES (Para usar la columna hyperlink)
# =====================================================================
# Leemos tu CSV de glosario. Asegúrate de que la ruta del archivo es correcta en tu PC.
try:
    df_gloss_maestro = pd.read_csv("../data/3_thor_wwii_aircraft_gloss.csv")
    # Limpiamos espacios raros en los nombres de las columnas por si acaso
    df_gloss_maestro.columns = df_gloss_maestro.columns.str.strip()
except Exception:
    df_gloss_maestro = pd.DataFrame() # Copia de seguridad por si acaso falla

def mostrar_tarjeta_avion(nombre_avion):
    """
    Función global definitiva. Cruza el nombre del avión directamente con 
    la columna 'aircraft' de tu CSV para extraer el 'hyperlink' real.
    """
    # 🔄 El parche de traducción que ya tenías para MED, LGT y GB24
    traducciones = {"GB24": "B-24", "MED": "B-25", "LGT": "A-20", "GB17": "B-17", "SB17": "B-17"}
    nombre_corregido = traducciones.get(nombre_avion, nombre_avion)

    # 🧼 Tu lógica de siempre que funciona de maravilla para cargar las fotos locales
    nombre_gloss_id = str(nombre_corregido).strip().replace("-", "").replace(" ", "").lower()
    ruta_foto = f"images/fotos_aviones/{nombre_gloss_id}.jpg"
    
    # 1. Pintar la Imagen Local (Tu parte sagrada)
    if os.path.exists(ruta_foto):
        st.image(ruta_foto, caption=f"Modelo: {nombre_avion}", use_container_width=True)
    else:
        st.info(f"📁 Guardar como: `{nombre_gloss_id}.jpg` en /fotos_aviones")
    
    # 2. 🌐 EXTRAER EL ENLACE REAL DE LA COLUMNA 'hyperlink'
    # Empezamos asumiendo que no hay link por si acaso fallara la lectura física del archivo
    link_web = None
    
    try:
        ruta_csv_glosario = "../data/3_thor_wwii_aircraft_gloss.csv"
        
        if os.path.exists(ruta_csv_glosario):
            df_gloss_maestro = pd.read_csv(ruta_csv_glosario)
            # Limpiamos posibles espacios en los títulos de las columnas
            df_gloss_maestro.columns = df_gloss_maestro.columns.str.strip()
            
            # 🔥 LA MAGIA DIRECTA:
            # Limpiamos la columna 'aircraft' del CSV igual que hicimos con tu foto (ej: 'B-17' -> 'b17')
            nombres_csv_limpios = df_gloss_maestro["aircraft"].astype(str).str.strip().str.replace("-", "").str.replace(" ", "").str.lower()
            
            # Buscamos la fila exacta comparando ambos textos ya homogeneizados
            fila = df_gloss_maestro[nombres_csv_limpios == nombre_gloss_id]
            
            # Si encuentra la fila y el hyperlink es válido, lo extraemos
            if not fila.empty and pd.notna(fila["hyperlink"].values[0]):
                link_web = str(fila["hyperlink"].values[0]).strip()
    except Exception:
        pass  # Si el CSV diera un error raro de permisos, pasa de largo para no colapsar la app
    
    # 3. Pintar el botón web solo si hemos conseguido extraer el link real de tu dataset
    if link_web:
        st.link_button(f"🌐 Más info sobre {nombre_avion}", link_web, use_container_width=True)
    else:
        # Si un avión raro no tuviera link en el CSV, te avisa elegantemente sin romper nada
        st.warning(f"⚠️ Sin enlace disponible para {nombre_avion} en el glosario.")

# -----------------------------
# CONFIGURACIÓN BÁSICA
# -----------------------------
st.set_page_config(
    page_title="WWII Bombing Dashboard",
    page_icon="✈️",
    layout="wide"
)

# -----------------------------
# TÍTULO PRINCIPAL
# -----------------------------
st.title("WWII Bombing Analysis – Interactive App")
st.markdown("### Complemento web del dashboard de Power BI")

# -----------------------------
# MENÚ LATERAL
# -----------------------------
menu = st.sidebar.radio(
    "Navegación",
    [
        "📌 Introducción",
        "🗺️ Panorama 1943–44",
        "🔥 1–5 Junio 1944",
        "⚔️ Día D (6 Junio 1944)",
        "📷 Galería Histórica",
        "⚠️ Sesgos del Dataset",
        "📉 Pérdidas y Contexto",
        "📁 Enlaces del Proyecto"
    ]
)

# -----------------------------
# SECCIONES
# -----------------------------
if menu == "📌 Introducción":
    st.header("Introducción")

    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        st.image("wwii_streamlit/images/introduccion.jpg", use_container_width=True)

    st.markdown("""
    Este proyecto combina análisis histórico, visualización de datos y narrativa arqueológica
    para identificar zonas con alta probabilidad de contener restos materiales derivados de los
    bombardeos aliados entre 1943 y 1944.

    La aplicación complementa el dashboard de Power BI con:
    - 📊 Visualizaciones interactivas adicionales
    - 🗺️ Mapas y contexto histórico
    - 📷 Fotografías reales de la época
    - ⚠️ Sección de sesgos y limitaciones del dataset
    - 📉 Contexto sobre pérdidas humanas y materiales
    """)

elif menu == "🗺️ Panorama 1943–44":
    st.header("Panorama 1943–1944")

    # 1. CARGA DE DATOS ORIGINALES DE BOMBARDEOS
    df = pd.read_csv("../adi_master_1943_1944_CLEAN.csv")
    
    # Aseguramos formato numérico en la columna de peso para evitar errores
    df["Total Weight (Tons)"] = pd.to_numeric(df["Total Weight (Tons)"], errors="coerce").fillna(0)

    # LIMPIEZA DE TEXTOS CRUCIAL
    df["Target City"] = df["Target City"].fillna("Desconocida").astype(str).str.strip()
    df["Aircraft Series"] = df["Aircraft Series"].fillna("Desconocido").astype(str).str.strip()
    df["Target Country"] = df["Target Country"].fillna("Desconocido").astype(str).str.strip()

    # 2. CÁLCULO DE KPIs REALES (Sobre el 100% de los datos)
    total_misiones = df["Mission ID"].nunique()
    total_toneladas = df["Total Weight (Tons)"].sum()
    promedio_toneladas = df["Total Weight (Tons)"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Misiones registradas", f"{total_misiones:,}")
    col2.metric("Toneladas lanzadas", f"{total_toneladas:,.0f}")
    col3.metric("Promedio por misión", f"{promedio_toneladas:,.2f}")

    # 3. CREAMOS UN DATAFRAME EXCLUSIVO PARA EL MAPA
    df_mapa = df.dropna(subset=["Target Latitude", "Target Longitude"]).copy()
    df_mapa["Target Latitude"] = pd.to_numeric(df_mapa["Target Latitude"], errors="coerce")
    df_mapa["Target Longitude"] = pd.to_numeric(df_mapa["Target Longitude"], errors="coerce")
    df_mapa = df_mapa.dropna(subset=["Target Latitude", "Target Longitude"])

    # 4. PREPARACIÓN DEL MAPA DE FOLIUM
    st.subheader("Mapa interactivo de bombardeos (1943–44)")
    
    df_resumen = df_mapa.groupby("Target City").agg({
        "Target Latitude": "first",
        "Target Longitude": "first",
        "Mission ID": "count",
        "Total Weight (Tons)": "sum"
    }).reset_index()

    df_resumen = df_resumen.rename(columns={"Mission ID": "Total Bombardeos"})

    coordenadas_centro = [46.2276, 2.2137]
    m = folium.Map(location=coordenadas_centro, zoom_start=5, control_scale=True)

    for idx, row in df_resumen.iterrows():
        radio_burbuja = min(4 + (row["Total Bombardeos"] * 0.3), 30)
        color_burbuja = "#D32F2F" if row["Total Bombardeos"] > 10 else "#F57C00"

        texto_flotante = f"""
        <div style="font-family: sans-serif; font-size: 12px; min-width: 180px;">
            <h4 style="margin: 0 0 5px 0; color: #1E88E5;">📍 {row['Target City']}</h4>
            <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ccc;">
            <strong>💥 Total Ataques:</strong> {row['Total Bombardeos']}<br>
            <strong>⚖️ Toneladas:</strong> {row['Total Weight (Tons)']:,.1f} Tons
        </div>
        """

        folium.CircleMarker(
            location=[row["Target Latitude"], row["Target Longitude"]],
            radius=radio_burbuja,
            color=color_burbuja,
            fill=True,
            fill_color=color_burbuja,
            fill_opacity=0.5,
            tooltip=texto_flotante
        ).add_to(m)

    st_folium(m, width=1100, height=550, key="mapa_panorama_final")

    st.markdown("---")

    # 5. BUSCADOR DINÁMICO
    st.subheader("🔍 Panel de Inspección Operativa")
    
    lista_ciudades = sorted(df_resumen["Target City"].unique())
    ciudad_seleccionada = st.selectbox(
        "Buscar objetivo histórico:",
        lista_ciudades,
        index=None,
        placeholder="Escribe una ciudad (ej. Tours, Caen, Paris)..."
    )

    # 6. DESPLIEGUE DE DATOS Y FOTOS LOCALES
    if ciudad_seleccionada:
        df_detalle_ciudad = df_mapa[df_mapa["Target City"] == ciudad_seleccionada]

        if not df_detalle_ciudad.empty:
            st.success(f"### 📊 Historial Operativo Desclasificado: {ciudad_seleccionada}")

            col_b1, col_b2 = st.columns(2)
            col_b1.metric("Misiones registradas", f"{len(df_detalle_ciudad)} bombardeos")
            col_b2.metric("Masa de explosivos", f"{df_detalle_ciudad['Total Weight (Tons)'].sum():,.1f} Toneladas")

            st.markdown("#### 🎯 Desglose Táctico de Objetivos:")
            
            col_objetivo = "Target Industry" if "Target Industry" in df_detalle_ciudad.columns else "Mission Type"
            df_detalle_ciudad[col_objetivo] = df_detalle_ciudad[col_objetivo].fillna("No especificado").astype(str).str.strip()

            df_tabla_objetivos = df_detalle_ciudad.groupby([col_objetivo, "Aircraft Series"]).agg({
                "Mission ID": "count",
                "Total Weight (Tons)": "sum"
            }).reset_index()

            df_tabla_objetivos.columns = ["Sector Objetivo", "Modelo de Avión", "Cantidad de Ataques", "Toneladas Lanzadas"]
            st.dataframe(df_tabla_objetivos, use_container_width=True, hide_index=True)

        # 📸 GALERÍA LOCAL INTERACTIVA MODULAR (VERSIÓN TRIPLE BLINDAJE)
            st.markdown("---")
            st.markdown("### 📷 Inteligencia Visual y Documentación de Aeronaves")
            st.markdown("*Fotografías y expedientes históricos de los modelos que operaron en esta zona:*")
            
            # Sacamos los aviones únicos de esta ciudad y quitamos nulos o vacíos
            aviones_en_ciudad = [a for a in df_detalle_ciudad["Aircraft Series"].unique() if pd.notna(a) and str(a).strip() != ""]
            
            # 🚨 CONTROL DE SEGURIDAD: Solo dibujamos si la lista tiene aviones
            if len(aviones_en_ciudad) > 0:
                # Creamos las columnas según los aviones reales que haya
                columnas_fotos = st.columns(len(aviones_en_ciudad))
                
                for i, avion in enumerate(aviones_en_ciudad):
                    with columnas_fotos[i]:
                        # Invocamos a nuestra función global corregida
                        mostrar_tarjeta_avion(avion)
            else:
                st.warning("⚠️ No se han detectado modelos de aeronaves registrados para los bombardeos de esta ciudad.")

# =====================================================================
# 📊 SECCIÓN DE CIERRE: INTEGRACIÓN CON POWER BI (Ecosistema Analítico)
# =====================================================================
    st.markdown("---")
    st.markdown("### 📊 Ecosistema de Inteligencia de Datos (Conexión Analítica)")
            
            # Usamos un contenedor visual moderno para separar esta sección teórica
    with st.container(border=True):
                st.markdown(
                    "💡 **Nota de Arquitectura:** Esta aplicación web en **Streamlit (Python)** "
                    "está diseñada específicamente para la exploración interactiva sobre mapas, "
                    "búsquedas tácticas por ciudad y documentación fotográfica local en tiempo real."
                )
                st.markdown(
                    "Para el análisis estadístico global (patrones temporales, correlación de tonelajes "
                    "totales y rendimiento de flotas a gran escala), el proyecto cuenta con un "
                    "**Cuadro de Mando Avanzado desarrollado en Power BI** (disponible en el repositorio local `.pbix`)."
                )
                
                # Simulamos el botón de BI, pero en modo informativo/deshabilitado ya que está en local
    st.button(
                    "📊 Dashboard Power BI (Ejecutar archivo local .pbix para interactuar)", 
                    disabled=True, 
                    use_container_width=True
            )


#-------------------------------------------

# =====================================================================
# 🔥 1–5 JUNIO 1944: BOMBARDEOS PREVIOS AL DÍA D
# =====================================================================
elif menu == "🔥 1–5 Junio 1944":
    st.header("🚀 Operaciones Preliminares: El Aislamiento de Normandía (1–5 Junio)")
    st.markdown(
        "Durante los primeros cinco días de junio de 1944, las fuerzas aéreas aliadas ejecutaron la "
        "**Operación Fortitude** y el Plan de Transportes. El objetivo no era atacar las playas, sino "
        "destruir las vías férreas, puentes y nudos de comunicación franceses para evitar que los alemanes "
        "enviaran refuerzos a Normandía."
    )
    
    # Intentamos filtrar dinámicamente tu dataset limpio para este periodo
    try:
        # Asegúrate de ajustar el nombre de la columna de fecha (ej: 'Mission Date' o 'Fecha')
        col_fecha = [c for c in df.columns if "date" in c.lower() or "fecha" in c.lower()][0]
        df_copia = df.copy()
        df_copia['Fecha_DT'] = pd.to_datetime(df_copia[col_fecha], errors='coerce')
        
        # Filtramos estrictamente del 1 al 5 de junio de 1944
        df_previo = df_copia[(df_copia['Fecha_DT'] >= '1944-06-01') & (df_copia['Fecha_DT'] <= '1944-06-05')]
        
        if not df_previo.empty:
            misiones_previas = len(df_previo)
            aviones_previos = df_previo["Aircraft Series"].nunique()
            
            st.info(f"📊 **Datos del Dataset en este periodo:** Se registraron **{misiones_previas} misiones** de ataque utilizando **{aviones_previos} modelos** de aviones diferentes en solo 5 días.")
            
            # Top 5 ciudades más machacadas esos días previos
            col_ciudad = [c for c in df_previo.columns if "city" in c.lower() or "ciudad" in c.lower() or "target" in c.lower()][0]
            top_ciudades = df_previo[col_ciudad].value_counts().head(5)
            
            st.write("**Principales objetivos logísticos destruidos (Top Objetivos):**")
            st.bar_chart(top_ciudades)
        else:
            st.warning("⚠️ No se encontraron misiones registradas entre el 1 y el 5 de junio en este corte del dataset.")
    except Exception:
        st.info("ℹ️ Campaña de ablandamiento estratégico: Destrucción sistemática de puentes en el Sena y el Loira.")

# =====================================================================
# ⚔️ DÍA D (6 JUNIO 1944)
# =====================================================================
elif menu == "⚔️ Día D (6 Junio 1944)":
    st.header("⚔️ El Día Más Largo: 6 de Junio de 1944")
    st.markdown(
        "El 6 de junio de 1944 arrancó la **Operación Overlord**. Miles de bombarderos pesados y medios "
        "despegaron en mitad de la noche para machacar las defensas costeras de la Muralla del Atlántico "
        "justo unos minutos antes de que las barcazas de desembarco tocaran la arena."
    )
    
    try:
        col_fecha = [c for c in df.columns if "date" in c.lower() or "fecha" in c.lower()][0]
        df_copia = df.copy()
        df_copia['Fecha_DT'] = pd.to_datetime(df_copia[col_fecha], errors='coerce')
        
        # Filtramos el día exacto
        df_diad = df_copia[df_copia['Fecha_DT'] == '1944-06-06']
        
        if not df_diad.empty:
            st.success(f"💥 **Impacto del Día D registrado:** ¡Se registran **{len(df_diad)} ataques coordinados** en el dataset para el 6 de junio!")
            
            # Qué aviones volaron ese día histórico
            aviones_diad = df_diad["Aircraft Series"].value_counts()
            st.write("**Flota aérea desplegada en el Día D (Misiones por modelo):**")
            st.bar_chart(aviones_diad)
        else:
            st.warning("⚠️ El filtro estricto del 6 de junio no devolvió filas. Revisa si las fechas de tu dataset limpio cubren este día exacto.")
    except Exception:
        st.info("ℹ️ Cobertura aérea total: Los aliados consiguieron superioridad aérea absoluta sobre las playas de desembarco.")

# =====================================================================
# 📷 GALERÍA HISTÓRICA
# =====================================================================
elif menu == "📷 Galería Histórica":
    st.header("📷 Archivo Fotográfico De Operaciones")
    st.markdown("---")
    st.markdown("*Imágenes de archivo de los bombardeos aliados en el teatro europeo (1943-1944):*")
    
    # Creamos una cuadrícula de fotos usando las fotos que tengas en tu carpeta o enlaces reales de internet
    col1, col2 = st.columns(2)
    
    with col1:
        # Intenta usar fotos reales si las tienes, o enlaces directos seguros de internet
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e1/B-17F_Forming_Up_-_GPN-2002-000018.jpg", 
                 caption="Escuadrón de Boeing B-17 Flying Fortress en formación de caja.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/4/45/B-24_Liberator_dropping_bombs.jpg", 
                 caption="Consolidated B-24 Liberator liberando su carga sobre un objetivo industrial.")
        
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/9/9d/B-29_In_Flight.jpg", 
                 caption="Boeing B-29 Superfortress ejecutando pruebas de altitud.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/d/df/Avro_Lancaster_B_I_PA474_BBMF.jpg", 
                 caption="Avro Lancaster de la RAF, pilar de los bombardeos nocturnos estratégicos.")

# =====================================================================
# ⚠️ SESGOS DEL DATASET (La autocrítica técnica que aman los tribunales)
# =====================================================================
elif menu == "⚠️ Sesgos del Dataset":
    st.header("⚠️ Sesgos, Vacíos y Limitaciones de la Base de Datos")
    st.markdown(
        "Ningún dataset histórico es perfecto. Al analizar el registro THOR de la Segunda Guerra Mundial, "
        "hemos identificado limitaciones críticas que deben tenerse en cuenta para no sesgar las conclusiones:"
    )
    
    with st.container(border=True):
        st.markdown("""
        1. **Sesgo Geográfico y Político (Predominio Angloamericano):** El dataset THOR recoge de forma masiva y excelente las misiones de la USAAF (Fuerza Aérea de EE.UU.) y la RAF (Reino Unido). Sin embargo, las operaciones del Frente Oriental (Unión Soviética) o las acciones de la Luftwaffe alemana apenas están documentadas, ofreciendo una visión parcial del conflicto global.
        2. **Falta de Estandarización en los Nombres de los Aviones:** Como hemos comprobado en el desarrollo técnico de este proyecto, existen registros con códigos militares anómalos o genéricos (`MED`, `LGT`, `GB24`), lo que dificulta el cruce automático con glosarios oficiales si no se aplica una limpieza de datos algorítmica previa.
        3. **Pérdida de Registros Físicos:** Muchas hojas de misión originales se quemaron, se perdieron en combate o nunca fueron digitalizadas por el ejército, por lo que los tonelajes y recuentos de misiones deben tratarse como *mínimos históricos* y no como cifras absolutas.
        """)
    st.info("💡 **Conclusión de BI:** Un científico de datos debe auditar la procedencia de la información antes de dar por válidos los patrones estadísticos.")

# =====================================================================
# 📉 PÉRDIDAS Y CONTEXTO
# =====================================================================
elif menu == "📉 Pérdidas y Contexto":
    st.header("📉 El Coste Humano y Material de la Victoria Aérea")
    st.markdown(
        "Detrás de las impresionantes cifras de misiones y miles de toneladas de bombas lanzadas, "
        "la campaña aérea de 1943-1944 fue una de las guerras de desgaste más sangrientas del conflicto."
    )
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("La Perspectiva Aliada")
        st.write(
            "Los tripulantes de los bombarderos pesados tenían una de las tasas de bajas más altas de las "
            "fuerzas armadas. Un tripulante de B-17 en 1943 tenía estadísticamente pocas probabilidades de "
            "completar su turno de 25 misiones debido a la artillería antiaérea (Flak) y los cazas alemanes."
        )
    with col_p2:
        st.subheader("El Impacto en el Terreno")
        st.write(
            "La estrategia del 'bombardeo de área' o 'bombardeo estratégico' buscaba destruir la industria "
            "de guerra, pero a menudo conllevaba una tremenda destrucción de cascos históricos europeos "
            "y un altísimo coste en vidas de civiles franceses, belgas, italianos y alemanes."
        )

# =====================================================================
# 📁 ENLACES DEL PROYECTO
# =====================================================================
elif menu == "📁 Enlaces del Proyecto":
    st.header("📁 Repositorio y Recursos del Proyecto")
    st.markdown("---")
    st.markdown("### 🛠️ Acceso al Ecosistema del Proyecto")
    
    # Aquí puedes cambiar las URLs por las tuyas reales de GitHub si las tienes listas
    col_link1, col_link2 = st.columns(2)
    with col_link1:
        st.info("💻 **Código Fuente y Datos**")
        st.write("Consulta todo el código de limpieza en Python, los scripts de Streamlit y los archivos CSV decodificados.")
        st.link_button("🌐 Ir al Repositorio de GitHub", "https://github.com/", use_container_width=True)
        
    with col_link2:
        st.success("📊 **Analítica en Power BI**")
        st.write("El archivo maestro `.pbix` con el cuadro de mando dinámico de pérdidas y toneladas globales se encuentra en la raíz del repositorio local.")
        st.button("📊 Informe Local Adjunto (.pbix)", disabled=True, use_container_width=True)