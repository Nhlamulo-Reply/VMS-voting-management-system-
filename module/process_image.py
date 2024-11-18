"""

This project is created by Nhlamulo Reply Shikweni
dated 2024-09-28

"""

import numpy as np
import cv2
import pytesseract
from flask import Flask, render_template, request, json, Blueprint, flash, jsonify
from lib import process_image
from PIL import Image
from io import BytesIO
import os

from Exceptions import *
from lib.process_image import *

module = Blueprint('process_image', __name__)


@module.route('/upload-image', methods=['POST'])
def process():

    """
    Handle image uploads and save metadata to the database.
    This function processes a POST request to upload an image along with related metadata
    such as staff ID, location (longitude and latitude), and address.
    It saves the image to the server and stores the metadata in a database. Returns: - 400 Bad Request:
     If the required image file is missing. - 500 Internal Server Error:
     If there is a failure in saving the image or metadata. - 200 OK:
      If the image and metadata are successfully processed.

    Returns
    -------

    """

    image = request.files.get('image')
    staff_id = '1'
    longitude = '27.932948466758585'
    latitude = ' -26.016783995755237'
    fullAddress = '23 Kansas Cres, Cosmo City, Roodepoort, 2188, South Africa'

    if not image:
        return jsonify({"message": "Missing required params"}), 400

    # Save the image and get the path
    db = current_app.config['db']
    image_path = save_image(staff_id, image, db, longitude, latitude, fullAddress)

    if image_path is None:
        return jsonify({"message": "Failed to save the image"}), 500

    # Process the image for table extraction and OCR
    # csv_path = extract_table_structure(image_path)
    # extracted_text = perform_ocr_and_highlight(image_path)

    return jsonify({
        "message": "Image processed successfully",
        # "csv_path": csv_path,
        # # "extracted_text": extracted_text
    }), 200



@module.route('/display-vote-data', methods=['POST'])
def process():
    """
        An endpoint  used to fetch votes data from csv then create an chart out of it
    Returns
    -------

    """

    folder_path = current_app.config['UPLOAD_FOLDER']

    try:
        res= read_csv_data(folder_path)
        return jsonify(res)
    except Exception as e:
        return jsonify({"message": str(e)}), 500



