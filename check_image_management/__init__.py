import base64
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import os
MEDIA_PATH = "C:/"

def get_check_image(user, account_no, exchange_id):
    try:
        str_encded = base64.b64encode(open(MEDIA_PATH+"check_images/{exid}.jpeg"
                                           .format(
                                                   exid=exchange_id), "rb").read())
        return str_encded
    except:
        return None


def save_check_image(user, account_no, exchange_id, file):
    MAX_WIDTH = 1000
    if file.content_type.split("/")[0] == "image":
        img = Image.open(file)

        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH/img.width
            (width, height) = (int(img.width * ratio), int(img.height * ratio))
            img.resize((width, height))
        filepath = MEDIA_PATH+"check_images/{exid}.jpeg".format(exid=exchange_id)
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        img.save(filepath, format="JPEG")
