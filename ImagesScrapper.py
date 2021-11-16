import hashlib
import io
import time
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import shutil
from tqdm import tqdm
from selenium import webdriver
from PIL import Image
import signal

driver_path = '/home/iheb/chromedriver'
output_path = 'data/images/robbery_images'
number_of_images = 1000
GET_IMAGE_TIMEOUT = 2
SLEEP_BETWEEN_INTERACTIONS = 0.1
SLEEP_BEFORE_MORE = 5
IMAGE_QUALITY = 1024
search_terms = ["armed robbery",
                "shop robbery",
                "man wearing robber mask",
                "man wearing robber mask and knife",
                "shop armed looting",

                "persons",
                "store customers",
                "faces",
                "covid mask",
                "person portrait",
                "full body person portrait",
                "person smiling"]
# search_terms = ["armed masked thief"]
class timeout:

    def __init__(self, seconds= 1, error_message="Timeout"):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


def fetch_image_urls(query: str,
                     max_links_to_fetch: int,
                     wd: webdriver,
                     sleep_between_interactions: int = 1):

    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    # building google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    # image_urls declared as set to prevent storing duplicates
    image_urls = set()
    image_count = 0
    results_start = 0

    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        print(f"Found : {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception as e:
                print(f"could not click image - {e}")
                continue

            # extract image url
            actual_images = wd.find_elements_by_css_selector("img.n3VNCb")
            for actual_image in actual_images:
                if actual_image.get_attribute("src") \
                        and "http" in actual_image.get_attribute("src"):
                    image_urls.add(actual_image.get_attribute("src"))

            image_count = len(image_urls)
            print(f"image count {image_count}")
            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} images links ! ")
                break

        else:
            print(f"Found: {len(image_urls)} looking for more...")
            time.sleep(30)

            not_what_you_want_button = ""

            try:
                not_what_you_want_button = wd.find_element_by_css_selector(".r0zKGf")
            except:
                pass


            # load_more_button = wd.find_elements_by_css_selector(".mye4qd")
            if not_what_you_want_button:
                print("No more images available ! ")
                return image_urls

            # if there is a load more button click it
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button and not not_what_you_want_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        results_start= len(thumbnail_results)

    return image_urls

def persist_image(folder_path:str, url:str):
    try:
        print("getting the image...")
        # download the image, if timeout is exceeded throw an error
        with timeout(GET_IMAGE_TIMEOUT):
            image_content = requests.get(url).content
    except Exception as e:
        print(f"Error - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')

        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=IMAGE_QUALITY)
        print(f"Success - Saved {url} - as {file_path} ")

    except Exception as e:
        print(f"Error - could not save {url} - {e}")

def search_download(search_term:str, target_path="data/images/robbery_images", number_images=5):

    # create a folder name
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(" ")))

    # create folder if not exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # launch chrome
    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, number_images, wd= wd, sleep_between_interactions=SLEEP_BETWEEN_INTERACTIONS)

    # download images
    if res is not None:
        for elem in res:
            persist_image(target_folder, elem)
    else:
        print(f"failed to return links for terms :   {search_term}")


for term in search_terms:
    search_download(term,
                    output_path,
                    number_of_images)

# search_term = "dog"
# search_download(search_term=search_term,
#                 driver_path=driver_path,
#                 target_path="data/images/robbery_images")
# def ImageScrapper(url):
#
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     base_link = ''
#     index = 0
#     # for item in soup.find_all('img'):
#     #     img_link = item.attrs['src']
#     #     index += 1
#     #     print(f"image number : {index} link : {img_link}")
#     #
#     #     full_url = url + img_link
#     #
#     #     r = requests.get(full_url,
#     #                      stream=True)
#     #     print(f"code : {r.status_code}")
#     #     print(r.raw)
#     #     if r.status_code == 200:
#     #         print(f"everything is okkay for image number {index}")
#     #         with open("data/images/robbery_images/img" +str(index)+ ".jpg", 'wb') as f:
#     #             r.raw.decode_content = True
#     #             shutil.copyfileobj(r.raw, f)
#
#     images = soup.find_all('img')
#     print(images[0])
#     img_src = images[0].attrs['src']
#     full_link = url + img_src
#     print(full_link)
#
#     split_string = img_src.split(".",1)
#     print(split_string[1])
#
#     r = requests.get(full_link, stream=True)
#     if r.status_code == 200:
#         with open("data/images/robbery_images/img"+str(index)+"."+str(split_string[1]) , "wb") as f:
#             r.raw.decode_content = True
#             shutil.copyfileobj(r.raw, f)
# ImageScrapper("https://www.google.com/search?q=armed+robbery+jpg&tbm=isch&client=opera&hs=Gao&hl=en&sa=X&ved=2ahUKEwjMmPa8s6byAhVaO-wKHXmYAQYQBXoECAEQIw&biw=1865&bih=952")


# def getData(url):
#     r = requests.get(url)
#     return r.text
#
# htmldata = getData("https://www.istockphoto.com/photos/armed-robbery")
# soup = BeautifulSoup(htmldata, 'html.parser')
# for item in soup.find_all('img'):
#     print(item['src'])
