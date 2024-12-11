from flask import Blueprint

bp = Blueprint('main', __name__)

from . import dataset_routes, face_recognition_routes, user_routes
