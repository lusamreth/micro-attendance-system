import pickle
import time

import cv2
import numpy as np
import requests
import tensorflow as tf
from deepface import DeepFace
from tensorflow.keras.models import load_model

# Paths to your files
model_file_path = "face_recognition_model.h5"
label_encoder_file_path = "label_encoder.pkl"
api_base_url = "http://localhost:8000"  # Replace with actual API base URL

# Check TensorFlow GPU availability
gpus = tf.config.list_physical_devices("GPU")
if gpus:
    print("GPU is available.")
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)
else:
    print("GPU is not available. TensorFlow will use CPU.")

# Load the pre-trained model
model = load_model(model_file_path)

# Load the label encoder
with open(label_encoder_file_path, "rb") as f:
    label_encoder = pickle.load(f)


# Function to extract face encodings and bounding boxes using DeepFace
def get_face_data(frame):
    df = DeepFace.represent(
        img_path=frame,
        model_name="ArcFace",
        enforce_detection=False,
        detector_backend="retinaface",
    )

    if len(df) == 0:
        return [], []

    face_encodings = [np.array(face["embedding"]) for face in df]
    face_bounding_boxes = [face["facial_area"] for face in df]

    return face_encodings, face_bounding_boxes


# Fetch classrooms from API
def fetch_classrooms():
    classrooms_url = f"{api_base_url}/classrooms/"
    response = requests.get(classrooms_url)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print("Failed to fetch classrooms.")
        return []


# Fetch enrollments from API
def fetch_enrollments(class_id):
    enrollments_url = f"{api_base_url}/stats/enrollment/{class_id}"
    response = requests.get(enrollments_url)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print("Failed to fetch enrollments.")
        return []


# Fetch student ID by name from API
def fetch_student_id_by_name(firstname, lastname=None):
    lastname = "" if not lastname else lastname
    students_url = f"{api_base_url}/students/name/{firstname}"
    response = requests.get(students_url)
    if response.status_code == 200:
        student_data = response.json()["data"]
        return student_data["id"] if student_data["id"] else None
    else:
        print(f"Failed to fetch student: {firstname} {lastname}")
        return None


attendance_local_maps = {}


# Check if the student is enrolled
def is_student_enrolled(student_id, enrollments):
    return student_id in enrollments


# Create attendance record for a student
def create_attendance(enroll_id):
    attendance_url = f"{api_base_url}/attendances/"
    payload = [
        {"enrollment_id": enroll_id, "entry_time": time.time(), "last_record": 0}
    ]
    print("P", payload)
    response = requests.post(attendance_url, json=payload)
    if response.status_code == 201 or response.status_code == 200:
        print(f"Attendance created for enroll : {enroll_id}.")
        attendance_local_maps[enroll_id] = 1
        return True
    else:
        print("Failed to create attendance.")
        return False


# Display TUI and select classroom
def select_classroom():
    classrooms = fetch_classrooms()
    if not classrooms:
        return None

    print("\nAvailable Classrooms:")
    for idx, classroom in enumerate(classrooms):
        print(f"{idx + 1}. {classroom['subject_name']} by {classroom['lecturer_name']}")
    user_res = input("\nSelect a classroom (by number): ")
    choice = int(user_res) - 1
    return classrooms[choice] if 0 <= choice < len(classrooms) else None


def has_overlap(array1, array2):
    # Convert array2 to a set for efficient lookup
    set_array2 = set(array2)

    # Check if any element in array1 exists in set_array2
    for element in array1:
        if element in set_array2:
            return True  # Overlap found

    return False  # No overlap found


# Main attendance taking loop
def take_attendance():
    selected_classroom = select_classroom()
    if not selected_classroom:
        print("No classroom selected. Exiting.")
        return

    print(f"\nClassroom '{selected_classroom['subject_name']}' selected.")
    enrollments_from_class = fetch_enrollments(selected_classroom["id"])
    enrollment_dict = {
        enrollment["student_id"]: enrollment for enrollment in enrollments_from_class
    }

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings, face_bounding_boxes = get_face_data(rgb_frame)

        for i, (face_encoding, bounding_box) in enumerate(
            zip(face_encodings, face_bounding_boxes)
        ):
            face_encoding = np.expand_dims(face_encoding, axis=0)
            predictions = model.predict(face_encoding)
            confidence_level = np.max(predictions)

            if confidence_level < 0.60:
                predicted_label = "Unknown"
            else:
                predicted_class = np.argmax(predictions, axis=1)
                predicted_label = label_encoder.inverse_transform(predicted_class)[0]

            # firstname, lastname = (
            #     predicted_label.split(" ")
            #     if len(predicted_label.split(" ")) == 2
            #     else (None, None)
            # )

            splt = predicted_label.split(" ")
            firstname = splt[0].lower()
            lastname = ""

            x, y, w, h = (
                bounding_box["x"],
                bounding_box["y"],
                bounding_box["w"],
                bounding_box["h"],
            )

            print(firstname, lastname, attendance_local_maps)
            if firstname:
                student_id = fetch_student_id_by_name(firstname, lastname)

                print(
                    student_id,
                    firstname,
                    lastname,
                    attendance_local_maps,
                    is_student_enrolled(student_id, enrollment_dict),
                    enrollment_dict,
                )
                if student_id and is_student_enrolled(student_id, enrollment_dict):
                    stud_enrollment = enrollment_dict.get(student_id) or {}
                    if attendance_local_maps.get(stud_enrollment.get("id")):
                        cv2.putText(
                            frame,
                            "attended",
                            (x, y + 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 255, 0),
                            2,
                        )
                    else:
                        res = create_attendance(stud_enrollment.get("id"))
                        print("RES", res)
                        if res:
                            cv2.putText(
                                frame,
                                "enrolled",
                                (x, y + 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (0, 255, 0),
                                2,
                            )

                if student_id is None:
                    cv2.putText(
                        frame,
                        "not yet enrolled",
                        (x, y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (0, 50, 225),
                        2,
                    )

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label_with_confidence = f"{predicted_label} ({confidence_level * 100:.2f}%)"

            cv2.putText(
                frame,
                label_with_confidence,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Face Recognition Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


# Start the attendance system
if __name__ == "__main__":
    take_attendance()
