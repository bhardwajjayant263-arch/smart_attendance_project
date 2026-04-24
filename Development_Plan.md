# Smart Attendance System - Development Plan

This document outlines the structured development plan followed to build the Smart Attendance System with Face Recognition, suitable for final year BCA project evaluation.

## Phase 1: Planning and Requirements Gathering (Weeks 1-2)
- **Objective:** Understand the core requirements and select the appropriate technology stack.
- **Tasks:**
  - Define the problem statement (manual attendance is slow and prone to errors/proxy).
  - Research existing face recognition algorithms (Eigenfaces, Fisherfaces, LBPH).
  - Finalize the tech stack: Python, OpenCV (LBPH Recognizer), SQLite, Flask, HTML/CSS.
  - Draft initial system architecture and UI wireframes.

## Phase 2: Core Backend & Database Design (Weeks 3-4)
- **Objective:** Set up the database and the basic Python script structure.
- **Tasks:**
  - Design the SQLite database schema (`users` table for student info, `attendance` table for logs).
  - Write `init_db()` and `query_db()` functions for database interaction.
  - Test SQLite queries locally.

## Phase 3: Face Detection and Data Gathering (Weeks 5-6)
- **Objective:** Implement the ability to register new students using their webcam.
- **Tasks:**
  - Integrate OpenCV to access the system webcam.
  - Use `haarcascade_frontalface_default.xml` to detect faces in real-time.
  - Create a script to capture 50-100 grayscale sample images of a user's face and save them in the `static/faces` directory with their User ID.
  - Update the database with the new user's Name and Roll No.

## Phase 4: Model Training (Week 7)
- **Objective:** Train the Face Recognizer model using the gathered data.
- **Tasks:**
  - Implement `cv2.face.LBPHFaceRecognizer_create()`.
  - Iterate through the `static/faces` directory, convert images to numpy arrays, and extract their corresponding IDs.
  - Train the model and save it as `trainer.yml`.

## Phase 5: Face Recognition and Attendance Marking (Weeks 8-9)
- **Objective:** Identify students from the live camera feed and mark attendance.
- **Tasks:**
  - Load the trained `trainer.yml` model.
  - Start the webcam and detect faces.
  - Use the model to predict the ID of the detected face along with a confidence score.
  - If confidence is acceptable, fetch the user ID and pass it to the `mark_attendance()` function.
  - Ensure logic is implemented to prevent duplicate attendance entries for the same day.

## Phase 6: Web Interface Development (Weeks 10-11)
- **Objective:** Build a user-friendly interface to control the system.
- **Tasks:**
  - Set up the Flask application (`app.py`).
  - Create HTML templates (`index.html`) using Bootstrap or custom CSS for a modern look.
  - Implement routes for viewing attendance, registering a new user, and starting the attendance tracking session.
  - Connect the OpenCV scripts to the Flask routes.

## Phase 7: Testing and Debugging (Week 12)
- **Objective:** Ensure the system works flawlessly in various conditions.
- **Tasks:**
  - Test the face recognition accuracy in different lighting conditions.
  - Verify that the database correctly logs attendance without duplicates.
  - Fix any module import issues (e.g., configuring virtual environments for `flask` and `opencv-python`).
  - Conduct end-to-end testing (Register -> Train -> Mark Attendance -> View Report).

## Phase 8: Documentation and Final Polish (Weeks 13-14)
- **Objective:** Prepare for the final university presentation and viva.
- **Tasks:**
  - Write the comprehensive `Project_Report.md`.
  - Create the `Viva_Questions.md` preparation guide.
  - Clean up the code, add comments, and ensure a logical folder structure.
  - Final project review.
