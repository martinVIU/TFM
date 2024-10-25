FROM ghcr.io/open-webui/open-webui:ollama

WORKDIR /tf-martin-llama

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 3000
EXPOSE 8080
EXPOSE 8888

ENTRYPOINT [ "jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser" ]