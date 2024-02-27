import os
import dotenv


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
        return f"backups/{key}"
    except FileNotFoundError as e:
        print(f'ERROR: No se pudo encontrar el archivo en S3: {e}')
        return None

def subir_archivo_local_a_drive(local_path, carpeta_drive_id):
    print(f'Subiendo: {key}')
    nuevo_id_carpeta = crear_carpeta(os.path.dirname(local_path.split("backups/")[1].split("/clarity_")[0]), carpeta_drive_id)
    subir_archivo(local_path, nuevo_id_carpeta)
    os.remove(local_path)  # Borra el archivo de la carpeta local después de subirlo a Drive

# Código principal
for obj in CONTENIDO_TOTAL_S3.get('Contents', []):
    key = obj['Key'].rstrip('/')
    archivo_local = descargar_archivo(bucket_name, key)
    subir_archivo_local_a_drive(archivo_local, carpeta_drive_id)