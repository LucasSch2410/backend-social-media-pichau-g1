import os
from google.cloud import storage
from dotenv import load_dotenv
from ..config import settings

load_dotenv()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.google_application_credentials

bucket_name = 'pichau_social_media'

storage_client = storage.Client()

def upload_to_bucket(blob_name, file_path):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.cache_control = 'no-cache'

        blob.upload_from_filename(file_path)
        return True
    except Exception as e:
        raise Exception(e)
    
def download_file_from_bucket(blob_name, file_path):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        with open(file_path, 'wb') as f:
            storage_client.download_blob_to_file(blob, f)
        return True
    except Exception as e:
        raise Exception(e)
    
def delete_from_bucket(blob_name, user_id, typeSocial):

    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f'{user_id}/{typeSocial}/{blob_name}')
        generation_match_precondition = None

        blob.reload()  
        generation_match_precondition = blob.generation

        blob.delete(if_generation_match=generation_match_precondition)

    except Exception as e:
        raise Exception(e)

def verify_template(typeSocial, user_id):

    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f'{user_id}/template-{typeSocial}')
        
        if blob.exists():
            return f'https://storage.googleapis.com/pichau_social_media/{user_id}/template-{typeSocial}'
         
        return False
    except Exception as e:
        raise Exception(e)