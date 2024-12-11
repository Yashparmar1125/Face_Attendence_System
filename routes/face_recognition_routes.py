from flask import Blueprint, Response
import cv2
from utils.face_utils import face_recognition

bp = Blueprint('face_recognition', __name__)

@bp.route('/video_feed')
def video_feed():
    return Response(face_recognition(), mimetype='multipart/x-mixed-replace; boundary=frame')
