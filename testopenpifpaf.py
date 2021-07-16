import time

import openpifpaf
import torch
import numpy as np
import cv2
from CentroidTracker import CentroidTracker

# print('openpifpaf version ', openpifpaf.__version__)
# print('pytorch version ', torch.__version__)


def fall_detection_method():
    cap = cv2.VideoCapture("fall 2.mp4")
    # cap = cv2.VideoCapture(0)
    predictor = openpifpaf.Predictor(checkpoint='shufflenetv2k30', json_data=True)
    annotation_painter = openpifpaf.show.AnnotationPainter()

    tracker = CentroidTracker()



    vdist = 0
    maxHeight = 0
    noseX = 0
    noseY = 0
    confidence = 0
    i = 1
    print("before while true")
    while True:

        index, frame = cap.read()

        if index is None:
            print("Cannot read frames ! ")

        else:
            # print("index is : ", index)
            # print("frame shape is : ", frame.shape)
            RGB_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # RGB_img = cv2.GaussianBlur(RGB_img, (3, 3), 0)
            try:
                predictions, gt_anns, image_meta = predictor.numpy_image(RGB_img)
                person_number = len(predictions)
            except BaseException as e:
                print("There is a problem extracting info from predictor : ",e)

            j = 0

            # print("person number : ", person_number)
            if predictions:
                while j < person_number:
                    rects = []
                    startX = int(predictions[j]["bbox"][0])
                    startY = int(predictions[j]["bbox"][1])
                    endX = int(startX + predictions[j]["bbox"][2])
                    endY = int(startY + predictions[j]["bbox"][3])

                    # print(f"startX : {startX} startY : {startY} endX : {endX} endY : {endY} for j = {j}")

                    rects.append((startX, startY, endX, endY))
                    j += 1

            else:
                rects = []

            persons = tracker.update(rects=rects)

            if predictions:
                for (objectID, centroid) in persons.items():
                    text = "ID {} ".format(objectID)
                    cv2.putText(RGB_img, text, (centroid[0] - 10, centroid[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.circle(RGB_img, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)



            i = len(persons)
            # print(f"persons number {i} ")
            cv2.putText(RGB_img, f"Tracked persons : {i}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),2,cv2.LINE_AA)

                    # # there is a person in the frame
                    # if predictions[0]["keypoints"][2] != 0:
                    #     # nose keypoint valid
                    #     if noseX == 0:
                    #         noseX = predictions[0]["keypoints"][0]
                    #         current_noseX = noseX
                    #     if noseY == 0:
                    #         noseY = predictions[0]["keypoints"][1]
                    #         current_noseY = noseY
                    #     if maxHeight == 0 :
                    #         maxHeight = predictions[0]["bbox"][3]
                    #     current_noseY = predictions[0]["keypoints"][1]
                    #
                    #     vdist = vdist + current_noseY - noseY
                    #
                    # height = predictions[0]["bbox"][3]
                    # width = predictions[0]["bbox"][2]
                    #
                    # print("noseY * 2 < current_noseY   =  ", noseY * 2 < current_noseY)
                    # print(f"noseY : {noseY} for frame number {i} ")
                    # print(f"current_noseY : {current_noseY} for frame number {i}")
                    # print(f"vdist {vdist}")
                    # print(f"first person height : {maxHeight}")
                    # print(f"person width : {width} for frame number {i}")
                    # print(f"person height : {height} for frame number {i}")
                    #
                    # # if predictions[0]["keypoints"][17] > 0:
                    # #     leftshouldY = predictions[0]["keypoints"][16]
                    # #     print("left shoulder Y available : ", leftshouldY)
                    # # if predictions[0]["keypoints"][35] > 0:
                    # #     leftwristY = predictions[0]["keypoints"][34]
                    # #     print("left wrist Y available : ", leftwristY)
                    #
                    # if vdist > maxHeight / 2 :
                    #
                    #     if width > height / 2:
                    #
                    #         cv2.putText(RGB_img,
                    #                     "Fall detected",
                    #                     (50, 50),
                    #                     cv2.FONT_HERSHEY_SIMPLEX,
                    #                     1,
                    #                     (255, 0, 0),
                    #                     2,
                    #                     cv2.LINE_AA)
                    #
                    # else:
                    #
                    #     cv2.putText(RGB_img,
                    #                 "No Fall",
                    #                 (50, 50),
                    #                 cv2.FONT_HERSHEY_SIMPLEX,
                    #                 1,
                    #                 (255, 0, 0),
                    #                 2,
                    #                 cv2.LINE_AA)
                    #
                    # print("******************************************* \n")
                # print(f"noseX : {noseX} for frame number {i}")
                # print(f"noseY : {noseY} for frame number {i}")
                # print(f"Person height : {height} for frame number {i}")
                # print(f"Person width : {width} for frame number {i}")

            BGR_img = cv2.cvtColor(RGB_img, cv2.COLOR_RGB2BGR)
            cv2.imshow('frame', BGR_img)
            # cv2.waitKey(0)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                cap.release()
                break




fall_detection_method()
