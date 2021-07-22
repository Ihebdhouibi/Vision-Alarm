from collections import OrderedDict

import numpy as np
import openpifpaf
import cv2
from MachineVision.FallDetection import CentroidTracker
from MachineVision.FallDetection import FallDetector

from cloudStorage import uploadBlob

# print('openpifpaf version ', openpifpaf.__version__)
# print('pytorch version ', torch.__version__)


def fall_detection_method():
    # cap = cv2.VideoCapture("fall 2.mp4")
    cap = cv2.VideoCapture(0)
    predictor = openpifpaf.Predictor(checkpoint='shufflenetv2k30', json_data=True)
    annotation_painter = openpifpaf.show.AnnotationPainter()

    tracker = CentroidTracker()

    fd = FallDetector()
    frames = []
    alert = False
    numb_noFall_frame = 300

    while True:

        index, frame = cap.read()

        if index is None:
            print("Cannot read frames ! ")

        else:
            # print("index is : ", index)
            # print("frame shape is : ", frame.shape)
            RGB_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            try:
                predictions, gt_anns, image_meta = predictor.numpy_image(RGB_img)
                person_number = len(predictions)
                print("person number : predictions : ",person_number)

            except BaseException as e:
                print("There is a problem extracting info from predictor : ",e)

            j = 0

            # print("person number : ", person_number)
            rects = []
            rects2 = []
            if predictions:

                while j < person_number:

                    keypoints = predictions[j]["keypoints"]

                    if keypoints.count(0.0) > len(keypoints) / 1.5 :
                        # not valid keypoint
                        print(f"Abandoning this prediction because number of zeros {keypoints.count(0)} while number of elements {len(keypoints)}")
                        j += 1
                        continue

                    startX = int(predictions[j]["bbox"][0])
                    startY = int(predictions[j]["bbox"][1])
                    endX = int(startX + predictions[j]["bbox"][2])
                    endY = int(startY + predictions[j]["bbox"][3])

                    noseX = keypoints[0]
                    noseY = keypoints[1]

                    width = predictions[j]["bbox"][2]
                    height = predictions[j]["bbox"][3]

                    # print(" executed times : ", j)
                    # print(f"startX : {startX} startY : {startY} endX : {endX} endY : {endY} for j = {j}")
                    j += 1
                    rects.append((startX, startY, endX, endY))
                    rects2.append((startX, startY, endX, endY, width, height))

            persons = tracker.update(rects=rects)
            persons2= OrderedDict()
            i = 0
            print("len of rects2 : ", len(rects2))

            if len(rects2) >0 :
                for ID in range(0, len(rects2)):
                    persons2[ID] = rects2[ID]
                    i+= 1


            i = len(persons)
            # print(f"persons number {i} ")
            cv2.putText(RGB_img, f"Tracked persons : {i}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0),2,cv2.LINE_AA)

            if predictions:
                for (objectID, centroid) in persons.items():
                    text = "ID {} ".format(objectID)
                    cv2.putText(RGB_img, text, (centroid[0] - 10, centroid[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.circle(RGB_img, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

            fall = fd.update(persons2)

            if fall:

                numb_noFall_frame = 0
                cv2.putText(RGB_img, "Fall detected", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

                # frame_array = np.asarray(RGB_img)
                frames.append(RGB_img)

            elif numb_noFall_frame < 300:
                cv2.putText(RGB_img, "Fall detected", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                print(f"inside elif with numb_noFall_frame = {numb_noFall_frame}")
                numb_noFall_frame += 1
                # frame_array = np.asarray(RGB_img)
                frames.append(RGB_img)
                alert = True
            else:

                cv2.putText(RGB_img, "No fall", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                img_width = 0
                img_height = 0
                img_channels = 0

                # print(type(RGB_img.shape))

                # print(f"width is : {img_width} ")
                # height("height is : ",int(img_height))

                if alert:
                    video = np.stack(frames, axis = 0)
                    ( img_height,img_width, img_channels) = RGB_img.shape
                    videoLink = uploadBlob(videoArray=video, videoName="Fall_Alert", width=img_width,height= img_height)
                    frames = []
                    alert = False

            BGR_img = cv2.cvtColor(RGB_img, cv2.COLOR_RGB2BGR)
            cv2.imshow('frame', BGR_img)
            # cv2.waitKey(0)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                cap.release()
                break




fall_detection_method()
