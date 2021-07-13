import time

import openpifpaf
import torch
import numpy as np
import cv2
from PIL import Image
import requests
import io


# print('openpifpaf version ', openpifpaf.__version__)
# print('pytorch version ', torch.__version__)



def fall_detection_method():

    cap = cv2.VideoCapture('sea waves.mp4')
    predictor = openpifpaf.Predictor(checkpoint='shufflenetv2k30', json_data=True)
    annotation_painter = openpifpaf.show.AnnotationPainter()

    vdist = 0
    maxHeight = 0
    noseX = 0
    noseY = 0
    confidence = 0
    i = 1
    print("before while true")
    while True:

        try:
            index, frame = cap.read()

            # print("index is : ", index)
            # print("frame shape is : ", frame.shape)

            RGB_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # img_array = np.asarray(RGB_img)

            predictions, gt_anns, image_meta = predictor.numpy_image(RGB_img)

            # annotation_painter.annotations(RGB_img, predictions[0]["keypoints"])

            try:

                if predictions:
                    # there is a person in the frame
                    if predictions[0]["keypoints"][2] != 0:
                        # nose keypoint valid
                        if noseX == 0:
                            noseX = predictions[0]["keypoints"][0]
                            current_noseX = noseX
                        if noseY == 0:
                            noseY = predictions[0]["keypoints"][1]
                            current_noseY = noseY

                        current_noseY = predictions[0]["keypoints"][1]
                        height = predictions[0]["bbox"][3]
                        width = predictions[0]["bbox"][2]

                    if noseY < current_noseY * 2 :

                        if width > height:

                            cv2.putText(RGB_img,
                                    "FAll detected",
                                    (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1,
                                    (255, 0, 0),
                                    2,
                                    cv2.LINE_AA)

                        else :

                            cv2.putText(RGB_img,
                                        "No Fall",
                                        (50, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        1,
                                        (255, 0, 0),
                                        2,
                                        cv2.LINE_AA)


                # print(f"noseX : {noseX} for frame number {i}")
                # print(f"noseY : {noseY} for frame number {i}")
                # print(f"Person height : {height} for frame number {i}")
                # print(f"Person width : {width} for frame number {i}")
                i += 1

            except Exception as e:
                print("errorrr")



            cv2.imshow('frame', RGB_img)
            cv2.waitKey(0)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        except BaseException as e:
            print("There is an error reading video : ",e)





fall_detection_method()