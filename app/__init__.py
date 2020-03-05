from flask import Flask

app = Flask(__name__)

from app import FaceRecogni
from app import view