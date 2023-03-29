import os
import pytz
from flask import Flask, flash, request, redirect, url_for,session
from werkzeug.utils import secure_filename
from flask import send_from_directory
import os
from google.oauth2 import service_account
from google.cloud import vision
import io
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.utils import secure_filename
from functools import wraps
from PIL import Image


app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

def check_for_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers['Authorization']
        if not token:
            return json.dumps({"error": "token missing"}),401
        if token.strip(" ") == app.config['SECRET_KEY']:
            return func(*args, **kwargs)
        else:
            return json.dumps({"error": "invalid token"}),401
        return func(*args, **kwargs)
    return decorated

def localize_objects(path):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
    credentials = service_account.Credentials.from_service_account_file("keyFile.json")
    client = vision.ImageAnnotatorClient(credentials=credentials)

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    objects = client.object_localization(image=image).localized_object_annotations
    # return the estimated number of persons in the image
    person_count = 0
    for object_ in objects:
        if object_.name == 'Person':
            person_count += 1
    return person_count

class PersonCount(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    person_count = db.Column(db.Integer)
    uploaded_at = db.Column(db.String(40))
    temperature = db.Column(db.Integer)

    def __init__(self,person_count, uploaded_at,temperature):
        self.person_count = person_count
        self.uploaded_at = uploaded_at
        self.temperature = temperature


@app.route('/')
def index():
    try:
        persons = PersonCount.query.order_by(PersonCount.uploaded_at.desc()).first()
        estimated_queue_time = persons.person_count * 2

    except:
        estimated_queue_time = " "
        persons = " "
    return render_template('index.html',context=persons,estimated_queue_time=estimated_queue_time)


# @app.route('/', methods=['POST'])
# def upload_files():
#     uploaded_file = request.files['file']
#     filename = secure_filename(uploaded_file.filename)
#     if filename != '':
#         file_ext = os.path.splitext(filename)[1]
#         if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
#                 file_ext != validate_image(uploaded_file.stream):
#             abort(400)
#         uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
#         file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
#         person_count = localize_objects(file_path)
#         session['person_count'] = person_count
#
#     return redirect(url_for('index', person_count=person_count))


@app.route('/api/upload', methods=['GET', 'POST'])
# @check_for_token
def upload():
    if request.method == 'POST':
        # create variable to get temperature from api post
        uploaded_file = request.files['file']
        temperature = request.form['temperature']
        temperature = int(round(float(temperature)))
        Image.open(uploaded_file).save(os.path.join(app.config['UPLOAD_PATH'], 'converted.png'))
        person_count = localize_objects('static/images/converted.png')
        persons_in_queue = PersonCount(person_count=person_count, uploaded_at= datetime.now(pytz.timezone("Europe/Copenhagen")).strftime("%Y-%m-%d %H:%M:%S"),
                                        temperature=temperature)
        db.session.add(persons_in_queue)
        db.session.commit()
        return json.dumps({"person_count": person_count, "temperature": temperature, "last_update": datetime.now(pytz.timezone("Europe/Copenhagen")) .strftime("%Y-%m-%d %H:%M:%S")})

