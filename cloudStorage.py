import os, uuid, time
from datetime import datetime

import cv2
import tempfile
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__


def init_blob_client():
    """
    Initialize the blob service from Azure storage connection string.

    Ensures connection string is retrieved securely from env variables.
    """

    connect_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    if not connect_string:
        raise EnvironmentError("AZURE_STORAGE_CONNECTION_STRING env variable not set.")

    blob_service_client = BlobServiceClient.from_connection_string(connect_string)

    return blob_service_client

def create_azure_container(container_name = "alerts"):

    blob_service_client = init_blob_client()
    try:
        container_client = blob_service_client.create_container(container_name)
    except Exception as e:
        print(f"Error creating container {container_name}: {e}")

def upload_blob(video_array, video_name, width, height, fps):

    blob_service_client = init_blob_client()
    current_time = datetime.now().strftime("%H:%M:%S")
    current_day = datetime.today().strftime("%Y-%m-%d")
    
    video_name = f"{video_name} {current_day} {current_time}.mp4"
    blob_client = blob_service_client.get_blob_client(container="alerts", blob=video_name)

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video_file:
            output = cv2.VideoWriter(temp_video_file.name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height), True)
            for i in video_array:
                output.write(i)
            output.release()

            with open(temp_video_file.name, "rb") as data:
                # Uploading video to the cloud
                blob_client.upload_blob(data)

        os.remove(temp_video_file.name) # removing temporary file after upload
        return blob_client.url
    
    except Exception as e:
        print(f"Error uploading video {video_name}: {e}")
        return None

    



