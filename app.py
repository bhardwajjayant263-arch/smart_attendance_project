import cv2
import os
import sqlite3
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'smart_attendance_secret'

DB_NAME = "attendance.db"

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, roll_no TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date TEXT, time TEXT,
                 FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

# Helper to execute DB queries
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    # Fetch today's attendance
    today = datetime.now().strftime("%Y-%m-%d")
    records = query_db('''SELECT users.name, users.roll_no, attendance.time 
                          FROM attendance 
                          JOIN users ON attendance.user_id = users.id 
                          WHERE attendance.date = ? ORDER BY attendance.time DESC''', (today,))
    return render_template('index.html', records=records, date=today)

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    roll_no = request.form['roll_no']
    
    try:
        # Insert user into DB
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users (name, roll_no) VALUES (?, ?)", (name, roll_no))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        
        # Capture Faces
        cam = cv2.VideoCapture(0)
        face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        count = 0
        os.makedirs('dataset', exist_ok=True)
        
        while True:
            ret, img = cam.read()
            if not ret: break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                count += 1
                cv2.imwrite(f"dataset/User.{user_id}.{count}.jpg", gray[y:y+h, x:x+w])
            
            cv2.imshow('Capturing Faces - Look at the camera', img)
            if cv2.waitKey(100) & 0xFF == 27: # Press 'ESC' to stop
                break
            elif count >= 50: # Take 50 face samples
                break
                
        cam.release()
        cv2.destroyAllWindows()
        
        # Train Model immediately after registration
        train_model()
        flash('Registration Successful! Faces captured and model trained.', 'success')
        
    except sqlite3.IntegrityError:
        flash('Error: Roll number already exists!', 'danger')
        
    return redirect(url_for('index'))

def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    if not os.path.exists('dataset'):
        return
        
    imagePaths = [os.path.join('dataset', f) for f in os.listdir('dataset')]
    faceSamples = []
    ids = []
    
    for imagePath in imagePaths:
        if not imagePath.endswith('.jpg'): continue
        PIL_img = Image.open(imagePath).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')
        user_id = int(os.path.split(imagePath)[-1].split(".")[1])
        
        faces = detector.detectMultiScale(img_numpy)
        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y+h, x:x+w])
            ids.append(user_id)
            
    if faceSamples:
        os.makedirs('trainer', exist_ok=True)
        recognizer.train(faceSamples, np.array(ids))
        recognizer.write('trainer/trainer.yml')

@app.route('/start_attendance')
def start_attendance():
    if not os.path.exists('trainer/trainer.yml'):
        flash('No trained model found. Please register a student first.', 'danger')
        return redirect(url_for('index'))
        
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    while True:
        ret, im = cam.read()
        if not ret: break
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x+w, y+h), (0, 255, 0), 2)
            user_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            
            # Confidence less than 100 means good match
            if confidence < 100:
                user = query_db("SELECT name FROM users WHERE id = ?", (user_id,), one=True)
                name = user['name'] if user else "Unknown"
                conf_str = f"  {round(100 - confidence)}%"
                
                # Mark attendance
                mark_attendance(user_id)
            else:
                name = "Unknown"
                conf_str = f"  {round(100 - confidence)}%"
                
            cv2.putText(im, str(name), (x+5, y-5), font, 1, (255, 255, 255), 2)
            cv2.putText(im, str(conf_str), (x+5, y+h-5), font, 1, (255, 255, 0), 1)
            
        cv2.imshow('Taking Attendance - Press ESC to stop', im)
        if cv2.waitKey(10) & 0xFF == 27: # ESC to stop
            break
            
    cam.release()
    cv2.destroyAllWindows()
    flash('Attendance session ended.', 'success')
    return redirect(url_for('index'))

def mark_attendance(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")
    
    # Check if already marked for today
    existing = query_db("SELECT id FROM attendance WHERE user_id = ? AND date = ?", (user_id, today), one=True)
    if not existing:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO attendance (user_id, date, time) VALUES (?, ?, ?)", (user_id, today, now))
        conn.commit()
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
