FROM ghcr.io/open-webui/open-webui:ollama

WORKDIR /compartida

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Instalar bash si no está ya disponible
RUN apt-get update && apt-get install -y bash libmagic1 libmagic-dev poppler-utils

EXPOSE 3000
EXPOSE 8080
EXPOSE 8888

# No establezcas ENTRYPOINT aquí, permitiendo que el docker-compose.yaml controle el comando
#ENTRYPOINT [ "jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser" ]