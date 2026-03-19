import os
import subprocess
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# CONFIGURACIÓN
# ==========================================
DOWNLOAD_FOLDER = '/Users/francis.contreras23/Library/CloudStorage/GoogleDrive-secretariosureste23@gmail.com/Mi unidad/Documentos Francis/Theology/Articulos, libros y otros documentos'
INDEX_FILE = 'biblioteca_indice.csv'
# ==========================================

def get_drive_id(file_path):
    """
    Lee el atributo extendido de Google Drive en macOS para obtener el ID del archivo.
    """
    try:
        res = subprocess.run(["xattr", "-p", "com.google.drivefs.item-id#S", file_path], capture_output=True, text=True)
        id_drive = res.stdout.strip()
        if id_drive:
            return id_drive
    except Exception:
        pass
    return None

def procesar_archivo(args):
    path_completo, file, root = args
    drive_id = get_drive_id(path_completo)
    if drive_id:
        drive_url = f"https://drive.google.com/file/d/{drive_id}/view"
        nombre_canal = os.path.basename(root)
        return {
            'Nombre': file,
            'Ruta_Local': path_completo,
            'Drive_ID': drive_id,
            'Drive_URL': drive_url,
            'Canal': nombre_canal
        }
    return None

def actualizar_indice():
    print(f"[{datetime.now()}] Iniciando actualización de índice...")
    archivos_procesados = 0
    nuevos_archivos = 0
    
    # Cargar índice existente para evitar reprocesar todo
    existentes = set()
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existentes.add(row['Ruta_Local'])

    # Recolectar lista de trabajos para procesar en paralelo
    trabajos = []
    print("Escaneando directorios...")
    for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
        if 'Buscador_Libros' in root:
            continue
            
        for file in files:
            if not file.lower().endswith('.pdf') or file.startswith('.'):
                continue
                
            path_completo = os.path.join(root, file)
            if path_completo not in existentes:
                trabajos.append((path_completo, file, root))

    print(f"Encontrados {len(trabajos)} archivos nuevos para procesar.")
    
    if not trabajos:
        print("✅ No hay archivos nuevos para añadir.")
        return

    # Procesar en paralelo (multi-hilo para xattr)
    resultados = []
    print("Extrayendo IDs de Google Drive en paralelo...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for idx, res in enumerate(executor.map(procesar_archivo, trabajos)):
            if res:
                resultados.append(res)
            if (idx + 1) % 1000 == 0:
                print(f"Procesando {idx + 1}/{len(trabajos)} archivos...")

    # Guardar resultados
    modo_archivo = 'a' if os.path.exists(INDEX_FILE) else 'w'
    with open(INDEX_FILE, modo_archivo, newline='', encoding='utf-8') as f:
        fields = ['Nombre', 'Ruta_Local', 'Drive_ID', 'Drive_URL', 'Canal']
        writer = csv.DictWriter(f, fieldnames=fields)
        
        if modo_archivo == 'w':
            writer.writeheader()
        
        for row in resultados:
            writer.writerow(row)
            nuevos_archivos += 1

    print(f"🎉 ¡Proceso finalizado! Se añadieron {nuevos_archivos} nuevos archivos al índice.")

if __name__ == '__main__':
    actualizar_indice()

