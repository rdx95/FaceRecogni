import os
from flask import Flask, request, jsonify
import numpy as np
from werkzeug.utils import secure_filename

import pymongo
from pymongo import MongoClient

import face_recognition


app=Flask(__name__)


###########################################################
## CONFIG TO BE DONE
##
##
cluster = pymongo.MongoClient('mongodb://faceDBUsr:13012020@139.59.34.77:27017/facedb')
db = cluster["facedb"]
collection = db["faces"]
###########################################################

@app.route('/learn', methods=['POST','GET'])
def learn():
    if request.method=='POST':
       file = request.files['image']
       name = request.form['name']
       if file.filename=='':
            return(jsonify(message="no filename"))
       else:
            path=os.path.join(os.getcwd(),'uploads/known')
            sav=os.path.join(path,secure_filename(file.filename))
            file.save(sav)
            return learn_encoding(sav,name)
       return jsonify(message="success")
    else:
        return(jsonify(message="INVALID HTTP METHOD"))  


@app.route('/compare',methods=['POST','GET'])
def compare():
    if request.method=='POST':
        file = request.files['image']
        if file.filename=='':
            return(jsonify(message="no filename"))
        else:
            path=os.path.join(os.getcwd(),'uploads/unknown')
            sav=os.path.join(path,secure_filename(file.filename))
            file.save(sav)
            return (compare_mod(sav))
        return jsonify(message="sorry")

if __name__=="__main__":
	app.run(host='0.0.0.0')

def learn_encoding(path,name):
    output=[]
    x=[]
    encoding=get_encoding(path)
    for i,item in enumerate(encoding):
        x.insert(i,item)
    data = {'name':name,'encoding': x  }
    collection.insert_one(data)
    return jsonify(message="encoding saved successfully")

def fetch_all():
    data=collection.find({})
    known_names=[]
    known_encodings=[]
    for i,item in enumerate(data):
        known_names.insert(i,item["name"])
        known_encodings.insert(i,item["encoding"]) 
    encodings= np.asarray(known_encodings)                  
    return known_names, encodings



def compare_mod(path):
    k_names, encodes = fetch_all()    
    test_encodes=get_encoding(path)
    dist = face_recognition.face_distance(encodes,test_encodes)
    rank=np.argmin(dist)
    best_match=k_names[rank]
    if dist[rank]<0.5:                                                                # set compare threshold [lesser the value better the accuracy]
        #print(best_match)
        #print(dist[rank])
        return(jsonify(best_match=best_match,distance=dist[rank]))
    else:
        return jsonify(message='unknown')


def get_encoding(path):
    id1 = face_recognition.load_image_file(path)
    encoding = face_recognition.face_encodings(id1)[0]      #to pass first index of ndarray
    return encoding
