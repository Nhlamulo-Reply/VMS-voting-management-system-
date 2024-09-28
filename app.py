from flask import Flask
import pytesseract
from module.process_image import module as process_image_module


UPLOAD_FOLDER = 'C:/Users/User/PycharmProjects/flaskProject/images'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(process_image_module, url_prefix='/process_image')

if __name__ == '__main__':
    app.run(debug=True)
