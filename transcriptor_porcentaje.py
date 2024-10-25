import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import soundfile as sf
import subprocess
import time
import json

# Cargar la configuración almacenada
def read_config(file_path='Compartida/config/config.json'):
    with open(file_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data

config = read_config()
# Establecer los archivos e idioma a utilizar
archivo_tiempos = "Compartida/" + config['directorios']['informes'] + "/tiempos.txt"
mp4_file = "Compartida/" + config['directorios']['videotemp'] + "/" + config['video']['nombretemp']
lang = config['video']['idioma']

# Guardar el tiempo de inicio
start_time = time.time()

# Establecer si se usa CUDA o CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

# Seleccionar LLM según idioma
if lang == 'ES':
    # load the model (Spanish)
    processor = WhisperProcessor.from_pretrained("clu-ling/whisper-large-v2-spanish")
    model = WhisperForConditionalGeneration.from_pretrained("clu-ling/whisper-large-v2-spanish").to(device)
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="es", task="transcribe")

if lang == 'EN':
    # load the model (English)
    processor = WhisperProcessor.from_pretrained("openai/whisper-large")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large").to(device)
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="en", task="transcribe")

# Función para convertir mp4 a wav usando ffmpeg
def convert_mp4_to_wav(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-y', '-ar', '16000', '-ac', '1', output_file]
    subprocess.run(command, check=True)

# Convertir el archivo MP4 a WAV
wav_file = mp4_file[:-4] + ".wav"
convert_mp4_to_wav(mp4_file, wav_file)

# Leer el archivo WAV
audio_input, sampling_rate = sf.read(wav_file)

# Dividir el audio en segmentos
segment_length = 30 * sampling_rate  # Segmento de 30 segundos
audio_segments = [audio_input[i:i + segment_length] for i in range(0, len(audio_input), segment_length)]

# Transcribir cada segmento y combinar las transcripciones
transcriptions = []
batch_size = 1  # Número de segmentos a procesar en batch

total_segments = len(audio_segments)
print("Transcribiendo , son " + str(len(audio_segments)) + " segmentos\n")

# Iniciar el procesamiento por lotes
for i in range(0, total_segments, batch_size):
    batch_segments = audio_segments[i:i + batch_size]
    batch_inputs = [processor(segment, sampling_rate=sampling_rate, return_tensors="pt").input_features for segment in
                    batch_segments]
    batch_inputs = torch.cat(batch_inputs).to(device)

    predicted_ids = model.generate(batch_inputs, forced_decoder_ids=forced_decoder_ids)
    batch_transcriptions = processor.batch_decode(predicted_ids, skip_special_tokens=True)

    transcriptions.extend(batch_transcriptions)

    # Mostrar porcentaje de progreso y segmento actual
    current_segment = min(i + batch_size, total_segments)
    progress = current_segment / total_segments * 100
    print(f"Progreso: {progress:.2f}% ({current_segment}/{total_segments})")

# Combinar todas las transcripciones
full_transcription = " ".join(transcriptions)

# Guardar el tiempo de finalización
end_time = time.time()

# Calcular la duración total
execution_time = end_time - start_time

import sys
import io

# Asegurarse de que la salida estándar utiliza utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Tu código completo con la modificación para escribir en utf-8
with open(mp4_file[:-4] + '.txt', 'w', encoding='utf-8') as f:
    f.write(full_transcription)

# Mostrar la transcripción y el tiempo de ejecución
print("\n")
print(full_transcription)
print(f"\nEl código tomó {execution_time:.2f} segundos en ejecutarse.")

# Guardar el tiempo de procesamiento
with open(archivo_tiempos, "a") as f:
    f.write( "Transcripción de fotogramas," + str(round(execution_time,2)) + "\n")

print(f"Duración del proceso: {execution_time:.4f} segundos")
