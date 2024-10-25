FROM tensorflow/tensorflow:latest-gpu

WORKDIR /compartida

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Instalar bash si no está ya disponible
RUN apt-get update && apt-get install -y bash

# Exponer puertos
EXPOSE 8888
EXPOSE 22

# No establezcas ENTRYPOINT aquí, permitiendo que el docker-compose.yaml controle el comando
# ENTRYPOINT [ "jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser" ]
