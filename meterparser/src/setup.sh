#!/bin/bash
set -e # exit on any error
# Setup base
apt-get clean
apt-get update 
# apt-get install -y --no-install-recommends gnupg2 
# curl -s https://notesalexp.org/debian/alexp_key.asc | gpg --dearmor > /usr/share/keyrings/tesseract-archive-keyring.gpg 
# echo "deb [signed-by=/usr/share/keyrings/tesseract-archive-keyring.gpg] https://notesalexp.org/tesseract-ocr5/bullseye/ bullseye main" >> /etc/apt/sources.list.d/tesseract.list 

apt-get install -y --no-install-recommends python3-pip #    tesseract-ocr 
pip3 install --no-cache-dir -r /src/requirements.txt 
rm -fr /tmp/* /var/{cache,log}/* /var/lib/apt/lists/* 