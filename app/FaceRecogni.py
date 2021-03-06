from app import app
import os
import sys
import timeit
from flask import Flask, request, jsonify, render_template
import numpy as np
from werkzeug.utils import secure_filename

import pymongo
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
import face_recognition

from functools import wraps
from flask_bcrypt import Bcrypt
import secrets
###########################################################
# CONFIGS
app.config.from_pyfile('config.py')
cluster = pymongo.MongoClient(app.config["URI"])
db = cluster["facedb"]
collection = db["faces"]
app_collection = db['app']
###########################################################
bcrypt = Bcrypt(app)
###########################################################


def token_required(f):
    @wraps(f)
    def decorator():
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return(jsonify(message='Token Missing'))

        t = app_collection.find_one({'token': token})

        if t is not None:
            current_user = t['id']
        else:
            return(jsonify(message='Invalid Token'))

        return f(current_user)
    return decorator
###########################################################


@app.route('/test')
@token_required
def test_func(app_name):
    return(jsonify(message="test successfull", user=app_name))


@app.route('/gettoken')
def gettoken():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return(jsonify(message='could not verify user', code='401'))
    else:
        user = app_collection.find_one({'id': auth.username}, {'_id': 0})
        if bcrypt.check_password_hash(user['pwd'], auth.password):
            if 'token' not in user:
                token = secrets.token_urlsafe(20)
                app_collection.update_one({'id': auth.username}, {
                                          "$set": {"token": token}})
                return(jsonify({'token': token}))
            else:
                return(jsonify({'token': user['token']}))
        else:
            return(jsonify(message='wrong password'))
    return(jsonify(message='unexpected error occured'))


@app.route('/getall', methods=['GET'])
def home():
    if request.method == 'GET':
        dict = {}
        dat = collection.find({}, {'name': 1})
        for i in dat:
            if os.path.exists('app/static/known/{}.jpg'.format(i['name'])):
                dict.update({i['name']: ('known/{}.jpg'.format(i['name']))})
            else:
                pass
        print(dict)
        return render_template('index.html', data=dict)
    else:
        return(jsonify(message='INVALID HTTP METHOD'))


@app.route('/createapp', methods=['POST', 'GET'])
def createapp():
    if request.method == 'POST':
        if 'id' in request.form and 'pwd' in request.form:
            password = bcrypt.generate_password_hash(request.form['pwd'])
            app_collection.insert({'id': request.form['id'], 'pwd': password})
            return(jsonify(message='app created'))
        else:
            return(jsonify(message='missing parameters'))
    else:
        return(jsonify(message='Invalid Method'))


"""
method: POST
headers: {  x-access-tokens:<token>,
            conten-type:multipart-form-data }
body:{  image:<img.jpg>,
        name:<name>,
        app:<app name>}
"""
@app.route('/learn', methods=['POST', 'GET'])
@token_required
@cross_origin(origin='*')
def learn(app_name):
    if request.method == 'POST':
        if 'image' in request.files and 'name' in request.form:
            # start = timeit.timeit()             # start time --1
            file = request.files['image']
            name = request.form['name']
            file.filename = '{}.jpg'.format(name)
            path = os.path.join(os.getcwd(), 'app/static/known')
            sav = os.path.join(path, secure_filename(file.filename))
            file.save(sav)
            return(learn_encoding(sav, name, app_name))
        else:
            return(jsonify(message="FILE or NAME missing"))
    else:
        return(jsonify(message="INVALID HTTP METHOD"))


"""
method: POST
headers:{  x-access-tokens:<token>,
            conten-type:multipart-form-data }
body:{  image:<img.jpg>
        }
"""
@app.route('/compare', methods=['POST', 'GET'])
@token_required
def compare(app_name):
    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return(jsonify(message="no filename"))
            else:
                # start = timeit.timeit()         # start time --2
                path = os.path.join(os.getcwd(), 'app/static/')
                sav = os.path.join(path, secure_filename(file.filename))
                file.save(sav)
                return (compare_mod(sav, app_name))
            return jsonify(message="sorry")
        else:
            return(jsonify(message="FILE NOT FOUND"))
    else:
        return(jsonify(status='403', message='method not allowed'))


@app.route('/checklabel', methods=['GET', 'POST'])
@cross_origin(origin='*')
def checklabel():
    if request.method == 'POST':
        if 'image' in request.files and 'name' in request.form:
            file = request.files['image']
            name = request.form['name']
            if file.filename == '':
                return(jsonify(message="error with filename"))
            else:
                path = os.path.join(os.getcwd(), 'app/static/')
                sav = os.path.join(path, secure_filename(file.filename))
                file.save(sav)
                result = searchAndCompare(sav, name)
                return(result)
        else:
            return(jsonify(message="Missing Parameters"))
    else:
        return(jsonify(status='403', message='method not allowed'))


if __name__ == "__main__":
    app.run(host='0.0.0.0')


def learn_encoding(path, name, app):
    try:
        output = []
        x = []
        try:
            encoding = get_encoding(path)
        except Exception as e:
            return({'message': "Sorry, unable to detect face.. change the image and try again"})

        for i, item in enumerate(encoding):
            x.insert(i, item)
        data = {'name': name, 'encoding': x, 'app': app}
        collection.insert_one(data)
        # end = timeit.timeit()               # end time --1
        return jsonify(message="encoding saved successfully")
    except:
        return jsonify(message="an unexpected error occured")


def fetch_faces(app_name):
    data = collection.find({'app': app_name})
    known_names = []
    known_encodings = []
    for i, item in enumerate(data):
        known_names.insert(i, item["name"])
        known_encodings.insert(i, item["encoding"])
    encodings = np.asarray(known_encodings)
    return known_names, encodings


def compare_mod(path, app_name):
    k_names, encodes = fetch_faces(app_name)
    if len(k_names) == 0:
        return(jsonify(message='No data available'))
    else:
        try:
            test_encodes = get_encoding(path)
            dist = face_recognition.face_distance(encodes, test_encodes)
            rank = np.argmin(dist)
            best_match = k_names[rank]
            # set compare threshold [lesser the value better the accuracy]
            if dist[rank] < 0.4000:
                return({'best_match': best_match, 'distance': dist[rank]})
            else:
                return jsonify(message='unknown')
        except Exception as e:
            return({'message': "Sorry, unable to detect face.. change the image and try again"})


def get_encoding(path):
    try:
        id1 = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(
            id1)[0]  # to pass first index of ndarray
        return encoding
    except Exception as e:
        return({'message': "Sorry, unable to detect face.. change the image and try again"})


def searchAndCompare(img, name):
    try:
        test_encode = get_encoding(img)
    except Exception as e:
        return({'message': "Sorry, unable to detect face.. change the image and try again"})

    data = collection.find_one({"name": name}, {'name': 1, 'encoding': 1})
    if data is None:
        return(jsonify(message='No Data Related'))
    else:
        encodes = []
        try:
            encodes.insert(0, data['encoding'])
            encode_data = np.asarray(encodes)
            dist = face_recognition.face_distance(encode_data, test_encode)[0]
            if dist < 0.400:
                return(jsonify(message='image matches the label', distance=dist))
            else:
                return(jsonify(message='unmatched label'))
        except Exception as e:
            return({'message': "Error with data to compare"})
