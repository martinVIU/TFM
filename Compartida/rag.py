#!/usr/bin/env python
# coding: utf-8
import os
import subprocess
import sys
import json
import time
from langchain.schema import Document

# Cargar la configuración almacenada
def read_config(file_path='config/config.json'):
    with open(file_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data

# Cargar la configuración y aplicarla
config = read_config()
archivo_tiempos = config['directorios']['informes'] + "/tiempos.txt"
archivo_respuestas = config['directorios']['respuestas'] + "/respuestas.txt"
archivo_preguntas = config['directorios']['preguntas'] + "/preguntas.txt"
# Guarda el tiempo de inicio
inicio = time.time()

# Iniciar OLLAMA en paralelo y descargar el LLM llama3
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
        print("Ollama2 ha sido iniciado en paralelo.")
    except subprocess.CalledProcessError as e:
        print(f"Error al iniciar Ollama en paralelo: {e}")

    try:
        # Ejecutar el comando para iniciar ollama
        subprocess.run(["ollama", "pull","mistral"], check=True)
        print("Modelo LLaVA instalado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar LLaVA: {e}")

    try:
        # Ejecutar el comando para iniciar ollama
        subprocess.run(["ollama", "pull","llama3"], check=True)
        print("Modelo LLaVA instalado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar LLaVA: {e}")

#Iniciar OLLAMA
start_ollama()

# Instalar la librería si no está disponible
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements3.txt"])

# Instalar la librería si no está disponible
subprocess.check_call([sys.executable, "-m", "pip", "install", "--q", "unstructured", "langchain"])

# Instalar la librería si no está disponible
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--q', 'unstructured[all-docs]'])

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import OnlinePDFLoader
from langchain.document_loaders import UnstructuredFileLoader

# Ruta al directorio que contiene los archivos .txt y PDF
directory_path_txt = "incluir_txt"
directory_path_pdf = "incluir_PDF"
directory_path_informes = "informes"

data_text=[]
data_pdf=[]

# Listar todos los archivos .txt en el directorio excepto "tiempos.txt"
txt_files_informes = [f for f in os.listdir(directory_path_informes) if f.endswith('.txt') and f != "tiempos.txt"]

# Procesar los archivos TXT presentes en el directorio de informes
if txt_files_informes:
    for txt_file in txt_files_informes:
        print("\nArchivo INFORME: " + txt_file + "\n")
        file_path = os.path.join(directory_path_informes, txt_file)
        print("\nArchivo: " + txt_file + "    RUTA: " + file_path + " \n")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:  # Intenta con 'utf-8' o 'latin-1'
                content = file.read()
                data_text.append({"text": content})
        except UnicodeDecodeError as e:
            print(f"Error de decodificación en el archivo {txt_file}: {e}")
        except Exception as e:
            print(f"Error al procesar el archivo {txt_file}: {e}")
else:
    print("No se encontraron archivos .txt en el directorio")


# Listar todos los archivos .txt en el directorio de TXT a incluir
txt_files_incluir = [f for f in os.listdir(directory_path_txt) if f.endswith('.txt')]

# Procesar los archivos TXT presentes en el directorio
if txt_files_incluir:
    for txt_file in txt_files_incluir:
        print("\nArchivo TXT: " + txt_file + "\n")
        file_path = os.path.join(directory_path_txt, txt_file)
        print("\nArchivo: " + txt_file + "    RUTA: " + file_path + " \n")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:  # Intenta con 'utf-8' o 'latin-1'
                content = file.read()
                data_text.append({"text": content})
        except UnicodeDecodeError as e:
            print(f"Error de decodificación en el archivo {txt_file}: {e}")
        except Exception as e:
            print(f"Error al procesar el archivo {txt_file}: {e}")
else:
    print("No se encontraron archivos .txt en el directorio")

# Listar todos los archivos .pdf en la carpeta PDF_incluir
pdf_files = [f for f in os.listdir(directory_path_pdf) if f.endswith('.pdf')]

# Procesar los archivos PDF presentes en el directorio
if pdf_files:
    for pdf_file in pdf_files:
        file_path = os.path.join(directory_path_pdf, pdf_file)
        # Cargar el archivo PDF
        loader = UnstructuredPDFLoader(file_path=file_path)
        pdf_data = loader.load()
        data_pdf.extend(pdf_data)  # Agregar el contenido cargado a la lista `data`
else:
    print("No se encontraron archivos PDF en el directorio")

# Instalar los LLM necesarios
try:
    # Instalar LLM nomic-embed-text
    subprocess.run(["ollama", "pull", "nomic-embed-text"], check=True)
    print("Modelo nomic-embed-text instalado correctamente.")
except subprocess.CalledProcessError as e:
    print(f"Error al instalar nomic-embed-text: {e}")

# Instalar la librería si no está disponible
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--q', 'chromadb'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--q', 'langchain-text-splitters'])

from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Trocear la información
text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)

# Almacenar el contenido de los PDF
print("\n ALMACENANDO PDFs \n")
if len(data_pdf)>0:
    #Almacenar el texto de los PDF
    chunks = text_splitter.split_documents(data_pdf)

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model="llama3",show_progress=True),
        collection_name="local-rag"
    )

# Almacenar el contenido de los TXT
print("\n ALMACENANDO TEXTOS \n")

# Convertir los diccionarios en objetos Document
documents = [Document(page_content=entry["text"]) for entry in data_text]

chunks = text_splitter.split_documents(documents)

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="llama3",show_progress=True),
    collection_name="local-rag"
)

from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

# Seleccionar LLM de procesamiento, inicialmente se usó mistral
#local_model = "mistral"
local_model = "llama3"
llm = ChatOllama(model=local_model)

# Establecer plantilla
QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""You are an AI language model assistant. Your task is to generate five
    different versions of the given user question to retrieve relevant documents from
    a vector database. By generating multiple perspectives on the user question, your
    goal is to help the user overcome some of the limitations of the distance-based
    similarity search. Provide these alternative questions separated by newlines.
    Original question: {question}""",
)

retriever = MultiQueryRetriever.from_llm(
    vector_db.as_retriever(), 
    llm,
    prompt=QUERY_PROMPT
)

# Establecer plantilla RAG
template = """Answer the question based ONLY on the following context:
{context}
Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Cargar las preguntas desde el archivo preguntas.txt
with open(archivo_preguntas, 'r', encoding='utf-8') as file:
    preguntas = file.read().splitlines()  # Dividir el archivo en una lista de preguntas, separadas por \n

# Inicializar una lista para almacenar las respuestas
respuestas = []

# Iterar sobre las preguntas y obtener las respuestas
for pregunta in preguntas:
    if pregunta.strip():  # Ignorar líneas vacías
        respuesta = chain.invoke(pregunta)  # Ejecutar chain.invoke() para cada pregunta
        respuestas.append(f"Pregunta: {pregunta}\nRespuesta: {respuesta}\n\n")  # Almacenar en una lista

# Guardar las respuestas en un archivo de texto
with open(archivo_respuestas, 'w', encoding='utf-8') as file:
    file.writelines(respuestas)

print("Las respuestas se han guardado en el archivo respuestas.txt")

# Borrar todas las colecciones de la base de datos
vector_db.delete_collection()

# Registrar el tiempo de finalización
fin = time.time()

# Calcular la duración
duracion = fin - inicio

# Registrar el tiempo del proceso
with open(archivo_tiempos, "a") as f:
    f.write( "Contestar Preguntas (RAG)," + str(round(duracion,2)) + "\n")

print(f"Duración del proceso: {duracion:.4f} segundos")