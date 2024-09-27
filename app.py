from flask import Flask
from module.process_image import module as process_image_module

app = Flask(__name__)

app.register_blueprint(process_image_module, url_prefix='/process_image')

if __name__ == '__main__':
    app.run(debug=True)
