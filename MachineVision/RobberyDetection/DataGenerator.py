from os import listdir, remove
from os.path import join, isfile
from PIL import Image


# Our dataset is composed of both png and jpg files so we need to convert all images to jpg
def convert_png_jpg(mypath: str):
    images = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    # print("all images ",images)
    for img in images:
        img_extension = img.split('.', 1)
        # print(img_extension[1])
        if img_extension[1] == 'png':
            image = Image.open(mypath + '/' + str(img))
            image_RGBA_RGB = image.convert('RGB')
            remove(mypath + '/' + str(img))
            image_RGBA_RGB.save(rf'{mypath}/{img_extension[0]} .jpg')


# after converting our images to one format 'jpg' let's generate a dataset 
def generate_dataset():
    pass



