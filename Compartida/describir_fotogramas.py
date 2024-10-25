#!/usr/bin/env python
# coding: utf-8
import glob
import os
import time
import json
# Registrar el tiempo de inicio
inicio = time.time()

import subprocess
import sys

# Cargar la configuración almacenada
def read_config(file_path='config/config.json'):
    with open(file_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data

# Iniciar Ollama en paralelo y descargar eL LLM llava
# Se ejecuta dos veces el pull porque no siempre conecta a la primera
def start_ollama():
    try:
        # Ejecutar el comando para iniciar ollama
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
        print("Ollama ha sido iniciado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar Ollama: {e}")

    try:
        # Ejecutar el comando para iniciar ollama
        subprocess.Popen(["ollama", "start"])
        print("Ollama ha sido iniciado en paralelo.")
    except subprocess.CalledProcessError as e:
        print(f"Error al iniciar Ollama en paralelo: {e}")

    try:
        # Ejecutar el comando para iniciar ollama
        subprocess.run(["ollama", "pull","llava"], check=True)
        print("Modelo LLaVA instalado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar LLaVA: {e}, PROBANDO DE NUEVO")
        try:
            # Ejecutar el comando para iniciar ollama
            subprocess.run(["ollama", "pull", "llava"], check=True)
            print("Modelo LLaVA instalado correctamente.")
        except subprocess.CalledProcessError as e:
            print(f"Error al instalar LLaVA: {e}")

# Iniciar OLLAMA
print("\nINICIANDO OLLAMA\n")
start_ollama()

# Esperar a que se inicie ollama correctamente
time.sleep(2)

# Cargar y aplicar la configuración
config = read_config()
archivo_tiempos = config['directorios']['informes'] + "/tiempos.txt"
archivo_descripciones = config['directorios']['informes'] + "/descripciones.txt"
# Ruta al directorio 'fotogramas'
directorio_fotogramas = config['directorios']['fotogramas']

from PIL import Image
import ollama

# Preparar el archivo de las descripciones
with open(archivo_descripciones, "a") as f:
    f.write("")

# Generar la descripción mediante el LLM
def generate_text(instruction, file_path):
    result = ollama.generate(
        model='llava',
        prompt=instruction,
        images=[file_path],
        stream=False
    )['response']
    img=Image.open(file_path, mode='r')
    img = img.resize([int(i/1.2) for i in img.size])
    #display(img)
    respuestas = []
    for i in result.split('.'):
        respuestas.append(i)
    # Filtrar elementos vacíos
    respuestas = list(filter(lambda x: x != '' and x != ' ', respuestas))

    return respuestas

#Procesar los fotogramas
# Obtener la lista de todos los archivos .jpg en el directorio 'fotogramas'
archivos_jpg = glob.glob(os.path.join(directorio_fotogramas, "*.jpg"))

# Definir el prompt en función del idioma
instruction = "Describe la imagen lo mejor y más detalladamente que puedas. La respuesta tiene que estar en español."

if config['video']['idioma'] == 'ES':
    instruction = "Describe la imagen lo mejor y más detalladamente que puedas. La respuesta tiene que estar en español."

if config['video']['idioma'] == 'EN':
    instruction = "Describe the image as best and as detailed as you can. The answer must be in English."


# Aplicar la función a cada archivo .jpg
contador = 0
for archivo_jpg in archivos_jpg:
    contador +=1
    file_path = archivo_jpg
    print("procesando el archivo " + archivo_jpg + "(" + str(contador) + "/" + str(len(archivos_jpg)) + ")")
    respuestas = generate_text(instruction, file_path)
    # Añadir la descripción al archivo de descripciones
    with open(archivo_descripciones, "a") as f:
        f.write( file_path + ": " + str(respuestas) + "\n")

    # Añadir un pequeño retraso para garantizar serialización y evitar saturar el modelo
    time.sleep(1)

# Registrar el tiempo de finalización
fin = time.time()

# Calcular la duración
duracion = fin - inicio

# Registrar la duración del proceso
with open(archivo_tiempos, "a") as f:
    f.write( "Descripción de fotogramas," + str(round(duracion,2)) + "\n")

print(f"Duración del proceso: {duracion:.4f} segundos")


