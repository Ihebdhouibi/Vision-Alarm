import os, uuid, time
from datetime import datetime

import cv2
import numpy as np
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

def upload_blob(videoArray, videoName, width, height, fps):

    blob_service_client = init_blob_client()
    current_time = datetime.now()
    current_day = datetime.today()
    current_time = current_time.strftime("%H:%M:%S")
    videoName = videoName + " " + str(current_day) + " "+ current_time + ".mp4"
    blob_client = blob_service_client.get_blob_client(container="alerts", blob=videoName)

    # Converting videoArray ( numpy array ) into video
    # fps = 30 # 25 frames per second


    # print(videoName)
    output = cv2.VideoWriter(videoName, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height), True)
    for i in videoArray:
        output.write(i)
    output.release()

    path = "./" + videoName
    # print("path : ", path)
    with open(path, "rb") as data :
        # Uploading video to the cloud
        blob_client.upload_blob(data)
    # Delete file after upload

    os.remove(path)

    return blob_client.url

# frames = []
# path = "./data/test.mp4"
#
# cap = cv2.VideoCapture(path)
#
# if cap.isOpened():
#     width = int(cap.get(3))
#     height = int(cap.get(4))
# print("width : ", width)
# print("height : ", height)
# ret = True
# while ret:
#     ret, img = cap.read()
#     if ret:
#         frames.append(img)
# video = np.stack(frames, axis = 0)
#
# # print(video)
#
# print(uploadBlob(video, "Alert", width, height))

