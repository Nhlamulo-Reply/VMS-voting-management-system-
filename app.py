#! C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe
from flask import Flask
import pytesseract

from db import Database
from module.process_image import module as process_image_module


UPLOAD_FOLDER = 'D:\htdocs\VMS-BACKEND\static\images'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#database connection here
db = Database(
    host ='localhost',
    user = 'root',
    password = '',
    database = 'votesdb'
)

#setting up Global viriables
app.config['db'] = db

db.connect()

app.register_blueprint(process_image_module, url_prefix='/process_image')

@app.teardown_request
def close_db(error):
    if db.connection:
        db.close_connection()

if __name__ == '__main__':
    app.run(debug=True, port = 5000)
