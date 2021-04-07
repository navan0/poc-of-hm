"""By Navaneeth KT."""
import json
import os
import sys
from io import BytesIO
import base64

import cv2
import torch
from PIL import Image
from vision.blacklist import BlaclistCamera
from vision.camera import VideoCamera
from vision.classification.detect_from_video import test_full_image_network
from vision.compression_detection import compression_detection
from vision.crowd import CrowdCamera
from ops.exceptions import InvalidUsage
from flask import Flask, Response, jsonify, render_template, request
from plugins import facerec
from vision.social import SocialCamera
from vision.speed import SpeedCamera

from werkzeug.utils import secure_filename

sys.path.append('./classification')

app = Flask(__name__)
CLASSIFICATION_DATA_DIR = 'classification/data_dir'
if not os.path.isdir(CLASSIFICATION_DATA_DIR):
    os.mkdir(CLASSIFICATION_DATA_DIR)
UPLOAD_FOLDER = os.path.join(CLASSIFICATION_DATA_DIR, 'uploads')

ALLOWED_EXTENSIONS = set(['mp4', 'avi'])
MODEL_PATH = 'classification/weights/full/xception/full_c23.p'
OUTPUT_PATH = os.path.join(CLASSIFICATION_DATA_DIR, 'results')
if not os.path.isdir(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cuda = False

base_weights_path = 'classification/weights/face_detection/xception'
model_full_path = f'{base_weights_path}/all_raw.p'
model_77_path = f'{base_weights_path}/all_c23.p'
model_60_path = f'{base_weights_path}/all_c40.p'

print(model_full_path)

model_full = torch.load(
    model_full_path, map_location=lambda storage, loc: storage)
model_77 = torch.load(model_77_path, map_location=lambda storage, loc: storage)
model_60 = torch.load(model_60_path, map_location=lambda storage, loc: storage)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def hello():
    """Reder index."""
    return render_template('index.html')


@app.route('/deepfake_upload')
def index():
    return render_template('Upload2.html')


@app.route('/deepfake', methods=['POST'])
def deepfake():
    if request.method == 'POST':
        fake_prediction = None
        image_frame = None
        if 'data_file' in request.files:
            file = request.files['data_file']
            if file.filename == '':
                return json.dumps({"response": "error"})
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
            if not os.path.isdir(app.config['UPLOAD_FOLDER']):
                os.mkdir(app.config['UPLOAD_FOLDER'])
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            return json.dumps({"response": "error"})

        predicted_class = compression_detection.classify_video(filepath)

        if predicted_class == '0.6':
            fake_prediction, image_frame = test_full_image_network(
                filepath, model=model_60, output_path=OUTPUT_PATH,
                start_frame=0, end_frame=None, cuda=cuda)
        elif predicted_class == '0.77':
            fake_prediction, image_frame = test_full_image_network(
                filepath, model=model_77, output_path=OUTPUT_PATH,
                start_frame=0, end_frame=None, cuda=cuda)
        elif predicted_class == 'original':
            fake_prediction, image_frame = test_full_image_network(
                filepath, model=model_full, output_path=OUTPUT_PATH,
                start_frame=0, end_frame=None, cuda=cuda)
        os.remove(filepath)
        if image_frame is not None:
            image_frame = cv2.cvtColor(image_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(image_frame)
            buff = BytesIO()
            pil_img.save(buff, format="JPEG")
            image_frame = base64.b64encode(
                buff.getvalue()).decode("utf-8")
        if fake_prediction == 1:
            return json.dumps({"response": "fake", "image": image_frame})
        elif fake_prediction == 0:
            return json.dumps({"response": "real", "image": image_frame})
        return json.dumps({"response": "error"})


@app.route("/upload",  methods=['GET', 'POST'])
def upload():
    """Upload unknown image."""
    if request.method == 'POST' and 'photo' in request.files:
        file = request.files['photo']
        file.save("plugins/geeks.jpg")
    hack = facerec.FaceRec("plugins/geeks.jpg")
    encoded = hack.classify_face()
    return json.dumps({"response": encoded[0]})


@app.route("/add",  methods=['GET', 'POST'])
def add():
    """Add new faces to database."""
    if request.method == 'POST':
        file = request.files.get('image')
        text = request.form.get('id')
        if not file or not text:
            raise InvalidUsage('Invalid data', status_code=400)
        file.save("plugins/faces/"+str(text)+".jpg")
    return json.dumps({"response": "done"})


def gen(camera):
    while True:
        frame, cache = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/face_mask')
def face_mask():
    """face_mask service."""
    return render_template('face.html')


@app.route('/video_feed')
def video_feed():
    video = request.args.get('video', 'test.mp4')
    return Response(gen(VideoCamera(video)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/blacklist')
def blacklist():
    """blacklist service."""
    return render_template('blacklist.html')


@app.route('/blacklist_criminal', methods=['POST'])
def blacklist_criminal():
    blacklist_id = request.form.get('id')
    name = request.form.get('name')
    blacklisted = request.form.get('blacklisted', 'False')
    print(blacklisted)
    image_path = os.path.join(
        os.path.dirname(__file__), "blacklist", str(blacklist_id)+"-"+name+".jpg")
    destination_path = os.path.join(
        os.path.dirname(__file__), "plugins/faces/"+str(blacklist_id)+".jpg")
    if blacklisted == 'True':
        print('fgdg')
        try:
            os.symlink(destination_path, image_path)
        except Exception:
            return json.dumps({"response": "error"})
    else:
        print('fsd')
        try:
            os.remove(image_path)
        except Exception:
            pass
    return json.dumps({"response": "done"})


@app.route('/black_video_feed')
def black_video_feed():
    video = request.args.get('video', 'blacklist.mp4')
    return Response(gen(BlaclistCamera(video)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/speed')
def speed():
    """speed service."""
    return render_template('speed.html')


@app.route('/spvideo_feed')
def spvideo_feed():
    video = request.args.get('video', 'car.mp4')
    return Response(gen(SpeedCamera(video)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/social')
def social():
    """face_mask service."""
    return render_template('social.html')


@app.route('/svideo_feed')
def svideo_feed():
    video = request.args.get('video', 'social_test.mp4')
    return Response(gen(SocialCamera(video)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/crowd')
def crowd():
    """crowd count service."""
    return render_template('crowd.html')


@app.route('/cvideo_feed')
def cvideo_feed():
    video = request.args.get('video', 'social_test.mp4')
    return Response(gen(CrowdCamera(video)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":

    app.run(debug=True)
