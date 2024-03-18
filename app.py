import os
import time
import random
import dotenv
from pydrive2.files import ApiRequestError

from GoogleDrive.GoogleDrive import subir_archivo, crear_carpeta
from AWS.descargador_de_aws import CLIENTE_S3

dotenv.load_dotenv()

carpeta_drive_id = os.getenv("folder_id")

# Especifica el nombre del bucket de S3 que deseas descargar
bucket_name = "clarity-buho-backups"

CONTENIDO_TOTAL_S3 = CLIENTE_S3.list_objects_v2(Bucket=bucket_name)

# import pdb; pdb.set_trace()
def descargar_archivo(bucket_name, key):
    print(f'Descargando: {key}')
    os.makedirs(os.path.dirname(f'backups/{key}'), exist_ok=True)
    try:
        # Eliminar cualquier identificador adicional al final del nombre del archivo
        CLIENTE_S3.download_file(bucket_name, Key=key, Filename=f"backups/{key}")
        return key
    except FileNotFoundError as e:
        print(f'ERROR: No se pudo encontrar el archivo en S3: {e}')
        return None

def subir_archivo_local_a_drive(local_path, carpeta_drive_id):
    print(f'Subiendo: {local_path}')
    nuevo_id_carpeta = crear_carpeta(os.path.dirname(local_path), carpeta_drive_id)
    try:
        subir_archivo(f"backups/{local_path}", nuevo_id_carpeta)
        os.remove(f"backups/{local_path}")  # Borra el archivo de la carpeta local después de subirlo a Drive
    except ApiRequestError as e:
        if 'userRateLimitExceeded' in str(e):
            # Si se supera el límite de velocidad de solicitud del usuario, aplicamos la estrategia de retirada exponencial
            n = 0
            while True:
                wait_time = min(((2 ** n) + random.randint(0, 1000)), 64000) / 1000  # Tiempo de espera en segundos
                print(f'Error 403: Límite de velocidad de solicitud del usuario excedido. Esperando {wait_time} segundos antes de volver a intentar...')
                time.sleep(wait_time)
                n += 1
                try:
                    subir_archivo(f"backups/{local_path}", nuevo_id_carpeta)
                    os.remove(f"backups/{local_path}")
                    break  # Si la subida tiene éxito, salimos del bucle
                except ApiRequestError as e:
                    if 'userRateLimitExceeded' not in str(e):
                        print(f'Error desconocido al subir el archivo: {e}')
                        break  # Si se produce un error diferente, salimos del bucle

### Código principal
for obj in CONTENIDO_TOTAL_S3.get('Contents', []):
    key = obj['Key'].rstrip('/')
    archivo_local = descargar_archivo(bucket_name, key)
    subir_archivo_local_a_drive(archivo_local, carpeta_drive_id)

### PARA PRUEBAS DE DRIVE SUBIR CUALQUIER COSA
# prueba = 'python-prueba.py'
# subir_archivo(f"backups/{prueba}", carpeta_drive_id)