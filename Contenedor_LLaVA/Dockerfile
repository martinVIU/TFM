FROM ghcr.io/open-webui/open-webui:ollama

WORKDIR /compartida

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Instalar bash si no está ya disponible
RUN apt-get update && apt-get install -y bash

EXPOSE 3000
EXPOSE 8080
EXPOSE 8888

#ENTRYPOINT [ "jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser" ]