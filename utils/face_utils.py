import cv2
import numpy as np
from datetime import date
import time
from utils.db_utils import execute_query, commit_changes

def face_recognition():
    def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, clf):
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = classifier.detectMultiScale(gray_image, scaleFactor, minNeighbors)
        global justscanned
        global pause_cnt
        global cnt  # Ensure cnt is declared as global if it's used in this scope
        pause_cnt += 1
        coords = []
        for (x, y, w, h) in features:
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            id, pred = clf.predict(gray_image[y:y + h, x:x + w])
            confidence = int(100 * (1 - pred / 300))
            if confidence > 70 and not justscanned:
                cnt += 1
                n = (100 / 30) * cnt
                w_filled = (cnt / 30) * w
                cv2.putText(img, f'{int(n)} %', (x + 20, y + h + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (153, 255, 255), 2, cv2.LINE_AA)
                cv2.rectangle(img, (x, y + h + 40), (x + w, y + h + 50), color, 2)
                cv2.rectangle(img, (x, y + h + 40), (x + int(w_filled), y + h + 50), (153, 255, 255), cv2.FILLED)
                row = execute_query(
                    "SELECT a.img_person, b.prs_name, b.prs_skill "
                    "FROM img_dataset a "
                    "LEFT JOIN prs_mstr b ON a.img_person = b.prs_nbr "
                    "WHERE img_id = %s", (id,)
                )
                if row:
                    pnbr, pname, pskill = row[0]
                    if int(cnt) == 30:
                        cnt = 0
                        execute_query(
                            "INSERT INTO accs_hist (accs_date, accs_prsn) VALUES (%s, %s)",
                            (str(date.today()), pnbr)
                        )
                        commit_changes()
                        cv2.putText(img, f'{pname} recognized', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                    (0, 255, 0), 2, cv2.LINE_AA)
                        justscanned = True
            else:
                justscanned = False  # Allow scanning again if not recognized

        return img

    # Initialize variables
    global justscanned
    global pause_cnt
    global cnt
    justscanned = False
    pause_cnt = 0
    cnt = 0

    # Load classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Load the trained model
    recognizer.read('trained_model.yml')  # Ensure this path is correct

    # Initialize video capture
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Apply face recognition
        frame = draw_boundary(frame, face_cascade, scaleFactor=1.1, minNeighbors=5, color=(0, 255, 0), clf=recognizer)

        # Display the result
        cv2.imshow('Face Recognition', frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    video_capture.release()
    cv2.destroyAllWindows()
