import os
import json
import config

def load_data_user():
    if not os.path.exists(config.DATA_FILE):
        return [ ]
    with open(config.DATA_FILE, "r") as file:
        return (json.load(file))
    #Transforma json (string) em dicionário
        
def save_data_user(data):
    with open(config.DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
    #Transforma dicionário em json string



def load_data_fav():
    if not os.path.exists(config.ATUAL_FILE):
        return [ ]
    with open(config.ATUAL_FILE, "r") as file:
        return (json.load(file))
    
def save_data_fav(data):
    with open(config.ATUAL_FILE, "w") as file:
        json.dump(data, file, indent=4)	    