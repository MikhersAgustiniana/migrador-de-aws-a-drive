import boto3
import os
import dotenv

dotenv.load_dotenv()


# Configura las credenciales de AWS (asegúrate de configurarlas adecuadamente)
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
aws_session_token = ''  # Deja esto en blanco si no utilizas AWS STS


# Crea un cliente S3
CLIENTE_S3 = boto3.client('s3',
 aws_access_key_id=aws_access_key_id,
 aws_secret_access_key=aws_secret_access_key,
 aws_session_token=aws_session_token)