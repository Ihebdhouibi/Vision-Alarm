import cv2
import numpy as np

class PersonDetector:

    def __init__(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def cycle(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        boxes, weights = self.hog.detectMultiScale(gray, winStride=(8, 8))

        boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

        if len(boxes) > 0:
            # print("person found")
            cv2.putText(img=frame, text="Person Detected", org=(20, 30),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=(255, 0, 0), thickness=1, lineType=cv2.LINE_AA)
        else:
            # print("person not found ")
            cv2.putText(img=frame, text="No Person", org=(20, 30),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=(255, 0, 0), thickness=1, lineType=cv2.LINE_AA)
        for (xA, yA, xB, yB) in boxes:
            cv2.rectangle(frame, (xA, yA), (xB, yB),
                          (0, 255, 0), 2)
        return frame


# cap = cv2.VideoCapture(0)
# pd = PersonDetector()
#
# while True:
#
#     ret, frame = cap.read()
#
#     frame = pd.cycle(frame)
#
#     cv2.imshow('frame', frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()

