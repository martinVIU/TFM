import subprocess
import json
import os
import tkinter as tk
from tkinter import filedialog, Text
from tkinter import messagebox
import shutil
import platform
import time


# Función que ejecuta el proceso entero, usando Python y contenedores
def ejecutar_proceso():
    # Se guarda la configuración
    save_config('Compartida/config/config.json',True,config)

    # Ejecutar el script Python "extraer_fotogramas.py" EXTRAER FOTOGRAMAS
    try:
        print("Ejecutando extraer_fotogramas.py...")
        subprocess.run(["python", "extraer_fotogramas.py"], check=True)
        print("extraer_fotogramas.py se ejecutó correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar extraer_fotogramas.py: {e}")
        print("ERROR - FIN DEL PROCESO")
        quit()

    # Ejecutar el archivo .bat "contenedor1.bat" CLASIFICADOR
    try:
        print("Ejecutando contenedor1.bat...")
        subprocess.run(["contenedor1.bat"], check=True, shell=True)
        print("contenedor1.bat se ejecutó correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar contenedor1.bat: {e}")
        quit()

    # Ejecutar el archivo .bat "contenedor2.bat" DESCRIPTOR (LLAVA)
    try:
        print("Ejecutando contenedor2.bat...")
        subprocess.run(["contenedor2.bat"], check=True, shell=True)
        print("contenedor1.bat se ejecutó correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar contenedor2.bat: {e}")
        quit()

    # Quitar archivos sobrantes
    print("Borrando fotogramas extraidos")
    borrar_contenido_directorio(config['directorios']['fotogramas'])

    # Ejecutar el archivo "transcriptor_porcentaje.py" Extrae el audio y lo transcribe
    try:
        print("Ejecutando transcriptor_porcentaje.py...")
        subprocess.run(["python", "transcriptor_porcentaje.py"], check=True)
        print("transcriptor_porcentaje.py se ejecutó correctamente.")
    except subprocess.CalledProcessError as e:
        print(f'Error al ejecutar transcriptor_porcentaje.py: {e}')
        print("ERROR - FIN DEL PROCESO")
        quit()
        
    # Ejecutar el archivo "resumir.py" Hace un resumen de la transcripción
    try:
        print("Ejecutando resumir.py...")
        subprocess.run(["python", "resumir.py"], check=True)
        print("resumir.py se ejecutó correctamente.")
    except subprocess.CalledProcessError as e:
        print(f'Error al ejecutar resumir.py: {e}')
        print("ERROR - FIN DEL PROCESO")
        quit()

    # Borrar sobrantes
    print("Borrando extras")
    borrar_contenido_directorio(config['directorios']['videotemp'])

    # Ejecutar el archivo .bat "contenedor3.bat" RAG
    try:
        print("Ejecutando contenedor3.bat...")
        subprocess.run(["contenedor3.bat"], check=True, shell=True)
        print("contenedor3.bat se ejecutó correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar contenedor3.bat: {e}")
        quit()
    print('Proceso completado')


# Función para crear la configuración inicial si no existe el archivo
def save_config(file_path='Compartida/config/config.json',rewrite=False, new_config = {}):
    default_config = {
        "video": {
            "nombre": "video.mp4",
            "idioma": "ES"
        },
        "directorios": {
            "clases_detectadas": "informes",
            "fotogramas": "fotogramas",
            "informes": "informes",
            "incluir_PDF": "incluir_PDF",
            "incluir_txt": "incluir_txt",
            "preguntas": "preguntas",
            "respuestas": "respuestas"
        }
    }

    if not os.path.exists(file_path):
        with open(file_path, 'w') as config_file:
            json.dump(default_config, config_file, indent=4)
        print(f"Archivo de configuración creado: {file_path}")

    if rewrite:
        with open(file_path, 'w') as config_file:
            json.dump(new_config, config_file, indent=4)
        print(f"Archivo de configuración actualizado: {file_path}")

# Vaciar el directorio especificado
def borrar_contenido_directorio(directorio):
    directorio = "Compartida/" + directorio
    try:
        # Verifica si el directorio existe
        if not os.path.exists(directorio):
            print(f"El directorio '{directorio}' no existe.")
            return

        # Itera sobre todos los archivos en el directorio
        for archivo in os.listdir(directorio):
            ruta_archivo = os.path.join(directorio, archivo)
            # Verifica si es un archivo y lo elimina
            if os.path.isfile(ruta_archivo):
                os.remove(ruta_archivo)

    except Exception as e:
        print(f"Ocurrió un error: {e}")

# Función para cargar la configuración almacenada
def read_config(file_path='Compartida/config/config.json'):
    with open(file_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data

# Crear el archivo de configuración si no existe
save_config()
config = read_config()

# Abrir un explorador de archivos en la carpeta solicitada
def abrir_explorador_carpeta(ruta):
    sistema = platform.system()
    if sistema == "Windows":
        os.startfile(ruta)
    elif sistema == "Linux":
        subprocess.Popen(["xdg-open", ruta])

# Función para copiar el vídeo, solo se va a trabajar sobre esta copia
def copiar_video(archivo_video):
    src = archivo_video
    dst = "Compartida/" + config['directorios']['videotemp'] + "/" + config['video']['nombretemp']
    shutil.copy(src, dst)

# Función para escoger el vídeo a analizar
def seleccionar_video():
    video_file = filedialog.askopenfilename(
        title="Seleccione un archivo de video",
        filetypes=[("Archivos de video", "*.mp4 *.avi *.mov *.mkv")]
    )
    if video_file:
        video_btn.config(text=os.path.basename(video_file))
        config['video']['nombre'] = video_file
        copiar_video(video_file)
        save_config()

# Función para abrir la carpeta donde van los archivos PDF a incluir
def adjuntar_pdfs():
    pdf_dir = os.path.join(os.getcwd(), "Compartida", "incluir_pdf")
    if not os.path.exists(pdf_dir):
        messagebox.showerror("Error", f"No se encuentra la carpeta: {pdf_dir}")
        return
    abrir_explorador_carpeta(pdf_dir)

# Función para abrir la carpeta donde van los archivos TXT a incluir
def adjuntar_txt():
    txt_dir = os.path.join(os.getcwd(), "Compartida", "incluir_txt")
    if not os.path.exists(txt_dir):
        messagebox.showerror("Error", f"No se encuentra la carpeta: {txt_dir}")
        return
    abrir_explorador_carpeta(txt_dir)

# Terminar el programa
def salir():
    quit()

# Función que guarda las preguntas escritas por el usuario en un archivo de texto
def guardar_preguntas(archivo_preguntas):
    # Obtener el contenido del TextBox
    texto = pregunta_text.get("1.0", tk.END)  # Obtener desde la primera línea hasta el final
    with open(archivo_preguntas, "w",encoding='utf-8') as f:
        f.write(texto)

#Función asociada al botón Procesar
def procesar():
    preguntas = pregunta_text.get("1.0", tk.END).strip()
    if not preguntas:
        messagebox.showwarning("Advertencia", "Por favor, escriba al menos una pregunta.")
    else:
        messagebox.showinfo("Procesando", "Iniciando el procesamiento...")
    save_config('Compartida/config/config.json',True,config)
    guardar_preguntas("Compartida/" + config['directorios']['preguntas'] + "/preguntas.txt")
    borrar_contenido_directorio(config['directorios']['informes'])
    # Registrar el tiempo de inicio
    inicio = time.time()
    ejecutar_proceso()
    # Registrar el tiempo de finalización
    fin = time.time()

    # Calcular la duración
    duracion = fin - inicio
    archivo_tiempos = "Compartida/" + config['directorios']['informes'] + "/tiempos.txt"
    with open(archivo_tiempos, "a") as f:
        f.write("Tiempo TOTAL," + str(round(duracion, 2)) + "\n")
    cargar_respuestas()
    messagebox.showinfo("Procesando", "Procesamiento completado en " + str(round(duracion,2)) + " segundos")

# Función que carga las respuestas obtenidas en el textbox
def cargar_respuestas():
    archivo_respuestas = "Compartida/" + config['directorios']['respuestas'] + "/respuestas.txt"
    if os.path.exists(archivo_respuestas):
        with open(archivo_respuestas, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            pregunta_text.delete(1.0, tk.END)
            pregunta_text.insert(tk.END, contenido)
    else:
        print(f"No se encontró el archivo: {archivo_respuestas}")

# Función para gestionar el cambio de idioma
def cambiar_idioma():
    idioma_seleccionado = idioma.get()
    print(f"Idioma seleccionado: {idioma_seleccionado}")
    if idioma_seleccionado == "ESPAÑOL":
        config['video']['idioma'] = "ES"
    if idioma_seleccionado == "ENGLISH":
        config['video']['idioma'] = "EN"

# Función para mostrar el mensaje "Acerca de"
def mostrar_acerca_de():
    messagebox.showinfo("Acerca de", "Trabajo de Fin de Master de\nMartín Carlos González Domínguez\nMaster en Big Data\nEdición Octubre 2023-2024")

# Crear la ventana principal
root = tk.Tk()
root.title("TFM Martín - Sistema autónomo comprensivo de clasificación y consulta de contenidos multimedia")
root.geometry("600x700")
root.config(bg="#f0f0f0")

# Crear la barra de menú
menu_bar = tk.Menu(root)

# Añadir un menú "Ayuda"
ayuda_menu = tk.Menu(menu_bar, tearoff=0)
ayuda_menu.add_command(label="Acerca de", command=mostrar_acerca_de)

# Añadir el menú "Ayuda" a la barra de menú
menu_bar.add_cascade(label="Información", menu=ayuda_menu)

# Mostrar la barra de menú en la ventana
root.config(menu=menu_bar)

# Etiqueta "Video a Procesar"
video_label = tk.Label(root, text="Video a Procesar", font=("Arial", 14), bg="#f0f0f0")
video_label.pack(pady=10)

# Botón para seleccionar video
video_btn = tk.Button(root, text="Seleccione Video", command=seleccionar_video, font=("Arial", 12), bg="#007bff", fg="white", width=30)
video_btn.pack(pady=5)

# Botón para adjuntar archivos PDF
pdf_btn = tk.Button(root, text="Adjuntar archivos PDF al procesamiento", command=adjuntar_pdfs, font=("Arial", 12), bg="#28a745", fg="white", width=30)
pdf_btn.pack(pady=15)

# Botón para adjuntar archivos de texto
txt_btn = tk.Button(root, text="Adjuntar archivos de texto", command=adjuntar_txt, font=("Arial", 12), bg="#ffc107", fg="black", width=30)
txt_btn.pack(pady=10)

# Radiobuttons para seleccionar idioma
idioma = tk.StringVar(value="ESPAÑOL")
cambiar_idioma()

radiobutton_frame = tk.Frame(root, bg="#f0f0f0")
radiobutton_frame.pack(pady=10)

radio_es = tk.Radiobutton(radiobutton_frame, text="ESPAÑOL", variable=idioma, value="ESPAÑOL", font=("Arial", 12), bg="#f0f0f0", command=cambiar_idioma)
radio_en = tk.Radiobutton(radiobutton_frame, text="ENGLISH", variable=idioma, value="ENGLISH", font=("Arial", 12), bg="#f0f0f0", command=cambiar_idioma)
radio_es.pack(side="left", padx=20)
radio_en.pack(side="left", padx=20)

# Etiqueta para escribir las preguntas
pregunta_label = tk.Label(root, text="Escriba las preguntas a contestar.\nCada pregunta va separada de la anterior por un Enter", font=("Arial", 12), bg="#f0f0f0", justify="center")
pregunta_label.pack(pady=15)

# Cuadro de texto para las preguntas
pregunta_text = tk.Text(root, height=8, width=50, font=("Arial", 12))
pregunta_text.pack(pady=10)

# Botón para procesar
procesar_btn = tk.Button(root, text="Procesar", command=procesar, font=("Arial", 14), bg="#dc3545", fg="white", width=30, height=2)
procesar_btn.pack(pady=20)

# Botón para salir
salir_btn = tk.Button(root, text="Salir", command=salir, font=("Arial", 14), bg="#000000", fg="white", width=20, height=2)
salir_btn.pack(pady=2)

# Iniciar el bucle principal de la aplicación
root.mainloop()
