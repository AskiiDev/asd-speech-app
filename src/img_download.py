from duckduckgo_images_api import search
from urllib.error import HTTPError
from io import BytesIO
from os import listdir
import urllib.request
from PIL import Image

opener = urllib.request.build_opener()
vocabulary = []
downloader_ready = False


def init_downloader():
    global opener
    global vocabulary
    global downloader_ready

    # create the url opener and add headers (prevents most request rejections)
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/36.0.1941.0 '
                          'Safari/537.36')]
    urllib.request.install_opener(opener)

    # get vocabulary list
    vocab_list = open("../data/words.txt", 'r')
    vocabulary = vocab_list.read().splitlines()
    downloader_ready = True


# download a compressed image using duckduckgo-api
def download_image(keyword, result=0, context="clipart"):
    global opener
    global downloader_ready

    if not downloader_ready:
        init_downloader()

    try:
        # get the image link from the first result of the image search (index 0)
        # note -- searching for clipart specifically provides more appropriate results
        response = opener.open(search("'" + keyword + "' " + context, 1)[result]["image"])

        # convert bytes array into a readable string
        img = BytesIO(response.read())
        im = Image.open(img)

        # resize image down to 128 pixels (maintains aspect ratio)
        im.thumbnail((128, 128), Image.LANCZOS)
        im.save("img/" + keyword + ".jpg", "png")
    except HTTPError:
        # if the user-agent is rejected, call the function again and look for the next result
        download_image(keyword, result + 1)


# if there are any files missing for whatever reason, attempt to re-download them
def verify_downloads(extension=".jpg"):
    global vocabulary

    for check in vocabulary:

        # check if the file exists in the img directory
        if not(check.strip() + extension in listdir("img")):
            download_image(check.strip())


def get_image(word, retries=0, max_retries=2):
    if retries >= max_retries:
        return "img/default_placeholder.png"

    # check if the file for this word exists
    elif word + ".jpg" in listdir("img"):
        return str("img/"+word+".jpg")
    else:
        download_image(word)
        return get_image(word, retries + 1)
