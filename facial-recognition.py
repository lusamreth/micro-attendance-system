import pickle

import cv2
import face_recognition
import numpy as np
import requests

# Load SVM model
with open("full_trained_svm_model.clf", "rb") as f:
    clf = pickle.load(f)

# Initialize variables
process_this_frame = True
known_faces = []  # List to store known faces to avoid duplicates


def create_class(class_name):
    try:
        # Replace 'your_attendance_api_url' with your actual API endpoint
        url = "http://localhost:8000/classroom/"
        payload = {"fullname": class_name}
        newclass = {
            "lecturer_name": "string",
            "duration": 0,
            "lecture_time": 0,
            "late_penalty_duration": 0,
            "subject_name": "string",
        }

        headers = {"Content-Type": "application/json"}

        response = requests.get(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Attendance recorded for:", class_name)
    except Exception as e:
        print("Error occurred while sending attendance:", e)


# Function to send POST request to attendance API
def send_attendance(student_name):
    try:
        # Replace 'your_attendance_api_url' with your actual API endpoint
        url = "http://localhost:8000/attendances/"
        payload = {"student_name": student_name}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Attendance recorded for:", student_name)
    except Exception as e:
        print("Error occurred while sending attendance:", e)


def get_name(student_name):
    try:
        # Replace 'your_attendance_api_url' with your actual API endpoint
        url = "http://localhost:8000/attendances/"
        payload = {"fullname": student_name}
        headers = {"Content-Type": "application/json"}

        response = requests.get(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Attendance recorded for:", student_name)
    except Exception as e:
        print("Error occurred while sending attendance:", e)


# Start video capture
video_capture = cv2.VideoCapture(0)

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, face_locations
        )

        face_names = []

        for face_encoding in face_encodings:
            name = "Unknown"

            # Predict the name using the SVM model
            name = clf.predict([face_encoding])[0]

            # Check if the face is not a duplicate
            if name not in known_faces:
                known_faces.append(name)
                send_attendance(name)

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(
            frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED
        )
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow("AI Student Attendance System", frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
