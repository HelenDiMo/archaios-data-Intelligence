<p align="center">
  <img src="logo_adi.png" alt="Logo del Proyecto" width="250">
</p>

# 🏛️ Archaios Data Intelligence

## 🌐 Proyecto: Operación Normandía - Inteligencia de Datos aplicada a la Arqueología Contemporánea

![Status](https://img.shields.io/badge/Status-Entregado-green)
![Tools](https://img.shields.io/badge/Herramientas-Power%20BI%20%7C%20Excel-blue)
![Focus](https://img.shields.io/badge/Enfoque-Arqueología%20Militar%20%7C%20Predictivo-orange)

---

## 📝 1. Descripción del Proyecto

**Archaios Data Intelligence** ha desarrollado este proyecto de consultoría analítica especializado para optimizar las campañas de excavación y exploración arqueológica en la región de Normandía (Francia). 

El objetivo es transformar los registros históricos de las operaciones aéreas aliadas entre **1943 y el 6 de junio de 1944 (Día D)** en un modelo de inteligencia geoespacial. Analizando la densidad de los bombardeos e incursiones, nuestro dashboard permite a los equipos arqueológicos identificar zonas con un alto potencial de restos materiales enterrados (búnkeres destruidos, fuselajes de aeronaves, cráteres de impacto y restos logísticos), minimizando los costes de prospección y maximizando la tasa de descubrimiento científico.

---

## 📊 2. Anatomía del Repositorio e Infraestructura de Datos

Para garantizar la reproducibilidad y la higiene del proyecto, la estructura de archivos sigue los estándares profesionales de la industria:

```text
📁 Archaios_Normandia/
│
├── 📂 data/                                # Datos crudos THOR                               
│   ├── 📊 1_cleanbombww2.csv               # Incursiones realizadas - THOR
|   ├── 📊 2_operations.csv                 # Operaciones realizadas - THOR
|   ├── 📊 3_thor_wwii_aircraft_gloss.csv   # Glosario de aviones utilizados - THOR
|   ├── 📊 4_thor_wwii_data_clean.csv       # Limpieza de datos de 1_cleanbombww2.csv - THOR
|   └── 📊 5_thor_wwii_weapon_gloss.csv     # Glosario de bombas/armas utilizadas
|
├── .gitignore
|
├── 📊 adi_dataset_master.csv
├── 📊 adi_master_1_5_junio.csv
├── 📊 adi_master_1943_1944_CLEAN.csv
| 
├── 🗒️ desembarco_normandia.ipynb           # Notebook con EDA
│── 📄 README.md                            # La portada del proyecto (este archivo).
└── 📈 wwii_analisys_dashboard.pbix         # Cuadro de mando interactivo en Power BI.
```

## 🚀 3. El Cuadro de Mando (Dashboard de Power BI)

El cuadro de mando cuenta con un *mapa interactivo* con el que se podrán explorar las zonas afectadas y que nos ayudará a centrarnos en la zona de interés.

Contamos con una *segmentación interactiva* por fechas, tipos de aeronaves (Aircraft Series) y ciudades objetivo (Target City), permitiendo micro-localizar áreas arqueológicas con precisión kilométrica.

El análisis visual está estructurado de manera cronológica y estratégica para guiar a los directores de excavación a través de las diferentes fases del conflicto:

### 📌 Vistas Principales del Dashboard:

* **Panorama 1943 - 1944** (Vista Global): Identificación de los macro-objetivos y zonas de alta concentración de impactos en todo el teatro de operaciones en Europa.

* **1-5 de Junio de 1944** (Fase de Ablandamiento Logístico) : Análisis crítico de los 5 días previos al desembarco. Muestra de forma pormenorizada las ciudades e infraestructuras atacadas para aislar las playas de Normandía.

* **Dia D** (El Día más Largo): Análisis visual de la situación vivida en ese día, en el que se realizó una de las operaciones militares más importantes y trágicas de la historia. 

### 🟩 Justificación de la Herramienta

Se seleccionó Power BI como herramienta principal debido a su capacidad para construir dashboards interactivos orientados a negocio sin necesidad de programación.

Power BI permite integrar datos históricos, aplicar filtros cruzados, generar mapas geoespaciales y estructurar una narrativa visual clara, lo que lo convierte en la opción ideal para el público, tanto técnico, como no técnico.

Además, su interfaz intuitiva facilita que la organización pueda mantener y ampliar el cuadro de mando sin depender de desarrolladores externos.

## ⚠️ 4. Sesgos y Gobernanza del Dato

Los datos utilizados proceden del repositorio militar **THOR (Theater History of Operations Reports)** del Departamento de Defensa de EE.UU. Aunque es una fuente histórica de alto valor, presenta limitaciones que deben considerarse antes de tomar decisiones operativas o arqueológicas:

### **1. Sesgo de representatividad**  
Solo se registran misiones documentadas. Algunas operaciones no quedaron archivadas o se perdieron, lo que puede subestimar la actividad real en ciertas zonas.

### **2. Sesgo geográfico**  
El dataset solo muestra puntos donde hubo bombardeos registrados. Las zonas sin datos no implican ausencia de actividad, sino ausencia de registro.

### **3. Sesgo de etiquetado**  
Algunos objetivos aparecen como *“Unknown”* o *“Unidentified”*, reduciendo la precisión analítica y dificultando la clasificación por tipo de infraestructura atacada.

### **4. Sesgo temporal**  
La calidad del registro varía entre 1943 y 1944. En 1944, debido a la preparación del Día D, la documentación fue más exhaustiva, lo que puede generar aparentes incrementos de actividad que responden a mejoras en el registro, no necesariamente a más bombardeos.

### **Impacto si se ignoran**  
Basar decisiones arqueológicas únicamente en estos datos podría llevar a priorizar zonas incompletas o mal documentadas, o a subestimar áreas con riesgo de munición sin detonar (UXO).

### **Recomendación**  
Este análisis debe complementarse con fuentes históricas adicionales: mapas militares, archivos locales, informes de daños y fotografías aéreas.


## 🛠️ 5. Guía de Uso e Instalación

Para explorar las capacidades interactivas del modelo de datos:

1. Clonar el repositorio a tu máquina local utilizando la terminal:

    ```Bash
    git clone https://github.com/HelenDiMo/archaios-data-Intelligence.git
    ```

2. Instalar Power BI Desktop - [versión gratuita de Microsoft](https://www.microsoft.com/es-es/download/details.aspx?id=58494)

3. Abrir el archivo situado en la raíz del proyecto - `wwii_analisys_dashboard.pbix`

El panel cargará automáticamente los datos locales almacenados en la carpeta raíz:
>`adi_master_1943_1944_CLEAN.csv`
>`adi_master_1_5_junio.csv`
>`adi_dataset_master.csv` 
     

¡Usa los filtros interactivos para explorar el mapa de calor de las misiones!

## 🎯 6. Conclusiones de Negocio (Valor Arqueológico)

* **Reducción de Costes:** El análisis de los datos demuestra que los esfuerzos no deben centrarse únicamente en la línea de costa, sino en los nudos de transporte del interior, donde la densidad de bombardeos para destruir puentes y vías férreas fue masiva entre el 1 y el 5 de junio.

* **Seguridad en las Excavaciones:** Identificar la densidad del tonelaje de bombas caídas ayuda a mapear posibles zonas con presencia de munición sin detonar (UXO), un factor crítico de seguridad para cualquier equipo arqueológico sobre el terreno.

## 🧠 Sobre la Consultora
Archaios Data Intelligence — Iluminando el pasado a través de la ciencia de datos.
