#!/usr/bin/env python
# coding: utf-8

# Instalar librerias necesarias
import subprocess
import sys
import json
import time

# Registrar el tiempo de inicio
inicio = time.time()

# Instalar la libreria necesaria en el sistema
subprocess.check_call(["apt-get", "install", "-y", "libgl1-mesa-glx"])

# Intenta instalar la librería si no está disponible
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Ejecuta el comando "python3 setup.py install" desde Python
subprocess.check_call([sys.executable, "setup.py", "install"])

import mrcnn
import mrcnn.config
import mrcnn.model
import mrcnn.visualize
import cv2
import os

import glob
import shutil

# Cargar la configuración por defecto
def read_config(file_path='config/config.json'):
    with open(file_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data


from importlib import reload  # Python 3.4+
mrcnn.visualize = reload(mrcnn.visualize)

# Se pueden usar las clases definidas en coco_labels o seleccionar unas cuantas
#CLASS_NAMES = open("coco_labels.txt").read().strip().split("\n")
CLASS_NAMES = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

# Configurar la Mask R-CNN con los pesos de COCO
class SimpleConfig(mrcnn.config.Config):
    # Give the configuration a recognizable name
    NAME = "coco_inference"
    
    # set the number of GPUs to use along with the number of images per GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

    # Number of classes = number of classes + 1 (+1 for the background). The background class is named BG
    NUM_CLASSES = len(CLASS_NAMES)

# Initialize the Mask R-CNN model for inference and then load the weights.
# This step builds the Keras model architecture.
model = mrcnn.model.MaskRCNN(mode="inference", 
                             config=SimpleConfig(),
                             model_dir=os.getcwd()+'/mrcnn')

# Load the weights into the model.
# Download the mask_rcnn_coco.h5 file from this link: https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5
model.load_weights(filepath="mask_rcnn_coco.h5", 
                   by_name=True)

config = read_config()

# Ruta al directorio 'fotogramas'
directorio_fotogramas = config['directorios']['fotogramas']

# Obtener la lista de todos los archivos .jpg en el directorio 'fotogramas'
archivos_jpg = glob.glob(os.path.join(directorio_fotogramas, "*.jpg"))

# Diccionario inicial de clases
clases_unicas = []

# Aplicar la función a cada archivo .jpg
contador = 0
for archivo_jpg in archivos_jpg:
    contador +=1
    # load the input image, convert it from BGR to RGB channel
    filename = archivo_jpg
    image = cv2.imread(filename)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    print("procesando el archivo " + archivo_jpg + "(" + str(contador) + "/" + str(len(archivos_jpg)) + ")" ) 
    
    # Perform a forward pass of the network to obtain the results
    r = model.detect([image], verbose=0)
    
    # Get the results for the first image.
    r = r[0]
    '''
    # Para debug
    # Visualize the detected objects.
    mode=0
    if mode == 0:
        mrcnn.visualize.display_instances(image=image, 
                                          boxes=r['rois'], 
                                          masks=r['masks'], 
                                          class_ids=r['class_ids'], 
                                          class_names=CLASS_NAMES, 
                                          scores=r['scores'])
    if mode == 1:
        mrcnn.visualize.display_results(image=image, 
                                          boxes=r['rois'], 
                                          masks=r['masks'], 
                                          class_ids=r['class_ids'], 
                                          class_names=CLASS_NAMES, 
                                          scores=r['scores'],
                                          save_dir=os.getcwd(),
                                          img_name=filename[:-4]+'_predicted'+filename[-4:])

    '''
    # Convertir el array de NumPy a un conjunto para eliminar duplicados
    valores_unicos = set(r['class_ids'])
    
    # Añadir los valores únicos a la lista, asegurando que no haya duplicados
    clases_unicas.extend(valores_unicos)

# Eliminar la posiblidad de duplicados entre fotogramas
clases_unicas = list(set(clases_unicas))
# In[68]:
#r['class_ids']
print ("clases detectadas:\n")
print(r['class_ids'])

clase_correspondiente = [CLASS_NAMES[i] for i in clases_unicas]

print ("las clases a las que corresponde: \n ")
print (clase_correspondiente)       

# Cargar clases desde el archivo, si existe
archivo_clases = config['directorios']['informes'] + "/clases_detectadas.txt"
archivo_tiempos = config['directorios']['informes'] + "/tiempos.txt"
clases_existentes = set()

# Añadir nuevas clases al conjunto de clases existentes
clases_existentes.update(clase_correspondiente)

# Guardar las clases combinadas y sin duplicados en el archivo
with open(archivo_clases, "w") as f:
    for clase in sorted(clases_existentes):  # Guardar ordenadas (opcional)
        f.write(clase + "\n")

# Registrar el tiempo de finalización
fin = time.time()

# Calcular la duración
duracion = fin - inicio

# Registrar la duración del proceso
with open(archivo_tiempos, "a") as f:
    f.write( "Clasificación de fotogramas," + str(round(duracion,2)) + "\n")

print(f"Duración del proceso: {duracion:.4f} segundos")