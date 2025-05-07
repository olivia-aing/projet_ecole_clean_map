!/bin/bash

# Ce script permet de lancer la machine virtuelle
# avec tout le nécessaire pour faire l'environnement virtuel


python3 -m venv venv;
source venv/bin/activate;
pip install -r requirements.txt;


# Découverte : on ne peut pas utiliser de source dans le fichier bash
# qui soit conservé sur le terminal, donc... euh... rip ? Je suppose ?
# Ou en tout cas, à creuser, mais je n'ai plus vraiment le temps

