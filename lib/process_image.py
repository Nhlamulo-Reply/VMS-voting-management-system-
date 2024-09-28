import os
from datetime import datetime
from typing import IO
import cv2
import pytesseract
import pandas as pd
from werkzeug.utils import secure_filename
from flask import current_app


def save_image(image: IO):
    folder_path = current_app.config['UPLOAD_FOLDER']

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    toaycurrent_date= datetime.now().strftime("%Y%m%d_%H%M%S")

    filename_image = image.filename
    original_filename, file_ext = os.path.splitext(filename_image)
    new_filename = f"{original_filename}_{today}{file_ext}"
    filename = secure_filename(new_filename)
    image_filename = os.path.join(folder_path, filename)
    image.save(image_filename)

    return image_filename


def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.bitwise_not(thresh)
    return thresh


def extract_tables(image_path):

    processed_image = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_string(processed_image, config=custom_config)

    lines = data.strip().split('\n')


    cleaned_lines = []
    for line in lines:

        words = [word.strip() for word in line.split() if word.strip()]
        if words:
            cleaned_lines.append(words)

    df = pd.DataFrame(cleaned_lines)

    df = df.drop_duplicates()
    today = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"extracted_data_{today}.csv"
    folder = current_app.config['UPLOAD_FOLDER']
    csv_path = os.path.join(folder, csv_filename)
    df.to_csv(csv_path, index=False, header=False)

    return csv_path


def perform_ocr(image_path):
    text = pytesseract.image_to_string(image_path)
    return text
