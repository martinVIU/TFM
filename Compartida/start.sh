#!/bin/bash

echo "Iniciando script..."

# Instalar el servidor SSH y configurar
apt-get update && apt-get install -y openssh-server
mkdir -p /var/run/sshd
echo 'root:password' | chpasswd
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Iniciar el servicio SSH
service ssh start

#Realizar ejecución automatica de un script python para encadenar
exec python clasificador_automatico.py

# Iniciar JupyterLab
#exec jupyter lab --ip=0.0.0.0 --allow-root --no-browser

