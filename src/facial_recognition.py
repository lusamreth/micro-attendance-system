import json
import os
import pickle

import cv2
import face_recognition
import numpy as np
import requests

from .facial_cli import collect_classroom_info

# Load SVM model
with open("full_trained_svm_model.clf", "rb") as f:
    clf = pickle.load(f)

# Initialize variables
process_this_frame = True
known_faces = []  # List to store known faces to avoid duplicates
classroom_id = None


# Function to send POST request to attendance API
def fetch_by_name(name):
    try:
        # Replace 'your_attendance_api_url' with your actual API endpoint
        url = "http://localhost:8000/students/name/{}".format(name)

        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Attendance recorded for:", name)
        return response.json()["data"]
    except Exception as e:
        print("Error occurred while registering student :", e)


# Function to send POST request to attendance API
def send_attendance(enrollment_id):
    try:
        # Replace 'your_attendance_api_url' with your actual API endpoint
        url = "http://localhost:8000/attendances/"
        payload = [
            {
                "enrollment_id": enrollment_id,
                "last_record": 0,
                "entry_time": 0,
            },
        ]

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Attendance recorded for:", enrollment_id)
        return response.json()["data"]

    except Exception as e:
        print("Error occurred while sending attendance:", e)


def create_student(student_name):
    try:
        # Replace 'your_attendance_api_url' with your actual API endpoint
        url = "http://localhost:8000/students/"
        firstname, lastname = student_name.split(" ")

        payload = [
            {
                "firstname": firstname or "",
                "lastname": lastname or "",
                "gender": "N/A",
                "generation": 1,
            }
        ]
        headers = {"Content-Type": "application/json"}
        print("PAY LOAD", payload)
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Attendance recorded for:", student_name)
        return response.json()["data"]
    except Exception as e:
        print("Error occurred while registering student :", e)


def create_enrollment(student_id, classroom_id):
    try:
        # Replace 'your_attendance_api_url' with your actual API endpoint
        url = "http://localhost:8000/students/enrollment"

        payload = {"student_id": student_id, "class_id": classroom_id}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()["data"]
    except Exception as e:
        print("Error occurred while sending attendance:", e)


def fetch_class(subject):
    try:
        # Replace 'your_attendance_api_url' with your actual API endpoint
        url = "http://localhost:8000/attendances/classroom/subject/{}".format(subject)
        headers = {"Content-Type": "application/json"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("classromm found for:", subject)
        return response.json()
    except Exception as e:
        print("Error occurred while fetching class:", e)


def create_class():
    class_info = collect_classroom_info()
    # result = fetch_class(class_info["subject_name"])
    # fatal error right here
    # if result is not None and result["data"] is not None:
    #     return [result["data"]]

    try:
        # Replace 'your_attendance_api_url' with your actual API endpoint
        url = "http://localhost:8000/classrooms/"
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=[class_info], headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("classroom recorded for:", class_info)
        return response.json()["data"]
    except Exception as e:
        print("Error occurred while creating class:", e)


class_response = create_class()
print(class_response)
if class_response is None:
    print("Exit cuz Error occurred ")
    os._exit(1)
else:
    classroom_id = class_response[0]["id"]
    print("class id confirmed : ", classroom_id)


def main():
    global process_this_frame
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
                    # send_attendance(name,class)
                    known_faces.append(name)
                    student = None
                    student_by_name = fetch_by_name(name)
                    if student_by_name is not None:
                        print("Found existing student: ", name)
                        student = [student_by_name]
                    else:
                        student = create_student(name)

                    if student is None:
                        print("Error registering student...")
                    else:
                        if len(student) > 0:
                            enrollment = create_enrollment(
                                student.pop()["id"], classroom_id
                            )
                            if enrollment is None:
                                print("Error enrolling student...")
                            else:
                                send_attendance(enrollment["id"])

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
            cv2.putText(
                frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1
            )
            cv2.putText(
                frame, "sss", (left + 6, bottom - 3), font, 1.0, (255, 255, 255), 1
            )

        # Display the resulting image
        cv2.imshow("AI Student Attendance System", frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
