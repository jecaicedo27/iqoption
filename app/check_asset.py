from app.connection import IQConnector
from app.config import DEFAULT_ASSET

def check_asset():
    connector = IQConnector()
    if not connector.connect():
        return

    print(f"Verificando estado de {DEFAULT_ASSET}...")
    
    # Intentar obtener info del activo o ver si está abierto
    # La librería suele tener 'get_all_open_time'
    
    all_open = connector.api.get_all_open_time()
    
    # Buscar nuestro activo en las listas
    found = False
    for type_name, assets in all_open.items():
        if DEFAULT_ASSET in assets:
            print(f"Activo {DEFAULT_ASSET} encontrado en categoría: {type_name}")
            print(f"Info: {assets[DEFAULT_ASSET]}")
            if assets[DEFAULT_ASSET]['open']:
                 print(">> EL ACTIVO ESTÁ ABIERTO AHORA MISMO.")
                 found = True
            else:
                 print(">> EL ACTIVO ESTÁ CERRADO.")
    
    if not found:
        print(f"Activo {DEFAULT_ASSET} no encontrado en listas de apertura.")

if __name__ == "__main__":
    check_asset()
