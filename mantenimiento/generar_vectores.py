import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm

# ==========================================
# CONFIGURACIÓN
# ==========================================
# Resolver ruta absoluta relativa al script
script_dir = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(script_dir, '../biblioteca_indice.csv')
DB_DIR = os.path.join(script_dir, '../chroma_db')
COLLECTION_NAME = 'libros_db'
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
BATCH_SIZE = 1000

# Lógica de Categorización (la misma de app.py)
def categorizar_libro(nombre):
    nombre_lower = nombre.lower()
    categorias = []
    
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

def formatear_nombre_canal(canal):
    if pd.isna(canal): return "General"
    res = str(canal).replace('@', '').replace('_', ' ').replace('-', ' ')
    if res.lower() == 'sdabooks':
        return 'Colección SDA'
    elif res.lower() == 'librospdfcristianos':
        return 'Libros Cristianos'
    elif res.lower() == 'libroscristianosadventistas':
        return 'Biblioteca Adventista'
    else:
        return res.title()

def main():
    print(f"Cargando {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo bibliotec_indice.csv. ¡Ejecuta actualizar_buscador.py primero!")
        return

    # Limpiar y procesar datos
    df['Nombre'] = df['Nombre'].fillna("Libro Sin Título")
    if 'Canal' not in df.columns:
        df['Canal'] = 'General'
        
    df['Colección'] = df['Canal'].apply(formatear_nombre_canal)
    df['Tematicas'] = df['Nombre'].apply(categorizar_libro)
    
    # Rellenar URLs o IDs vacíos para no fallar en metadata
    for col in ['Ruta_Local', 'Drive_ID', 'Drive_URL']:
        if col in df.columns:
            df[col] = df[col].fillna("")

    total_docs = len(df)
    print(f"📚 {total_docs} libros encontrados. Inicializando ChromaDB...")

    # Instanciar ChromaDB local
    client = chromadb.PersistentClient(path=DB_DIR)
    
    # Configurar modelo de sentence-transformers
    print(f"🧠 Cargando modelo de IA '{MODEL_NAME}' (la primera vez puede tardar en descargar)...")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    
    # Obtener o crear la colección
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"} # Usar similitud del coseno
    )
    
    # Revisar cuántos documentos ya existen para no reindexar todo si se cortó
    existing_count = collection.count()
    if existing_count > 0:
        print(f"⚠️ La base de datos ya contiene {existing_count} libros. ¿Quieres re-crearla por completo? [s/N]")
        # Para forzar sobrescritura en automatización o script
        pass # Por ahora lo hacemos incremental basado en IDs: usaremos Ruta_Local como ID
    
    # Generar iteración por lotes
    print("🚀 Comenzando a embeber textos...")
    
    # Preparar datos
    ids = []
    documents = []
    metadatas = []
    
    for i, row in df.iterrows():
        # Usar la ruta o el drive_id como ID único
        doc_id = row['Drive_ID'] if row['Drive_ID'] else str(i)
        if not doc_id:
            doc_id = f"local_{i}"
            
        ids.append(doc_id)
        
        # El texto que la IA entenderá
        titulo_limpio = row['Nombre'].replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        temas_str = ", ".join(row['Tematicas'])
        coleccion_str = row['Colección']
        
        texto_busqueda = f"Título: {titulo_limpio}\nColección: {coleccion_str}\nTemática: {temas_str}"
        documents.append(texto_busqueda)
        
        # Metadata para luego poder filtrar y mostrar en app.py
        meta = {
            "nombre_archivo": row['Nombre'],
            "ruta_local": row['Ruta_Local'],
            "drive_id": row['Drive_ID'],
            "drive_url": row['Drive_URL'],
            "coleccion": coleccion_str,
            "tematica": temas_str
        }
        metadatas.append(meta)

    # Insertar en lotes
    for i in tqdm(range(0, total_docs, BATCH_SIZE), desc="Insertando en ChromaDB"):
        batch_ids = ids[i:i+BATCH_SIZE]
        batch_docs = documents[i:i+BATCH_SIZE]
        batch_metas = metadatas[i:i+BATCH_SIZE]
        
        # Upsert actualiza si existe, inserta si es nuevo
        collection.upsert(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metas
        )
        
    print("✅ ¡Proceso finalizado! Base de datos vectorial lista.")
    print(f"Se crearon localmente en la carpeta {DB_DIR}")

if __name__ == "__main__":
    main()
