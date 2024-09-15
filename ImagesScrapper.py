import hashlib
import time
import io
import os
import requests
from bs4 import BeautifulSoup
import shutil
from tqdm import tqdm
from selenium import webdriver
from PIL import Image
import signal
import platform
import threading

class TimeoutException(Exception):
    pass

class timeout:

    def __init__(self, seconds= 1, error_message="Timeout"):
        self.seconds = seconds
        self.error_message = error_message
        self.os_is_windows = platform.system().lower() == 'windows'
    
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        if self.os_is_windows:
            # For better portability a timeout class for windows is needed
            self.timer = threading.Timer(self.seconds, self._raise_timeout)
            self.timer.start()
        else:
            # Use signal for Unix-based systems
            signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        if self.os_is_windows:
            # Cancel timer for windows
            self.timer.cancel()
        else:
            # Disable Unix alarm
            signal.alarm(0)

    def _raise_timeout(self):
        raise TimeoutException(self.error_message)

class ScraperConfig:

    def __init__(self, driver_path, output_path, number_of_images, get_image_timeout, sleep_between_interactions, sleep_before_more
                     , image_quality, search_terms):
                     self.driver_path                = driver_path
                     self.output_path                = output_path
                     self.number_of_images           = number_of_images
                     self.get_image_timeout          = get_image_timeout
                     self.sleep_between_interactions = sleep_between_interactions
                     self.sleep_before_more          = sleep_before_more
                     self.image_quality              = image_quality
                     self.search_terms               = search_terms

config = ScraperConfig(    
    driver_path = '/home/iheb/chromedriver',
    output_path = 'data/images/robbery_images',
    number_of_images = 1000,
    GET_IMAGE_TIMEOUT = 2,
    SLEEP_BETWEEN_INTERACTIONS = 0.1,
    SLEEP_BEFORE_MORE = 5,
    IMAGE_QUALITY = 1024,
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
    )

def fetch_image_urls(query: str,
                     max_links_to_fetch: int,
                     wd: webdriver,
                     config: ScraperConfig):

    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(config.sleep_between_interactions)

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
                time.sleep(config.sleep_between_interactions)
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

def persist_image(folder_path:str,url:str, config: ScraperConfig):
    try:
        print("getting the image...")
        # download the image, if timeout is exceeded throw an error
        with timeout(config.get_image_timeout):
            image_content = requests.get(url).content
    except Exception as e:
        print(f"Error - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')

        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=config.image_quality)
        print(f"Success - Saved {url} - as {file_path} ")

    except Exception as e:
        print(f"Error - could not save {url} - {e}")

def search_download(search_term:str, config: ScraperConfig, target_path="data/images/robbery_images", number_images=5):
    # create a folder name
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(" ")))

    # create folder if not exist
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # launch chrome
    with webdriver.Chrome(executable_path=config.driver_path) as wd:
        res = fetch_image_urls(search_term, number_images, wd= wd, sleep_between_interactions=config.sleep_between_interactions)

    # download images
    if res is not None:
        for elem in res:
            persist_image(target_folder, elem)
    else:
        print(f"failed to return links for terms :   {search_term}")


for term in config.search_terms:
    search_download(term,
                    config
                    )