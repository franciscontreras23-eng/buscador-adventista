import streamlit as st
import pandas as pd
import os
from google import genai
from st_copy_to_clipboard import st_copy_to_clipboard


# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Biblioteca Digital Francis",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= =========================
# ESTILOS PREMIUM (Vanilla CSS)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(37, 38, 43, 1) 0%, rgba(20, 21, 23, 1) 90%);
        color: #ffffff;
    }
    
    .dashboard-header {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem !important;
        letter-spacing: -1px;
    }
    
    .dashboard-subheader {
        text-align: center;
        color: #A0AAB5;
        font-size: 1.2rem;
        margin-top: -2rem;
        margin-bottom: 3rem;
    }

    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        transition: all 0.3s ease;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #4ECDC4 !important;
        box-shadow: 0 0 15px rgba(78, 205, 196, 0.2) !important;
    }

    .book-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        backdrop-filter: blur(10px);
    }
    
    .book-card:hover {
        transform: translateY(-4px);
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(78, 205, 196, 0.3);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .book-title {
        color: #FFFFFF;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    .book-collection {
        display: inline-block;
        background: rgba(78, 205, 196, 0.1);
        color: #4ECDC4;
        font-size: 0.8rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        margin-bottom: 1rem;
        text-transform: capitalize;
    }
    
    .drive-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        background: linear-gradient(135deg, #1A73E8 0%, #1557B0 100%);
        color: white !important;
        text-decoration: none !important;
        padding: 0.8rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        border: none;
        transition: all 0.2s ease;
        gap: 8px;
    }
    
    .stat-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 2.5rem;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.02);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        padding: 1rem 2rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.03);
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #4ECDC4;
    }
    .book-tag {
        display: inline-block;
        background: rgba(255, 165, 0, 0.12);
        color: #FFA500;
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        border: 1px solid rgba(255, 165, 0, 0.3);
        font-weight: 500;
    }
</style>

""", unsafe_allow_html=True)

# Lógica de Categorización Automática (Nivel 2)
def categorizar_libro(nombre):
    nombre_lower = nombre.lower()
    categorias = []
    
    # Heurísticas de temáticas en base al título
    if any(k in nombre_lower for k in ["salud", "cocina", "dieta", "receta", "nutricion", "vegan", "vegetari"]):
        categorias.append("Salud y Nutrición 🥗")
    if any(k in nombre_lower for k in ["niño", "infantil", "joven", "menor", "adolescente", "historias"]):
        categorias.append("Infantil y Juvenil 👼")
    if any(k in nombre_lower for k in ["elena", "white", "egw", "mensajes", "mente", "profetisa"]):
        categorias.append("Elena G. de White 📖")
    if any(k in nombre_lower for k in ["biblia", "estudio", "profecia", "daniel", "apocalipsis", "doctrine"]):
        categorias.append("Estudios Bíblicos 📜")
    if any(k in nombre_lower for k in ["sermon", "bosquejo", "predic", "homilet"]):
        categorias.append("Sermones y Homilética 🗣️")
        
    return categorias if categorias else ["General 📚"]

# Lógica de nombres de carpeta
def formatear_nombre_canal(canal):
    res = canal.replace('@', '').replace('_', ' ').replace('-', ' ')
    if res.lower() == 'sdabooks':
        return 'Colección SDA'
    elif res.lower() == 'librospdfcristianos':
        return 'Libros Cristianos'
    elif res.lower() == 'libroscristianosadventistas':
        return 'Biblioteca Adventista'
    else:
        return res.title()

@st.cache_data(ttl=3600)
def cargar_datos():
    ruta_csv = 'biblioteca_indice.csv'
    if os.path.exists(ruta_csv):
        df = pd.read_csv(ruta_csv)
    else:
        url_drive_csv = "https://drive.google.com/uc?id=1CTh5XFNipHCky2JaUsB8eyI8hahLlGdU"
        try:
            df = pd.read_csv(url_drive_csv)
        except Exception:
            return pd.DataFrame()
    
    if 'Canal' in df.columns:
        df['Colección'] = df['Canal'].apply(formatear_nombre_canal)
    else:
        df['Colección'] = 'General'
        
    # Aplicar categorización automática
    df['Tematicas'] = df['Nombre'].apply(categorizar_libro)
    return df

        
    return df

# Lógica IA - Búsqueda
def interpretar_busqueda_con_ia(query, api_key):
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Eres un experto en búsqueda de una biblioteca cristiana. El usuario busca: '{query}'.
        
        Devuelve texto plano SIN MARKDOWN, SIN ASTERISCOS. Estrictamente 2 líneas:
        PRIMARIOS: <Sinónimos exactos de '{query}', números romanos, traducciones al inglés/portugués>. Ejemplo: 2 reyes|ii reyes|segunda de reyes|2 kings|2 reis
        SECUNDARIOS: <Personajes principales o subtemas MUY específicos de '{query}'>. NO uses palabras genéricas como 'Israel', 'Biblia', 'Antiguo', 'Testamento', 'Rey', 'Juda'. Solo términos exclusivos y fuertes. Ej: elias|eliseo|naamán
        """
        response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
        import re
        texto = response.text.replace('*', '').replace('`', '')
        
        primarios = ""
        secundarios = ""
        
        p_match = re.search(r'PRIMARIOS:(.*)', texto, re.IGNORECASE)
        s_match = re.search(r'SECUNDARIOS:(.*)', texto, re.IGNORECASE)
        
        if p_match: primarios = p_match.group(1).strip()
        if s_match: secundarios = s_match.group(1).strip()
                
        return primarios, secundarios
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
            return "ERROR_QUOTA", "ERROR_QUOTA"
        return "", ""




# Lógica IA - Resumen (Nivel 1)
def resumir_libro(ruta, api_key):
    try:
        from pypdf import PdfReader
        
        if not os.path.exists(ruta):
            return "⚠️ El archivo no se encuentra en el disco local!"
            
        reader = PdfReader(ruta)
        texto = ""
        # Leer primeras 4 páginas (suele tener índice, introducción y autor)
        paginas_a_leer = min(4, len(reader.pages))
        for i in range(paginas_a_leer):
            pag_texto = reader.pages[i].extract_text()
            if pag_texto:
                texto += pag_texto + "\n"
                
        if len(texto.strip()) < 50:
             return "💡 Este PDF parece una imagen escaneada (sin OCR). No se puede leer el texto interno directamente."

        client = genai.Client(api_key=api_key)
        prompt = f"""
        A partir del siguiente extracto del inicio de un libro:
        ---
        {texto[:6000]} # Limitamos a 6000 chars por seguridad de token
        ---
        
        Extrae y genera un resumen con la siguiente estructura:
        1. **Tema principal**: (1 frase de qué trata)
        2. **Autor**: (Identifica al autor si está ahí)
        3. **Puntos Clave**: (3 viñetas resumen)
        """
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error al leer PDF: {str(e)}"

# Lógica IA - Reordenar por Relevancia (Nivel 1 Upgrade)
def reordenar_por_relevancia(query, df_sub, api_key):
    try:
        if df_sub.empty or len(df_sub) <= 1:
            return df_sub
            
        # 🥇 REGLA DE ORO: Priorizar primero los que contienen la búsqueda EXACTA literal antes de que la IA decida
        mask_exacto = df_sub['Nombre'].str.contains(query, case=False, na=False)
        df_exacto = df_sub[mask_exacto]
        df_resto = df_sub[~mask_exacto]
        
        # Unimos: exactos primero, resto abajo
        df_prioritario = pd.concat([df_exacto, df_resto])
            
        # Preparar la lista para la IA
        df_recortado = df_prioritario.head(40)
        items = []
        indices_originales = []


        
        for i, (_, row) in enumerate(df_recortado.iterrows()):
            items.append(f"{i+1}. {row['Nombre']}")
            indices_originales.append(_) # El índice real del DataFrame
            
        lista_texto = "\n".join(items)
        
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Un usuario busca en un biblioteca de libros esto: '{query}'
        
        Aquí tienes una lista de libros encontrados:
        {lista_texto}
        
        Evalúa cuáles responden mejor o son más relevantes para la búsqueda del usuario.
        Devuelve ÚNICAMENTE los números de la lista (1, 2, 3...) ordenados de mayor a menor relevancia, separados por comas.
        Ejemplo: 3, 1, 4, 2
        No escribas texto extra, solo los números separados por coma.
        """
        
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        orden_str = response.text.strip()
        
        # Limpiar y extraer números
        # Remover corchetes, comillas que a veces la IA envia
        orden_str = orden_str.replace('[', '').replace(']', '').replace('`', '')
        # Extraer los números
        numeros = [int(n.strip()) for n in orden_str.split(',') if n.strip().isdigit()]
        
        indices_reordenados = []
        for num in numeros:
            idx_lista = num - 1
            if 0 <= idx_lista < len(indices_originales):
                indices_reordenados.append(indices_originales[idx_lista])
                
        # Agregar los que faltan (si la IA ignoró alguno)
        items_restantes = [i for i in indices_originales if i not in indices_reordenados]
        indices_finales = indices_reordenados + items_restantes
        
        # Mapear de vuelta al dataframe original
        df_reordenado = df_sub.loc[indices_finales]
        
        # Si había más de 40 elementos, adjuntar el resto al final en su orden original
        if len(df_sub) > 40:
            sobrantes = df_sub.iloc[40:]
            df_reordenado = pd.concat([df_reordenado, sobrantes])
            
        return df_reordenado
    except Exception as e:
        # Si falla (por límite de cuota), dejamos el orden original
        # Para que no se quede la pantalla en blanco
        return df_sub

# ==========================================
# CARGAR DATOS Y DASHBOARD
# ==========================================

df = cargar_datos()

st.markdown('<div class="dashboard-header">Biblioteca Digital 🧠</div>', unsafe_allow_html=True)

# Sidebar para API Key y Filtros
with st.sidebar:
    st.subheader("Configuración de IA")
    api_key_por_defecto = st.secrets.get("GEMINI_API_KEY", "")
    api_key = st.text_input("Ingresa tu Gemini API Key 🔑", value=api_key_por_defecto, type="password")
    st.markdown("""
    [¿Cómo conseguir una clave gratis?](https://aistudio.google.com/) 
    """)
    st.markdown("---")
    
    st.subheader("Filtros Avanzados 🗂️")
    # Aplanar la lista de temáticas para sacar los valores únicos
    todas_las_tematicas = sorted(list(set([t for sublist in df['Tematicas'] for t in sublist])))
    temas_seleccionados = st.multiselect("Filtrar por tema:", todas_las_tematicas)

if df.empty:

    st.warning("⚠️ No se encontró el archivo de índice.")
    st.stop()

# Stats
total_libros = len(df)
colecciones = df['Colección'].dropna().unique()

st.markdown(f"""
<div class="stat-container">
    <div class="stat-box"><div class="stat-value">{total_libros:,}</div><div class="stat-label">Libros Totales</div></div>
    <div class="stat-box"><div class="stat-value">{len(colecciones)}</div><div class="stat-label">Colecciones</div></div>
</div>
""", unsafe_allow_html=True)

# ================= =========================
# BARRA DE BUSQUEDA
# ==========================================
col_search, col_ia, col_filter = st.columns([3, 1, 1])

with col_search:
    busqueda = st.text_input("", placeholder="🔍 Escribe lo que buscas (Ej: Libros de Elena White para jóvenes)...")

with col_ia:
    usar_ia = st.checkbox("Buscar con IA 🤖")

with col_filter:
    filtro_coleccion = st.selectbox("", ["Todas las colecciones"] + list(colecciones))

# ==========================================
# LÓGICA DE FILTRADO
# ==========================================
# ==========================================
# GESTIÓN DE ESTADO (PAGINACIÓN)
# ==========================================
if 'busqueda_anterior' not in st.session_state:
    st.session_state.busqueda_anterior = ""
    st.session_state.limite_resultados = 12

if busqueda != st.session_state.busqueda_anterior:
    st.session_state.busqueda_anterior = busqueda
    st.session_state.limite_resultados = 12

# ==========================================
# INICIALIZAR CHROMADB
# ==========================================
@st.cache_resource
def get_chroma_collection():
    import chromadb
    from chromadb.utils import embedding_functions
    try:
        if not os.path.exists("./chroma_db"):
            return None
        client = chromadb.PersistentClient(path="./chroma_db")
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name='paraphrase-multilingual-MiniLM-L12-v2')
        return client.get_collection(name="libros_db", embedding_function=emb_fn)
    except Exception as e:
        st.sidebar.error(f"Error cargando ChromaDB: {e}")
        return None

collection = get_chroma_collection()

# ==========================================
# LÓGICA DE BÚSQUEDA Y FILTRADO
# ==========================================
df_filtered = df

if busqueda:
    if usar_ia and collection:
        with st.spinner("Buscando con IA Vectorial... ✨"):
            # Construir filtros de metadata si existen
            where_clause = {}
            if filtro_coleccion != "Todas las colecciones":
                where_clause["coleccion"] = filtro_coleccion
                
            # Buscar en ChromaDB
            if where_clause:
                results = collection.query(
                    query_texts=[busqueda],
                    n_results=100,
                    where=where_clause
                )
            else:
                results = collection.query(
                    query_texts=[busqueda],
                    n_results=100
                )
                
            if results and results['ids'] and len(results['ids'][0]) > 0:
                # Obtener IDs devueltos ordenados por relevancia
                ids_encontrados = results['ids'][0]
                # Filtrar el DataFrame para quedarnos solo con esos IDs (Drive_ID o índice)
                # Como guardamos doc_id = Drive_ID o local_i
                
                # Para cruzar fácil: mapear ID a row
                # En df, el drive ID está en 'Drive_ID'.
                mask_drive = df_filtered['Drive_ID'].isin(ids_encontrados)
                
                # Para los que no tenían Drive ID, el doc_id era local_{indice}
                # Esto es un poco complejo de cruzar rápido si no, hagamos algo más inteligente:
                # En ChromaDB guardamos en metadatas la 'ruta_local', la usamos como clave fuerte.
                rutas_encontradas = [meta['ruta_local'] for meta in results['metadatas'][0]]
                
                df_filtered = df_filtered[df_filtered['Ruta_Local'].isin(rutas_encontradas)].copy()
                
                # Mantener el orden semántico que nos dio ChromaDB
                # Crear diccionario con posición
                orden_dict = {ruta: i for i, ruta in enumerate(rutas_encontradas)}
                df_filtered['orden_semantico'] = df_filtered['Ruta_Local'].map(orden_dict)
                df_filtered = df_filtered.sort_values('orden_semantico')
                
                st.caption("🎯 **Resultados clasificados por Relevancia Semántica (IA Local)**")
            else:
                df_filtered = df_filtered.iloc[0:0] # Vacio
    else:
        # Búsqueda clásica por texto exacto si la IA está apagada o no hay DB
        if usar_ia and not collection:
            st.sidebar.error("⚠️ La Base de Datos Vectorial no está lista. Usa el script generar_vectores.py primero. Retrocediendo a búsqueda de texto normal.")
        df_filtered = df_filtered[df_filtered['Nombre'].str.contains(busqueda, case=False, na=False)]

# Si la IA NO se usó (o falló), aplicar filtros tradicionales arriba de los resultados
if not (usar_ia and collection and busqueda):
    if filtro_coleccion != "Todas las colecciones":
        df_filtered = df_filtered[df_filtered['Colección'] == filtro_coleccion]

# El filtro de temática es una lista dentro del DF original
if 'temas_seleccionados' in locals() and temas_seleccionados:
    if not df_filtered.empty:
        df_filtered = df_filtered[df_filtered['Tematicas'].apply(lambda t: any(item in temas_seleccionados for item in t))]




# ==========================================
# RESULTADOS
# ==========================================
if len(df_filtered) > 0:
    st.write(f"Mostrando **{len(df_filtered)}** resultados relacionados")
    
    df_display = df_filtered.head(st.session_state.limite_resultados)
    columnas = st.columns(3)
    
    for idx, (_, row) in enumerate(df_display.iterrows()):
        col_idx = idx % 3
        with columnas[col_idx]:
            titulo_limpio = row['Nombre'].replace('.pdf', '').replace('_', ' ').replace('-', ' ')
            # Generar HTML de tags
            tags_html = "".join([f'<span class="book-tag">{t}</span>' for t in row['Tematicas']])
            
            st.markdown(f"""
            <div class="book-card">
                <div class="book-collection">📂 {row['Colección']}</div>
                <div style="margin-top: -5px; margin-bottom: 8px;">{tags_html}</div>
                <div class="book-title">{titulo_limpio}</div>
                <a href="{row['Drive_URL']}" target="_blank" class="drive-btn">Abrir en Google Drive</a>
            </div>
            """, unsafe_allow_html=True)
            
            # Utilidad para NotebookLM (Copiar Link rápido)
            st_copy_to_clipboard(row['Drive_URL'], text="📋 Copiar Link", show_text=True)
            
            # Botón para Resumen IA (Nivel 1)
            with st.expander("🧬 Resumen de IA"):
                if st.button("Generar Resumen ⚡", key=f"resumen_{row['Nombre']}"):
                    if not api_key:
                        st.error("⚠️ Debes tener el API Key para generar resúmenes.")
                    else:
                        with st.spinner("Leyendo y resumiendo..."):
                            resumen = resumir_libro(row['Ruta_Local'], api_key)
                            st.markdown(resumen)
                            
    # Botón Ver Más
    if len(df_filtered) > st.session_state.limite_resultados:
        st.write("")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🔽 Cargar más resultados", use_container_width=True):
                st.session_state.limite_resultados += 12
                st.rerun()
else:
    st.info("No se encontraron resultados para tu búsqueda.")


