from flask import Blueprint, render_template, request, redirect, url_for, Response
import cv2
import numpy as np
from utils.db_utils import execute_query, commit_changes

bp = Blueprint('dataset', __name__)


@bp.route('/vidfeed_dataset/<nbr>')
def vidfeed_dataset(nbr):
    return Response(generate_dataset(nbr), mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_dataset(nbr):
    face_classifier = cv2.CascadeClassifier(
        "resources/haarcascade_frontalface_default.xml"
    )

    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            return None
        for (x, y, w, h) in faces:
            return img[y:y + h, x:x + w]

    cap = cv2.VideoCapture(0)

    # Get the last image ID from the database
    execute_query("SELECT IFNULL(MAX(img_id), 0) FROM img_dataset")
    lastid = execute_query("SELECT IFNULL(MAX(img_id), 0) FROM img_dataset")[0][0]
    img_id = lastid
    max_imgid = img_id + 100  # Limit the number of images to capture
    count_img = 0

    while True:
        ret, img = cap.read()
        if not ret:
            continue

        face = face_cropped(img)
        if face is not None:
            count_img += 1
            img_id += 1
            face = cv2.resize(face, (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            file_name_path = f"dataset/{nbr}.{img_id}.jpg"
            cv2.imwrite(file_name_path, face)
            cv2.putText(face, str(count_img), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            execute_query(
                "INSERT INTO img_dataset (img_id, img_person) VALUES (%s, %s)",
                (img_id, nbr)
            )
            commit_changes()

            # Convert image to JPEG format
            _, buffer = cv2.imencode('.jpg', face)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            # Stop capturing if we reach the max image ID
            if img_id >= max_imgid:
                break

    cap.release()
    cv2.destroyAllWindows()
