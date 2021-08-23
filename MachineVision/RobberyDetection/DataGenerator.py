from os import listdir, remove, path
from os.path import join, isfile
from PIL import Image
import splitfolders
from keras.preprocessing.image import ImageDataGenerator

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
def split_dataset(mypath:str):
    splitfolders.ratio(mypath, output='/home/iheb/PycharmProjects/Vision-Alarm/data/Finaldataset/', seed=1337, ratio=(.8, .1, .1))

# now that our dataset is split into train/test/validation folders each contains two folders robbery/no_robbery
# let's generate the dataset

def generate_dataset():
    # pass
    train_robbery_dir = path.join('/home/iheb/PycharmProjects/Vision-Alarm/data/Finaldataset/train/Robbery')
    train_noRobbery_dir = path.join('/home/iheb/PycharmProjects/Vision-Alarm/data/Finaldataset/train/No_robbery')
    valid_robbery_dir = path.join('/home/iheb/PycharmProjects/Vision-Alarm/data/Finaldataset/val/Robbery')
    valid_noRobbery_dir = path.join('/home/iheb/PycharmProjects/Vision-Alarm/data/Finaldataset/val/No_robbery')
    test_robbery_dir = path.join('/home/iheb/PycharmProjects/Vision-Alarm/data/Finaldataset/test/Robbery')
    test_noRobbery_dir = path.join('/home/iheb/PycharmProjects/Vision-Alarm/data/Finaldataset/test/No_robbery')

    train_datagen = ImageDataGenerator(rescale=1 / 255)
    valid_datagen = ImageDataGenerator(rescale=1 / 255)

    train_generator = train_datagen.flow_from_directory(
        '/home/iheb/PycharmProjects/Vision-Alarm/data/Finaldataset/train/',
        classes=['No_robbery', 'Robbery'],
        target_size=(256, 256),
        batch_size=64,
        class_mode='binary'
    )

    valid_generator = valid_datagen.flow_from_directory(
        '/home/iheb/PycharmProjects/Vision-Alarm/data/Finaldataset/val/',
        classes=['No_robbery', 'Robbery'],
        target_size=(256, 256),
        batch_size=64,
        class_mode='binary',
        shuffle=False
    )

generate_dataset()


