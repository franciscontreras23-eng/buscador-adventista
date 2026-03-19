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
# CSS (Light Theme)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&family=Inter:wght@400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #f8f9fa;
        color: #191c1d;
    }
    
    .dashboard-header {
        font-family: 'Manrope', sans-serif;
        text-align: center;
        padding: 3rem 1rem 1rem 1rem;
        color: #191c1d;
        font-weight: 800;
        font-size: 3rem !important;
        letter-spacing: -1px;
    }
    
    .dashboard-subheader {
        text-align: center;
        color: #434655;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    div[data-baseweb="input"] {
        background-color: #edeeef !important;
        border: none !important;
        border-radius: 8px !important;
        color: #191c1d !important;
        transition: all 0.3s ease;
    }
    
    div[data-baseweb="input"] input {
        color: #191c1d !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        background-color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0, 74, 198, 0.08) !important;
    }

    .book-card {
        background: #ffffff;
        border-radius: 12px 12px 4px 4px;
        padding: 1.5rem;
        margin-bottom: 0rem !important;
        box-shadow: 0px 4px 20px rgba(25, 28, 29, 0.04);
        border: 1px solid #e1e3e4;
        border-bottom: none;
        transition: all 0.4s ease;
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }
    
    .book-card:hover {
        transform: translateY(-4px);
        box-shadow: 0px 10px 40px rgba(0, 74, 198, 0.06);
        border-color: #b4c5ff;
    }
    
    .book-title {
        font-family: 'Manrope', sans-serif;
        color: #191c1d;
        font-size: 1.1rem;
        font-weight: 800;
        line-height: 1.3;
        transition: color 0.3s;
    }
    
    .book-card:hover .book-title {
        color: #004ac6;
    }
    
    .book-collection {
        display: inline-block;
        background: #edeeef;
        color: #434655;
        font-size: 0.65rem;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .drive-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #004ac6 !important;
        text-decoration: none !important;
        font-family: 'Manrope', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        transition: transform 0.2s ease;
    }
    
    .book-card:hover .drive-btn {
        transform: translateX(5px);
    }
    
    .stat-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 2.5rem;
    }
    
    .stat-box {
        background: transparent;
        padding: 1rem 2rem;
        text-align: center;
        border-left: 1px solid #e1e3e4;
    }
    .stat-box:first-child { border-left: none; }
    
    .stat-value {
        font-family: 'Manrope', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        color: #004ac6;
        line-height: 1;
    }
    
    .book-tag {
        display: inline-block;
        background: #f3f4f5;
        color: #434655;
        font-size: 0.75rem;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        font-weight: 600;
        transition: background 0.2s;
    }
    .book-tag:hover {
        background: #acbfff;
        color: #00174b;
    }
    .icon-box {
        width: 4rem;
        height: 4rem;
        background: #dbe1ff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #004ac6;
    }
    .icon-box span { font-size: 2rem; }
    .header-card {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.5rem;
    }
    .collection-pill {
        background: #edeeef;
        color: #434655;
        font-size: 0.65rem;
        font-weight: 800;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .file-stats {
        display: flex;
        gap: 2rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: #737686;
        margin-top: 0.5rem;
    }
    
    /* Adaptaciones de la barra lateral y botones Streamlit */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #c3c6d7;
        color: #004ac6;
        font-weight: 600;
    }
    .stCheckbox label { color: #191c1d !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🌐 TRADUCCIONES (i18n)
# ==========================================
if 'lang' not in st.session_state:
    st.session_state.lang = "ES"

TRANSLATIONS = {
    "ES": {
        "title": "Berea Library",
        "subtitle": "Un santuario para el conocimiento digital.",
        "global_repo": "Repositorio Global",
        "curated": "Colecciones",
        "search_placeholder": "🔍 Busca por título, temática o palabra clave...",
        "ai_search": "Búsqueda Semántica con IA",
        "ai_search_desc": "La IA busca conceptos similares (ej. 'ansiedad' halla 'depresión')",
        "sidebar_title": "Opciones de Búsqueda",
        "collection_filter": "Filtrar por Colección",
        "all_collections": "Todas las colecciones",
        "theme_filter": "Filtrar por Temática",
        "results_count": "Mostrando **{}** resultados",
        "access_btn": "ACCEDER DOCUMENTO",
        "copy_btn": "📋 Copiar Link",
        "ai_summary": "🧬 Resumen de IA",
        "gen_summary": "Generar Resumen ⚡",
        "no_results": "No se encontraron resultados para tu búsqueda.",
        "load_more": "🔽 Cargar más resultados"
    },
    "EN": {
        "title": "Berea Library",
        "subtitle": "A sanctuary for digital knowledge.",
        "global_repo": "Global Repository",
        "curated": "Collections",
        "search_placeholder": "🔍 Search by title, theme or keyword...",
        "ai_search": "AI Semantic Search",
        "ai_search_desc": "AI searches for similar concepts (e.g., 'anxiety' finds 'depression')",
        "sidebar_title": "Search Options",
        "collection_filter": "Filter by Collection",
        "all_collections": "All collections",
        "theme_filter": "Filter by Theme",
        "results_count": "Showing **{}** results",
        "access_btn": "ACCESS DOCUMENT",
        "copy_btn": "📋 Copy Link",
        "ai_summary": "🧬 AI Summary",
        "gen_summary": "Generate Summary ⚡",
        "no_results": "No results found for your search.",
        "load_more": "🔽 Load more results"
    },
    "PT": {
        "title": "Berea Library",
        "subtitle": "Um santuário para o conhecimento digital.",
        "global_repo": "Repositório Global",
        "curated": "Coleções",
        "search_placeholder": "🔍 Pesquisar por título, tema ou palavra-chave...",
        "ai_search": "Pesquisa Semântica com IA",
        "ai_search_desc": "A IA procura conceitos semelhantes",
        "sidebar_title": "Opções de Pesquisa",
        "collection_filter": "Filtrar por Coleção",
        "all_collections": "Todas as coleções",
        "theme_filter": "Filtrar por Tema",
        "results_count": "Mostrando **{}** resultados",
        "access_btn": "ACESSAR DOCUMENTO",
        "copy_btn": "📋 Copiar Link",
        "ai_summary": "🧬 Resumo da IA",
        "gen_summary": "Gerar Resumo ⚡",
        "no_results": "Nenhum resultado encontrado.",
        "load_more": "🔽 Carregar mais resultados"
    }
}

def _t(key):
    return TRANSLATIONS[st.session_state.lang].get(key, key)

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

st.markdown(f'<div class="dashboard-header">{_t("title")}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dashboard-subheader">{_t("subtitle")}</div>', unsafe_allow_html=True)

# Sidebar para API Key y Filtros
with st.sidebar:
    st.session_state.lang = st.selectbox("🌐 Idioma / Language", ["ES", "EN", "PT"], index=["ES", "EN", "PT"].index(st.session_state.lang))
    st.markdown("---")
    
    st.subheader("Configuración de IA")
    try:
        api_key_por_defecto = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key_por_defecto = ""
        
    api_key = st.text_input("Ingresa tu Gemini API Key 🔑", value=api_key_por_defecto, type="password")
    st.markdown("""
    [¿Cómo conseguir una clave gratis?](https://aistudio.google.com/) 
    """)
    st.markdown("---")
    
    st.subheader(f"🗂️ {_t('sidebar_title')}")
    # Aplanar la lista de temáticas para sacar los valores únicos
    todas_las_tematicas = sorted(list(set([t for sublist in df['Tematicas'] for t in sublist])))
    temas_seleccionados = st.multiselect(_t("theme_filter"), todas_las_tematicas)

if df.empty:

    st.warning("⚠️ No se encontró el archivo de índice.")
    st.stop()

# Stats
total_libros = len(df)
colecciones = df['Colección'].dropna().unique()

st.markdown(f"""
<div class="stat-container">
    <div class="stat-box"><div class="stat-value">{total_libros:,}</div><div class="stat-label">{_t("global_repo")}</div></div>
    <div class="stat-box"><div class="stat-value">{len(colecciones)}</div><div class="stat-label">{_t("curated")}</div></div>
</div>
""", unsafe_allow_html=True)

# ================= =========================
# BARRA DE BUSQUEDA
# ==========================================
col_search, col_ia, col_filter = st.columns([3, 1, 1])

with col_search:
    busqueda = st.text_input("Search", label_visibility="collapsed", placeholder=_t("search_placeholder"))

with col_ia:
    usar_ia = st.checkbox(_t("ai_search"), help=_t("ai_search_desc"))

with col_filter:
    filtro_coleccion = st.selectbox("Collection", label_visibility="collapsed", options=[_t("all_collections")] + list(colecciones))

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
    if filtro_coleccion != _t("all_collections"):
        df_filtered = df_filtered[df_filtered['Colección'] == filtro_coleccion]

# El filtro de temática es una lista dentro del DF original
if 'temas_seleccionados' in locals() and temas_seleccionados:
    if not df_filtered.empty:
        df_filtered = df_filtered[df_filtered['Tematicas'].apply(lambda t: any(item in temas_seleccionados for item in t))]




# ==========================================
# RESULTADOS
# ==========================================
if len(df_filtered) > 0:
    st.write(_t("results_count").format(len(df_filtered)))
    
    df_display = df_filtered.head(st.session_state.limite_resultados)
    columnas = st.columns(3)
    
    for idx, (_, row) in enumerate(df_display.iterrows()):
        col_idx = idx % 3
        with columnas[col_idx]:
            titulo_limpio = row['Nombre'].replace('.pdf', '').replace('_', ' ').replace('-', ' ')
            tags_html = "".join([f'<span class="book-tag">{t}</span>' for t in row['Tematicas']])
            
            html_card = f"""
<div class="book-card">
    <div class="header-card">
        <div class="icon-box"><span class="material-symbols-outlined">description</span></div>
        <span class="collection-pill">{row['Colección']}</span>
    </div>
    <div>
        <h3 class="book-title">{titulo_limpio}</h3>
        <div style="margin-top: 12px;">{tags_html}</div>
    </div>
    <div class="file-stats">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span class="material-symbols-outlined" style="font-size: 1rem;">database</span> Format PDF
        </div>
    </div>
    <a href="{row['Drive_URL']}" target="_blank" class="drive-btn" style="margin-top: 0.5rem;">
        {_t("access_btn")} <span class="material-symbols-outlined" style="font-size: 1.1rem;">arrow_forward</span>
    </a>
</div>
"""
            st.markdown(html_card, unsafe_allow_html=True)
            
            # Utilidad para NotebookLM (Copiar Link rápido, solo botón sin caja de texto)
            st_copy_to_clipboard(row['Drive_URL'], before_copy_label=_t("copy_btn"), show_text=False)
            
            # Botón para Resumen IA (Nivel 1)
            with st.expander(_t("ai_summary")):
                if st.button(_t("gen_summary"), key=f"resumen_{row['Nombre']}"):
                    if not api_key:
                        st.error("⚠️ Debes tener el API Key para generar resúmenes.")
                    else:
                        with st.spinner("..."):
                            resumen = resumir_libro(row['Ruta_Local'], api_key)
                            st.markdown(resumen)
                            
    # Botón Ver Más
    if len(df_filtered) > st.session_state.limite_resultados:
        st.write("")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button(_t("load_more"), use_container_width=True):
                st.session_state.limite_resultados += 12
                st.rerun()
else:
    st.info(_t("no_results"))


