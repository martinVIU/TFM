import time
import json
from transformers import WhisperProcessor, WhisperForConditionalGeneration, T5Tokenizer, T5ForConditionalGeneration

#Cargar la configuración almacenada
def read_config(file_path='Compartida/config/config.json'):
    with open(file_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data

config = read_config()
# Establecer los archivos a utilizar de logs
archivo_tiempos = "Compartida/" + config['directorios']['informes'] + "/tiempos.txt"
archivo_resumen = "Compartida/" + config['directorios']['informes'] + "/resumen.txt"

# Guardar el tiempo de inicio
start_time = time.time()

# Cargar el archivo de la transcripción
f = open("Compartida/" + config['directorios']['videotemp'] + "/" + config['video']['nombretemp'][:config['video']['nombretemp'].rfind('.') ] + ".txt", "r")
full_transcription = f.readlines()

# Resumir el texto utilizando el modelo T5
summary_tokenizer = T5Tokenizer.from_pretrained("t5-small")
summary_model = T5ForConditionalGeneration.from_pretrained("t5-small")

# Preparar el texto para resumen
text = ' '.join(map(str, full_transcription))
input_text = "summarize: " + text
input_ids = summary_tokenizer.encode(input_text, return_tensors="pt", max_length=1024, truncation=True) #antes 512

# Generar el resumen
#summary_ids = summary_model.generate(input_ids, max_length=150, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
summary_ids = summary_model.generate(input_ids, max_length=500, min_length=100, length_penalty=2.0, num_beams=4, early_stopping=True)
summary = summary_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Mostrar el resumen creado
print("\nResumen:\n")
print(summary)

# Guardar el resumen
with open(archivo_resumen, "w") as f:
    f.write(summary)

# Guardar el tiempo de finalización
end_time = time.time()

# Calcular la duración total y almacenarla
execution_time = end_time - start_time

with open(archivo_tiempos, "a") as f:
    f.write( "Resumen transcripción," + str(round(execution_time,2)) + "\n")

print(f"Duración del proceso: {execution_time:.4f} segundos")