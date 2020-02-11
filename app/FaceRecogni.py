import os
import timeit
from flask import Flask, request, jsonify, render_template
import numpy as np
from werkzeug.utils import secure_filename

import pymongo
from pymongo import MongoClient

import face_recognition


app = Flask(__name__)


###########################################################
# CONFIG TO BE DONE
app.config.from_pyfile('config.py')
cluster = pymongo.MongoClient(app.config["URI"])
db = cluster["facedb"]
collection = db["faces"]
###########################################################


@app.route('/', methods=['GET'])
def home():
    if request.method=='GET' :
        dict = {}
        dat = collection.find({}, {'name': 1})
        for i in dat:
            if os.path.exists('static/known/{}.jpg'.format(i['name'])):
                dict.update({i['name']: ('known/{}.jpg'.format(i['name']))})
            else:
                pass
        print(dict)
        return render_template('index.html', data=dict)
    else :
        return(jsonify(message='INVALID HTTP METHOD'))


@app.route('/learn', methods=['POST', 'GET'])
def learn():
    if request.method == 'POST': 
        if 'image' in request.files and 'name' in request.form:
            start = timeit.timeit()             # start time --1
            file = request.files['image']
            name = request.form['name']
            file.filename = '{}.jpg'.format(name)
            path = os.path.join(os.getcwd(), 'static/known')
            sav = os.path.join(path, secure_filename(file.filename))
            file.save(sav)
            return learn_encoding(sav, name, start)
        else :
            return(jsonify(message="FILE or NAME missing"))
    else:
        return(jsonify(message="INVALID HTTP METHOD"))


@app.route('/compare', methods=['POST', 'GET'])
def compare():
    if request.method == 'POST':
        if 'image' in request.files :
            file = request.files['image']
            if file.filename == '':
                return(jsonify(message="no filename"))
            else:
                start = timeit.timeit()         # start time --2
                path = os.path.join(os.getcwd(), 'static/')
                sav = os.path.join(path, secure_filename(file.filename))
                file.save(sav)
                return (compare_mod(sav,start))
            return jsonify(message="sorry")
        else :
            return(jsonify(message="FILE NOT FOUND"))    
    else:
        return(jsonify(status='403', message='method not allowed'))


if __name__ == "__main__":
    app.run(host='0.0.0.0')


def learn_encoding(path, name, start):
    output = []
    x = []
    encoding = get_encoding(path)
    for i, item in enumerate(encoding):
        x.insert(i, item)
    data = {'name': name, 'encoding': x}
    collection.insert_one(data)
    end = timeit.timeit()               # end time --1
    return jsonify(message="encoding saved successfully",time=(end - start))


def fetch_all():
    data = collection.find({})
    known_names = []
    known_encodings = []
    for i, item in enumerate(data):
        known_names.insert(i, item["name"])
        known_encodings.insert(i, item["encoding"])
    encodings = np.asarray(known_encodings)
    return known_names, encodings


def compare_mod(path, start):
    k_names, encodes = fetch_all()
    test_encodes = get_encoding(path)
    dist = face_recognition.face_distance(encodes, test_encodes)
    rank = np.argmin(dist)
    best_match = k_names[rank]
    # set compare threshold [lesser the value better the accuracy]
    if dist[rank] < 0.5:
        # print(best_match)
        # print(dist[rank])
        end = timeit.timeit()           # end time --2
        return(jsonify(best_match=best_match, distance=dist[rank], time=(end - start)))
    else:
        return jsonify(message='unknown')


def get_encoding(path):
    id1 = face_recognition.load_image_file(path)
    encoding = face_recognition.face_encodings(
        id1)[0]  # to pass first index of ndarray
    return encoding
