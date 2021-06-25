import os, uuid, time, datetime

import cv2
import numpy as np
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__


def initBlogClient():
    """
    TODO: remove cloud connection string

    """
    connect_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    print("Connection string : ", connect_string)
    blob_service_client = BlobServiceClient.from_connection_string(connect_string)

    return blob_service_client

def createAzureContainer():

    blob_service_client = initBlogClient()

    container_name = "alerts"

    container_client = blob_service_client.create_container(container_name)


def uploadBlob(videoArray, videoName, width, height):

    blob_service_client = initBlogClient()
    videoName = videoName + " " + str(datetime.date.today()) + ".mp4"
    blob_client = blob_service_client.get_blob_client(container="alerts", blob=videoName)

    # Converting videoArray ( numpy array ) into video
    fps = 25 # 25 frames per second


    print(videoName)
    output = cv2.VideoWriter(videoName, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height), True)
    for i in videoArray:
        output.write(i)
    output.release()

    path = "./" + videoName
    print("path : ", path)
    with open(path, "rb") as data :
        # Uploading video to the cloud
        blob_client.upload_blob(data)
    # Delete file after upload

    os.remove(path)

    return blob_client.url

frames = []
path = "./data/test.mp4"

cap = cv2.VideoCapture(path)

if cap.isOpened():
    width = int(cap.get(3))
    height = int(cap.get(4))
print("width : ", width)
print("height : ", height)
ret = True
while ret:
    ret, img = cap.read()
    if ret:
        frames.append(img)
video = np.stack(frames, axis = 0)

# print(video)

print(uploadBlob(video, "Alert", width, height))

