"""

This project is created by Nhlamulo Reply Shikweni
dated 2024-09-28

"""


import numpy as np
import cv2
import  pytesseract
from flask import Flask, render_template, request, json, Blueprint, flash
from lib import process_image
from PIL import Image
from io import BytesIO
import os


from  Exceptions import *
from lib.process_image import *

module = Blueprint('process_image', __name__)

@module.route('/upload-image', methods=['POST'])
def process():
    """
       Endpoint to process the uploaded image and save it to a specific directory.

    :param  image
    :param string Longitude
    :param string Latitude
    :param string UserName

    :return:

    """

    image = request.files.get('image')

    if not image:
        return "No image provided", 400


    image_path = save_image(image)

    csv_path = extract_tables(image_path)

    extracted_text = perform_ocr(image_path)

    return {
        "message": "Image processed successfully",
        "csv_path": csv_path,
        "extracted_text": extracted_text
    }, 200



