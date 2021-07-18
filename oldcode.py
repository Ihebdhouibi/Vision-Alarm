# there is a person in the frame
if predictions[0]["keypoints"][2] != 0:
    # nose keypoint valid
    if noseX == 0:
        noseX = predictions[0]["keypoints"][0]
        current_noseX = noseX
    if noseY == 0:
        noseY = predictions[0]["keypoints"][1]
        current_noseY = noseY
    if maxHeight == 0 :
        maxHeight = predictions[0]["bbox"][3]
    current_noseY = predictions[0]["keypoints"][1]

    vdist = vdist + current_noseY - noseY

height = predictions[0]["bbox"][3]
width = predictions[0]["bbox"][2]

print("noseY * 2 < current_noseY   =  ", noseY * 2 < current_noseY)
print(f"noseY : {noseY} for frame number {i} ")
print(f"current_noseY : {current_noseY} for frame number {i}")
print(f"vdist {vdist}")
print(f"first person height : {maxHeight}")
print(f"person width : {width} for frame number {i}")
print(f"person height : {height} for frame number {i}")

# if predictions[0]["keypoints"][17] > 0:
#     leftshouldY = predictions[0]["keypoints"][16]
#     print("left shoulder Y available : ", leftshouldY)
# if predictions[0]["keypoints"][35] > 0:
#     leftwristY = predictions[0]["keypoints"][34]
#     print("left wrist Y available : ", leftwristY)

if vdist > maxHeight / 2 :

    if width > height / 2:

        cv2.putText(RGB_img,
                    "Fall detected",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 0, 0),
                    2,
                    cv2.LINE_AA)

else:

    cv2.putText(RGB_img,
                "No Fall",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2,
                cv2.LINE_AA)

print("******************************************* \n")
print(f"noseX : {noseX} for frame number {i}")
print(f"noseY : {noseY} for frame number {i}")
print(f"Person height : {height} for frame number {i}")
print(f"Person width : {width} for frame number {i}")