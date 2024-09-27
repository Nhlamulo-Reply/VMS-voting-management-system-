"""

This project is created by Nhlamulo Reply Shikweni
dated 2024-09-28

"""


import numpy as np
import cv2
import  pytesseract
from flask import Flask ,render_template,   request, json,Blueprint
from lib import process_image
from PIL import Image
from io import BytesIO
import os
from  Exceptions import *
from lib.process_image import process_image_data

module = Blueprint('process_image', __name__)


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@module.route('/extact-data', methods=['POST'])
def process(image):
    """
     The following will endpoint is used to  extract tables and text from the image

    :param  image
    :param string Longitude
    :param string Latitude
    :param string UserName

    :return:

    """
    image = request.files['image']
    lat = request.args.get("Longitude")
    long = request.args.get("Longitude")

    if not image:
        raise AuthenticationError("No image provided")

    return process_image_data(image,lat,long)



