import plotly.express as px
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import os

# =====================================================================
# 📌 CONFIGURACIÓN DE RUTAS ABSOLUTAS (Triple blindaje para la nube)
# =====================================================================
carpeta_actual = os.path.dirname(__file__)

# 1. Ruta absoluta para el dataset de misiones limpio
ruta_clean_csv = os.path.abspath(os.path.join(carpeta_actual, "..", "adi_master_1943_1944_CLEAN.csv"))
df = pd.read_csv(ruta_clean_csv) 

# 2. Ruta absoluta para el glosario de aeronaves
ruta_csv_glosario = os.path.abspath(os.path.join(carpeta_actual, "..", "data", "3_thor_wwii_aircraft_gloss.csv"))

try:
    df_gloss_maestro = pd.read_csv(ruta_csv_glosario)
    df_gloss_maestro.columns = df_gloss_maestro.columns.str.strip()
except Exception:
    df_gloss_maestro = pd.DataFrame() # Respaldo si no existe el archivo

# =====================================================================
# ✈️ FUNCIÓN GLOBAL: TARJETAS DE AVIONES
# =====================================================================
def mostrar_tarjeta_avion(nombre_avion):
    """
    Cruza el nombre del avión directamente con la columna 'aircraft' 
    del glosario para extraer imágenes locales e hyperlinks reales.
    """
    traducciones = {"GB24": "B-24", "MED": "B-25", "LGT": "A-20", "GB17": "B-17", "SB17": "B-17"}
    nombre_corregido = traducciones.get(nombre_avion, nombre_avion)

    nombre_gloss_id = str(nombre_corregido).strip().replace("-", "").replace(" ", "").lower()
    ruta_foto = f"images/fotos_aviones/{nombre_gloss_id}.jpg"
    
    # 1. Imagen Local
    if os.path.exists(ruta_foto):
        st.image(ruta_foto, caption=f"Modelo: {nombre_avion}", use_container_width=True)
    else:
        st.info(f"📁 Guardar como: `{nombre_gloss_id}.jpg` en /fotos_aviones")
    
    # 2. Extracción del hipervínculo del Glosario
    link_web = None
    try:
        if not df_gloss_maestro.empty and "aircraft" in df_gloss_maestro.columns:
            nombres_csv_limpios = df_gloss_maestro["aircraft"].astype(str).str.strip().str.replace("-", "").str.replace(" ", "").str.lower()
            fila = df_gloss_maestro[nombres_csv_limpios == nombre_gloss_id]
            
            if not fila.empty and pd.notna(fila["hyperlink"].values[0]):
                link_web = str(fila["hyperlink"].values[0]).strip()
    except Exception:
        pass
    
    # 3. Renderizado de botón o aviso
    if link_web:
        st.link_button(f"🌐 Más info sobre {nombre_avion}", link_web, use_container_width=True)
    else:
        st.warning(f"⚠️ Sin enlace disponible para {nombre_avion}.")

# -----------------------------
# CONFIGURACIÓN DE LA INTERFAZ
# -----------------------------
st.set_page_config(
    page_title="WWII Bombing Dashboard",
    page_icon="✈️",
    layout="wide"
)

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

# =====================================================================
# SECCIÓN: INTRODUCCIÓN
# =====================================================================
if menu == "📌 Introducción":
    st.header("Introducción")

    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        # Ajustamos la ruta para que use la subcarpeta correcta en el repositorio
        st.image("images/introduccion.jpg", use_container_width=True)

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

# =====================================================================
# SECCIÓN: PANORAMA 1943-44
# =====================================================================
elif menu == "🗺️ Panorama 1943–44":
    st.header("Panorama 1943–1944")
    
    # Aseguramos formato numérico y limpieza de textos directamente sobre el df global
    df["Total Weight (Tons)"] = pd.to_numeric(df["Total Weight (Tons)"], errors="coerce").fillna(0)
    df["Target City"] = df["Target City"].fillna("Desconocida").astype(str).str.strip()
    df["Aircraft Series"] = df["Aircraft Series"].fillna("Desconocido").astype(str).str.strip()
    df["Target Country"] = df["Target Country"].fillna("Desconocido").astype(str).str.strip()

    # KPIs
    total_misiones = df["Mission ID"].nunique()
    total_toneladas = df["Total Weight (Tons)"].sum()
    promedio_toneladas = df["Total Weight (Tons)"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Misiones registradas", f"{total_misiones:,}")
    col2.metric("Toneladas lanzadas", f"{total_toneladas:,.0f}")
    col3.metric("Promedio por misión", f"{promedio_toneladas:,.2f}")

    # Preparación de datos geográficos
    df_mapa = df.dropna(subset=["Target Latitude", "Target Longitude"]).copy()
    df_mapa["Target Latitude"] = pd.to_numeric(df_mapa["Target Latitude"], errors="coerce")
    df_mapa["Target Longitude"] = pd.to_numeric(df_mapa["Target Longitude"], errors="coerce")
    df_mapa = df_mapa.dropna(subset=["Target Latitude", "Target Longitude"])

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
    st.subheader("🔍 Panel de Inspección Operativa")
    
    lista_ciudades = sorted(df_resumen["Target City"].unique())
    ciudad_seleccionada = st.selectbox(
        "Buscar objetivo histórico:",
        lista_ciudades,
        index=None,
        placeholder="Escribe una ciudad (ej. Tours, Caen, Paris)..."
    )

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

            st.markdown("---")
            st.markdown("### 📷 Inteligencia Visual y Documentación de Aeronaves")
            
            aviones_en_ciudad = [a for a in df_detalle_ciudad["Aircraft Series"].unique() if pd.notna(a) and str(a).strip() != ""]
            
            if len(aviones_en_ciudad) > 0:
                columnas_fotos = st.columns(len(aviones_en_ciudad))
                for i, avion in enumerate(aviones_en_ciudad):
                    with columnas_fotos[i]:
                        mostrar_tarjeta_avion(avion)
            else:
                st.warning("⚠️ No se han detectado modelos de aeronaves registrados para esta ciudad.")

    # Cierre con mención a Power BI
    st.markdown("---")
    st.markdown("### 📊 Ecosistema de Inteligencia de Datos (Conexión Analítica)")
    with st.container(border=True):
        st.markdown(
            "💡 **Nota de Arquitectura:** Esta aplicación web en **Streamlit (Python)** está diseñada "
            "específicamente para la exploración interactiva sobre mapas y documentación fotográfica táctica."
        )
        st.markdown(
            "Para el análisis estadístico global macro (patrones de flotas y tonelajes totales acumulados), "
            "el proyecto cuenta con un **Cuadro de Mando Avanzado en Power BI** (archivo `.pbix` en el repositorio)."
        )
        st.button("📊 Dashboard Power BI (Ejecutar archivo local .pbix para interactuar)", disabled=True, use_container_width=True)

# =====================================================================
# SECCIÓN: 1-5 JUNIO 1944 (PREVIO DÍA D)
# =====================================================================
elif menu == "🔥 1–5 Junio 1944":
    st.header("🚀 Operaciones Preliminares: El Aislamiento de Normandía (1–5 Junio)")
    st.markdown(
        "Durante los primeros cinco días de junio de 1944, las fuerzas aéreas aliadas ejecutaron la "
        "**Operación Fortitude** y el Plan de Transportes para destruir las líneas de comunicación francesas."
    )
    
    try:
        col_fecha = [c for c in df.columns if "date" in c.lower() or "fecha" in c.lower()][0]
        df_copia = df.copy()
        df_copia['Fecha_DT'] = pd.to_datetime(df_copia[col_fecha], errors='coerce')
        df_previo = df_copia[(df_copia['Fecha_DT'] >= '1944-06-01') & (df_copia['Fecha_DT'] <= '1944-06-05')]
        
        if not df_previo.empty:
            misiones_previas = len(df_previo)
            aviones_previos = df_previo["Aircraft Series"].nunique()
            st.info(f"📊 **Métricas del periodo:** Se ejecutaron **{misiones_previas} misiones** con **{aviones_previos} modelos** de aviones.")
            
            col_ciudad = [c for c in df_previo.columns if "city" in c.lower() or "ciudad" in c.lower() or "target" in c.lower()][0]
            top_ciudades = df_previo[col_ciudad].value_counts().head(5)
            st.write("**Principales objetivos estratégicos atacados (Top Ciudades):**")
            st.bar_chart(top_ciudades)
        else:
            st.warning("⚠️ No se encontraron misiones para este rango de fechas en este corte de datos.")
    except Exception:
        st.info("ℹ️ Campaña de ablandamiento logístico: Ataques masivos a puentes sobre el Sena y el Loira.")

# =====================================================================
# SECCIÓN: DÍA D (6 JUNIO 1944)
# =====================================================================
elif menu == "⚔️ Día D (6 Junio 1944)":
    st.header("⚔️ El Día Más Largo: 6 de Junio de 1944")
    st.markdown(
        "El 6 de junio de 1944, miles de bombarderos pesados atacaron la Muralla del Atlántico "
        "minutos antes de que las oleadas de desembarco asaltaran las playas de Normandía."
    )
    
    try:
        col_fecha = [c for c in df.columns if "date" in c.lower() or "fecha" in c.lower()][0]
        df_copia = df.copy()
        df_copia['Fecha_DT'] = pd.to_datetime(df_copia[col_fecha], errors='coerce')
        df_diad = df_copia[df_copia['Fecha_DT'] == '1944-06-06']
        
        if not df_diad.empty:
            st.success(f"💥 **Impacto del Día D:** ¡Registradas **{len(df_diad)} misiones de combate** en el dataset para esta jornada!")
            aviones_diad = df_diad["Aircraft Series"].value_counts()
            st.write("**Flota aérea activa durante los desembarcos (Misiones por modelo):**")
            st.bar_chart(aviones_diad)
        else:
            st.warning("⚠️ Sin registros específicos para el 6 de junio en este fragmento del dataset.")
    except Exception:
        st.info("ℹ️ Superioridad aérea absoluta: Los aliados neutralizaron la respuesta aérea de la Luftwaffe.")

# =====================================================================
# SECCIÓN: GALERÍA HISTÓRICA
# =====================================================================
elif menu == "📷 Galería Histórica":
    st.header("📷 Archivo Fotográfico De Operaciones")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/e/e1/B-17F_Forming_Up_-_GPN-2002-000018.jpg", caption="Boeing B-17 Flying Fortress en formación.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/4/45/B-24_Liberator_dropping_bombs.jpg", caption="Consolidated B-24 Liberator en acción.")
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/9/9d/B-29_In_Flight.jpg", caption="Boeing B-29 Superfortress estratégico.")
        st.image("https://upload.wikimedia.org/wikipedia/commons/d/df/Avro_Lancaster_B_I_PA474_BBMF.jpg", caption="Avro Lancaster de la RAF.")

# =====================================================================
# SECCIÓN: SESGOS DEL DATASET
# =====================================================================
elif menu == "⚠️ Sesgos del Dataset":
    st.header("⚠️ Sesgos, Vacíos y Limitaciones de la Base de Datos")
    
    with st.container(border=True):
        st.markdown("""
        1. **Predominio Angloamericano:** Recoge masivamente misiones de la USAAF y la RAF. El Frente Oriental y las acciones del eje apenas están representados.
        2. **Estandarización de Modelos:** Existen códigos militares ambiguos (`MED`, `LGT`, `GB24`) que exigen algoritmos de limpieza de datos previos para su correcto emparejamiento.
        3. **Mínimos Históricos:** Debido a la destrucción y pérdida de cuadernos de vuelo originales, los tonelajes deben interpretarse como umbrales mínimos y nunca como totales definitivos.
        """)

# =====================================================================
# SECCIÓN: PÉRDIDAS Y CONTEXTO
# =====================================================================
elif menu == "📉 Pérdidas y Contexto":
    st.header("📉 El Coste Humano y Material de la Victoria Aérea")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("La Perspectiva Aliada")
        st.write("Los tripulantes de bombardeo sufrieron tasas de bajas extremas en 1943 debido al fuego de la artillería antiaérea (Flak) y los interceptores alemanes.")
    with col_p2:
        st.subheader("El Impacto en el Terreno")
        st.write("La estrategia del bombardeo estratégico conllevó una severa destrucción de cascos urbanos y nudos logísticos, afectando drásticamente a las poblaciones civiles europeas.")

# =====================================================================
# SECCIÓN: ENLACES DEL PROYECTO
# =====================================================================
elif menu == "📁 Enlaces del Proyecto":
    st.header("📁 Repositorio y Recursos del Proyecto")
    st.markdown("---")
    
    col_link1, col_link2 = st.columns(2)
    with col_link1:
        st.info("💻 **Código Fuente y Datos**")
        st.link_button("🌐 Ir al Repositorio de GitHub", "https://github.com/", use_container_width=True)
    with col_link2:
        st.success("📊 **Analítica en Power BI**")
        st.button("📊 Informe Local Adjunto (.pbix)", disabled=True, use_container_width=True)