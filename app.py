import cv2
import numpy as np
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, send_file
import mysql.connector
from PIL import Image
from datetime import datetime, date
import csv

app = Flask(__name__)

# Database Connection
# Load environment variables from .env file
load_dotenv()

# Retrieve the database credentials from environment variables
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_passwd = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

# Database Connection
mydb = mysql.connector.connect(
    host=db_host,
    user=db_user,
    passwd=db_passwd,
    database=db_name
)
mycursor = mydb.cursor()

# Utility Function for CSV Generation
def generate_attendance_csv():
    date_str = datetime.now().strftime('%d-%m-%Y')
    filename = f'attendance_{date_str}.csv'

    mycursor.execute("""
        SELECT a.accs_id, a.accs_prsn, b.prs_name, b.prs_skill, a.accs_added
        FROM attendence_history a
        LEFT JOIN person_details b ON a.accs_prsn = b.prs_nbr
        WHERE a.accs_date = CURDATE()
        ORDER BY a.accs_id DESC
    """)
    data = mycursor.fetchall()

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['ID', 'Person Number', 'Name', 'Branch', 'Timestamp'])
        for row in data:
            csvwriter.writerow(row)

    return filename

# Generate dataset
def generate_dataset(nbr):
    face_classifier = cv2.CascadeClassifier(
        "C:/Users/Yash/PycharmProjects/flask_face_attendence/resources/haarcascade_frontalface_default.xml")

    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return None  # No faces detected

        for (x, y, w, h) in faces:
            cropped_face = img[y:y + h, x:x + w]
            return cropped_face  # Return the first detected face

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera could not be accessed.")
        return

    mycursor.execute("SELECT IFNULL(MAX(img_id), 0) FROM img_dataset")
    row = mycursor.fetchone()
    img_id = row[0]
    max_imgid = img_id + 100
    count_img = 0

    while True:
        ret, img = cap.read()
        if not ret:
            break  # Break the loop if the frame is not captured

        face = face_cropped(img)
        if face is not None:
            count_img += 1
            img_id += 1
            face = cv2.resize(face, (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            file_name_path = f"dataset/{nbr}.{img_id}.jpg"
            cv2.imwrite(file_name_path, face)
            cv2.putText(face, str(count_img), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

            mycursor.execute("INSERT INTO img_dataset (img_id, img_person) VALUES (%s, %s)", (img_id, nbr))
            mydb.commit()

            frame = cv2.imencode('.jpg', face)[1].tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            if cv2.waitKey(1) == 13 or img_id >= max_imgid:
                break

    cap.release()
    cv2.destroyAllWindows()

# Train Classifier
@app.route('/train_classifier/<nbr>')
def train_classifier(nbr):
    dataset_dir = "C:/Users/Yash/PycharmProjects/flask_face_attendence/dataset"
    path = [os.path.join(dataset_dir, f) for f in os.listdir(dataset_dir)]
    faces = []
    ids = []

    for image in path:
        img = Image.open(image).convert('L')
        imageNp = np.array(img, 'uint8')
        id = int(os.path.split(image)[1].split(".")[1])
        faces.append(imageNp)
        ids.append(id)

    ids = np.array(ids)

    # Adjusting parameters for the classifier
    clf = cv2.face.LBPHFaceRecognizer_create(grid_x=8, grid_y=8, radius=1, neighbors=8, threshold=80)
    clf.train(faces, ids)
    clf.write("classifier.xml")

    return redirect('/')

# Face Recognition
def face_recognition():
    def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf):
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = classifier.detectMultiScale(gray_image, scaleFactor, minNeighbors)

        detected_ids = set()  # Track detected IDs in the current frame

        for (x, y, w, h) in features:
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            id, pred = clf.predict(gray_image[y:y + h, x:x + w])
            confidence = int(100 * (1 - pred / 300))

            if confidence > 70:
                detected_ids.add(id)  # Add detected ID to the set

                mycursor.execute("""
                    SELECT a.img_person, b.prs_name, b.prs_skill 
                    FROM img_dataset a
                    LEFT JOIN person_details b ON a.img_person = b.prs_nbr
                    WHERE img_id = %s
                """, (id,))
                row = mycursor.fetchone()
                if row:
                    pnbr, pname, pskill = row
                    mycursor.execute("""
                        SELECT COUNT(*) 
                        FROM attendence_history 
                        WHERE accs_date = CURDATE() AND accs_prsn = %s
                    """, (pnbr,))
                    if mycursor.fetchone()[0] == 0:
                        mycursor.execute("""
                            INSERT INTO attendence_history (accs_date, accs_prsn) 
                            VALUES (%s, %s)
                        """, (date.today(), pnbr))
                        mydb.commit()
                        cv2.putText(img, pname + ' | ' + pskill, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                    (153, 255, 255), 2, cv2.LINE_AA)

        return img

    faceCascade = cv2.CascadeClassifier(
        "C:/Users/Yash/PycharmProjects/flask_face_attendence/resources/haarcascade_frontalface_default.xml")
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.read("classifier.xml")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera is not accessible")
        return
    cap.grab()
    while True:
        ret, img = cap.read()
        if not ret:
            break  # Break the loop if the frame is not captured

        img = draw_boundary(img, faceCascade, 1.1, 10, (255, 255, 0), "Face", clf)

        frame = cv2.imencode('.jpg', img)[1].tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()
    cv2.destroyAllWindows()

# Routes
@app.route('/')
def home():
    mycursor.execute("SELECT prs_nbr, prs_name, prs_skill, prs_active, prs_added FROM person_details")
    data = mycursor.fetchall()
    return render_template('index.html', data=data)

@app.route('/addprsn')
def addprsn():
    mycursor.execute("SELECT IFNULL(MAX(prs_nbr) + 1, 101) FROM person_details")
    row = mycursor.fetchone()
    nbr = row[0]
    return render_template('addprsn.html', newnbr=int(nbr))

@app.route('/addprsn_submit', methods=['POST'])
def addprsn_submit():
    prsnbr = request.form.get('txtnbr')
    prsname = request.form.get('txtname')
    prsskill = request.form.get('optskill')
    mycursor.execute("""
        INSERT INTO person_details (prs_nbr, prs_name, prs_skill) 
        VALUES (%s, %s, %s)
    """, (prsnbr, prsname, prsskill))
    mydb.commit()
    return redirect(url_for('vfdataset_page', prs=prsnbr))

@app.route('/vfdataset_page/<prs>')
def vfdataset_page(prs):
    return render_template('gendataset.html', prs=prs)

@app.route('/vidfeed_dataset/<nbr>')
def vidfeed_dataset(nbr):
    return Response(generate_dataset(nbr), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    return Response(face_recognition(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/fr_page')
def fr_page():
    mycursor.execute("""
        SELECT a.accs_id, a.accs_prsn, b.prs_name, b.prs_skill, a.accs_added
        FROM attendence_history a
        LEFT JOIN person_details b ON a.accs_prsn = b.prs_nbr
        WHERE a.accs_date = CURDATE()
        ORDER BY a.accs_id DESC
    """)
    data = mycursor.fetchall()
    return render_template('fr_page.html', data=data)

@app.route('/countTodayScan')
def countTodayScan():
    mycursor.execute("SELECT COUNT(*) FROM attendence_history WHERE accs_date = CURDATE()")
    row = mycursor.fetchone()
    rowcount = row[0]
    return jsonify({'rowcount': rowcount})

@app.route('/loadData', methods=['GET', 'POST'])
def loadData():
    mycursor.execute("""
        SELECT a.accs_id, a.accs_prsn, b.prs_name, b.prs_skill, DATE_FORMAT(a.accs_added, '%H:%i:%s')
        FROM attendence_history a
        LEFT JOIN person_details b ON a.accs_prsn = b.prs_nbr
        WHERE a.accs_date = CURDATE()
        ORDER BY a.accs_id DESC
    """)
    data = mycursor.fetchall()
    return jsonify(response=data)

@app.route('/generate_attendance_csv')
def generate_attendance_csv_route():
    filename = generate_attendance_csv()
    return send_file(filename, as_attachment=True)

@app.route('/students')
def student():
    mycursor.execute("SELECT prs_nbr, prs_name, prs_skill, prs_active, prs_added FROM person_details")
    data = mycursor.fetchall()
    return render_template('students.html', data=data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
