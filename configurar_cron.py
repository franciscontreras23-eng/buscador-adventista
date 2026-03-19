import subprocess

# Comando que queremos agregar
# 0 0 * * 5 => Viernes a las 12:00 AM
cron_cmd = '0 0 * * 5 cd "/Users/francis.contreras23/Library/CloudStorage/GoogleDrive-secretariosureste23@gmail.com/Mi unidad/Documentos Francis/Theology/Articulos, libros y otros documentos/Buscador_Libros" && /usr/bin/python3 actualizar_buscador.py >> cron_log.txt 2>&1'

try:
    # 1. Obtener el crontab actual
    res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    cron_actual = res.stdout
    
    # 2. Verificar si ya existe
    if "actualizar_buscador.py" in cron_actual:
        print("✅ La tarea programada ya estaba configurada.")
    else:
        # Añadir al final
        nuevo_cron = cron_actual.rstrip('\n') + '\n' + cron_cmd + '\n'
        
        # 3. Guardar de nuevo
        p = subprocess.run(["crontab", "-"], input=nuevo_cron, text=True, capture_output=True)
        if p.returncode == 0:
            print("📅 Tarea programada configurada con éxito para los viernes a las 12:00 AM.")
        else:
            print(f"❌ Error al configurar cron: {p.stderr}")
            
except Exception as e:
    print(f"❌ Error general: {e}")
