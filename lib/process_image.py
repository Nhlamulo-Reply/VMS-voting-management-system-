import os
from datetime import datetime
from typing import IO
import cv2
import pytesseract
import pandas as pd
from werkzeug.utils import secure_filename
from flask import current_app, app
from db import Database
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def save_image(staff_id, image, db: Database, longitude, latitude, fullAddress):
    folder_path = current_app.config['UPLOAD_FOLDER']

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    today = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_image = image.filename
    original_filename, file_ext = os.path.splitext(filename_image)
    new_filename = f"{original_filename}_{today}{file_ext}"
    filename = secure_filename(new_filename)
    image_filename = os.path.join(folder_path, filename)

    try:
        image.save(image_filename)
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

    sql = ("INSERT INTO photographer (staff_id, image, date_added, longitude, latitude, fullAdress) "
           "VALUES (%(staff_id)s, %(image)s, NOW(), %(longitude)s, %(latitude)s, %(fullAddress)s)")
    params = {
        'staff_id': staff_id,
        'image': filename,
        'longitude': longitude,
        'latitude': latitude,
        'fullAddress': fullAddress
    }

    if db and db.connection:
        try:
            db.execute(sql, params)
            return image_filename
        except Exception as e:
            print(f"Failed to execute query: {e}")
            return None
    else:
        print("Database connection is not established.")
        return None


# def preprocess_image(image_path):
#     # Check if the file exists before attempting to read
#     if not os.path.exists(image_path):
#         print(f"Error: File '{image_path}' does not exist.")
#         return None
#
#     # Read the image file
#     img = cv2.imread(image_path)
#
#     # Verify that the image was loaded successfully
#     if img is None:
#         print(f"Error: Failed to load image from '{image_path}'.")
#         return None
#
#     # Proceed with image processing if loading was successful
#     try:
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         thresh = cv2.adaptiveThreshold(
#             gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
#         )
#         thresh = cv2.bitwise_not(thresh)
#         return thresh
#     except cv2.error as e:
#         print(f"OpenCV error during image processing: {e}")
#         return None
#
# def perform_ocr(image_path):
#     text = pytesseract.image_to_string(image_path)
#     return text
# def extract_tables(image_path):
#
#     processed_image = preprocess_image(image_path)
#     custom_config = r'--oem 3 --psm 6'
#     data = pytesseract.image_to_string(processed_image, config=custom_config)
#
#     lines = data.strip().split('\n')
#     cleaned_lines = []
#
#     for line in lines:
#         words = [word.strip() for word in line.split() if word.strip()]
#         if words:
#             cleaned_lines.append(words)
#
#     # Create a DataFrame from the cleaned data
#     df = pd.DataFrame(cleaned_lines)
#
#     # Drop duplicate rows
#     df = df.drop_duplicates()
#
#     # Generate a timestamped filename
#     today = datetime.now().strftime('%Y%m%d_%H%M%S')
#     csv_filename = f"extracted_data_{today}.csv"
#     csv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], csv_filename)
#
#     # Save the DataFrame to CSV, ensuring no header or index is included
#     df.to_csv(csv_path, index=False, header=False)
#
#     return csv_path
#


def preprocess_image(image_path):
    """
    Preprocess the image for table detection. This function checks if the file exists, loads the image,
    converts it to grayscale, and applies adaptive thresholding for further processing. Parameters: image_path (str):
    The path to the image to be processed. Returns: tuple:
    The original image and the thresholded image.

    Parameters
    ----------
    image_path

    Returns
    -------

    """

    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' does not exist.")
        return None

    # Load and process the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Failed to load image from '{image_path}'.")
        return None

    # Convert to grayscale and apply adaptive thresholding
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    return img, thresh

def detect_cells(image_path):

    """
        Detect table cells in the processed image. This function identifies and groups contours that represent cells in the image.
        Contours are filtered by size and grouped into rows.
        Parameters: image_path (str): The path to the image file.
        Returns: tuple:
        The original image and a list of rows containing cell coordinates.
        Parameters
        ----------
        image_path

        Returns
        -------

    """


    img, processed_image = preprocess_image(image_path)
    if processed_image is None:
        return None, None

    # Find contours in the thresholded image
    contours, hierarchy = cv2.findContours(processed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out contours that likely represent cells by size
    cell_contours = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Apply size filter to get cells, assuming cells are larger than some area
        if 50 < w < 500 and 20 < h < 200:  # Adjust these numbers as needed
            cell_contours.append((x, y, w, h))

    # Sort cells by position (top to bottom, then left to right)
    cell_contours = sorted(cell_contours, key=lambda b: (b[1], b[0]))

    # Group detected contours into rows
    rows = []
    current_row = []
    previous_y = -1
    for i, (x, y, w, h) in enumerate(cell_contours):
        if previous_y == -1 or abs(y - previous_y) < 10:
            current_row.append((x, y, w, h))
            previous_y = y
        else:
            rows.append(sorted(current_row, key=lambda b: b[0]))  # Sort cells in the row by x position
            current_row = [(x, y, w, h)]
            previous_y = y
    if current_row:
        rows.append(sorted(current_row, key=lambda b: b[0]))

    return img, rows

def extract_text_from_cells(img, rows):
    """

      Extract text from detected cells using OCR.
      Parameters: img (ndarray): The original image. rows (list):
      List of rows containing cell coordinates. Returns: list:
      A list of rows containing extracted text from each cell.

        Parameters
        ----------
        img
        rows

        Returns
        -------

    """

    table_data = []
    for row in rows:
        row_data = []
        for (x, y, w, h) in row:
            # Crop each cell and perform OCR
            cell = img[y:y+h, x:x+w]
            text = pytesseract.image_to_string(cell, config='--psm 7').strip()
            row_data.append(text)
        table_data.append(row_data)
    return table_data

def save_to_csv(table_data):

    """
Save the extracted table data to a CSV file.
 Parameters: table_data (list): The extracted table data.
  Returns: str: The path to the saved CSV file.

    Parameters
    ----------
    table_data

    Returns
    -------
    """
    # Convert to DataFrame
    df = pd.DataFrame(table_data)
    print(df)
    # Generate timestamped filename
    today = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"extracted_data_{today}.csv"
    csv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], csv_filename)

    # Save DataFrame to a tab-separated CSV file
    df.to_csv(csv_path, sep='\t', index=False, header=False)
    return csv_path

def extract_table_structure(image_path):
    """

Extract table structure from an image and save it as a CSV.
Parameters: image_path (str): Path to the image containing the table.
 Returns: str: Path to the saved CSV file.


    Parameters
    ----------
    image_path

    Returns
    -------

    """
    img, rows = detect_cells(image_path)
    if rows is None:
        return None

    table_data = extract_text_from_cells(img, rows)
    csv_path = save_to_csv(table_data)

    return csv_path


def read_csv_data(filepath):
    """
    Read a tab seperated csv file into a dataframe

    Parameters
    ----------
    filepath

    Returns
    -------

    """

    try:
        df = pd.read_csv(filepath,sep = 't', header=None,names=)

        if 'Party' not in df.columns or 'Votes' not in  df.columns:
            raise ValueError("Party and Votes columns are missing. this must contain atleast two columns.")

        res = {
            "part_name":df['Party'].tolist(),
            "total votes":df['Votes'].tolist()
        }



def load_cleaned_csv(csv_path):
    """


Load cleaned CSV data for training.
Parameters: csv_path (str): Path to the CSV file.
 Returns: tuple: Features (X) and labels (y) extracted from the CSV.
    Parameters
    ----------
    csv_path

    Returns
    -------

    """
    # Load the cleaned CSV data
    df = pd.read_csv(csv_path, header=None)

    # Assume the last column is the label (target), and others are features
    X = df.iloc[:, :-1]  # Features (all columns except the last one)
    y = df.iloc[:, -1]  # Labels (the last column)

    return X, y

def train_model(csv_path):
    # Load data from cleaned CSV
    X, y = load_cleaned_csv(csv_path)

    # Split data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier()

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    print(f"Model accuracy: {accuracy * 100:.2f}%")


def plot_graph(path)