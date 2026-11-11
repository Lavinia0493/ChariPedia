import os

#Diretórios para arquivo JSON

#Recuperar diretório do arquivo app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Definir o local do arquivo JSON com base no diretório do app.py
DATA_FILE = os.path.join(BASE_DIR, "models", "data", "dados.json")
ATUAL_FILE = os.path.join(BASE_DIR, "models", "data", "atual.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "image")
TIPOS_IMAGEM = set(['png', 'jpg', 'jpeg', 'gif'])