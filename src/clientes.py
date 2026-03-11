import csv
import os 

def cargar_clientes():
    clientes = []
    ruta_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "data", "clientes.csv")
    with open(ruta_csv, newline="", encoding="utf-8") as archivo:
        
        lector = csv.DictReader(archivo)

        for fila in lector:
            clientes.append(fila)
        return clientes
    
clientes = cargar_clientes()
for cliente in clientes:
    print(cliente["nombre"], "-", cliente["email"])
 