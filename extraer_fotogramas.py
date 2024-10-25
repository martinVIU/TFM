import subprocess
import sys
import json
# instalar la librería si no está disponible
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

import cv2
import os
import time

# Registrar el tiempo de inicio
inicio = time.time()

#Función para extraer los fotogramas a un directorio, estableciendo el número de FPS a extraer
def extract_frames(video_path, output_folder, frames_per_second=1):
    # Crea la carpeta de salida si no existe
    os.makedirs(output_folder, exist_ok=True)

    # Inicia el temporizador
    start_time = time.time()

    # Abre el video
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"Error al abrir el video: {video_path}")
        sys.exit(1)

    # Obtiene la tasa de frames por segundo (fps) del video
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))

    # Calcula el intervalo de frames que corresponde al número de frames por segundo deseados
    frame_interval = max(1, int(fps / frames_per_second))

    frame_count = 0
    extracted_count = 0

    print("Extrayendo fotogramas...")

    # Bucle principal para extraer fotogramas
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break  # Salimos si no hay más frames

        # Extrae un fotograma cada 'frame_interval'
        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{extracted_count}.jpg")
            cv2.imwrite(frame_filename, frame)
            extracted_count += 1

        frame_count += 1

    # Libera los recursos del video
    video_capture.release()

    # Calcula el tiempo total del proceso
    elapsed_time = time.time() - start_time
    print(f"Se han extraído {extracted_count} fotogramas en {elapsed_time:.2f} segundos.")

# Cargar la configuración almacenada
def read_config(file_path='Compartida/config/config.json'):
    with open(file_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data

# Crear el archivo de configuración si no existe
config = read_config()
print(config)
# Uso del script
video_path = "./Compartida/" + config['directorios']['videotemp'] + "/" + config['video']['nombretemp'] # Reemplaza con la ruta de tu video
output_folder = "./Compartida/" + config['directorios']['fotogramas'] # Carpeta donde se guardarán los fotogramas
frames_per_second = 1  # Modifica este valor para cambiar la cantidad de fotogramas por segundo
archivo_tiempos = "Compartida/" + config['directorios']['informes'] + "/tiempos.txt"

# Extraer los fotogramas
extract_frames(video_path, output_folder, frames_per_second)

# Registrar el tiempo de finalización
fin = time.time()

# Calcular la duración
duracion = fin - inicio

# Almacenar la duración del proceso
with open(archivo_tiempos, "w") as f:
    f.write( "Extracción de fotogramas," + str(round(duracion,2)) + "\n")