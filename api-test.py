import random

import requests

# Base URL of the API
base_url = "http://localhost:8000"


# Helper function to generate random data
def generate_random_student_data():
    return {
        "firstname": "John",
        "lastname": "Doe",
        "generation": random.randint(2010, 2022),
        "gender": random.choice(["male", "female"]),
    }


def generate_random_classroom_data():
    return {
        "lecturer_name": "Professor "
        + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5)),
        "duration": random.randint(1, 4),  # Assuming duration is in hours
        "lecture_time": random.uniform(
            0, 24
        ),  # Assuming lecture time is in 24-hour format
        "late_penalty_duration": random.uniform(
            0, 1
        ),  # Assuming late penalty duration in hours
        "subject_name": "Mathematics",  # Assuming a fixed subject for simplicity
    }


def generate_random_attendance_data(enrollment_id):
    return {
        "last_record": random.uniform(0, 10),
        "entry_time": random.uniform(0, 10000),
        "enrollment_id": enrollment_id,
    }


# Step 1: Create Classroom
classroom_data = [
    generate_random_classroom_data() for _ in range(3)
]  # Generate 3 random classrooms
class_response = requests.post(f"{base_url}/classrooms/", json=classroom_data)
if class_response.status_code == 200:
    print("Classrooms created successfully!")
else:
    print("Failed to create classrooms. Status code:", class_response.status_code)

class_data = class_response.json()["data"]

# Step 2: Create Students
student_data = [
    generate_random_student_data() for _ in range(5)
]  # Generate 5 random students
print(student_data)
response = requests.post(f"{base_url}/students/", json=student_data)
if response.status_code == 200:
    print("Students created successfully!")
else:
    print("Failed to create students. Status code:", response.status_code)

# Step 3: Enroll Students
enrollment_data = []
classrooms = response.json()["data"]  # Get the classrooms created in Step 1

for student in classrooms:
    enrollment_data.append(
        {"student_id": student["id"], "class_id": random.choice(class_data)["id"]}
    )

enrollment_result = []
for enroll in enrollment_data:
    sid = enroll["student_id"]
    response = requests.post(f"{base_url}/students/enrollment/", json=enroll)
    print(response.json())
    if response.status_code == 200:
        print("Students enrolled successfully!")
        enrollment_result.append(response.json()["data"])
    else:
        print("Failed to enroll students. Status code:", response.status_code)

print(enrollment_result)
# Step 4: Create Attendance
attendance_data = [
    generate_random_attendance_data(random.choice(enrollment_result)["id"])
    for _ in range(5)  # Generate 5 random attendance records
]

print(attendance_data)

response = requests.post(f"{base_url}/attendances/", json=attendance_data)
if response.status_code == 200:
    print("Attendance created successfully!")
else:
    print("Failed to create attendance. Status code:", response.status_code)

# Step 5: Fetch Student Info by Enrollment ID
enrollment_id = random.choice(enrollment_data)["student_id"]
response = requests.get(f"{base_url}/students/enrollment/{enrollment_id}")

if response.status_code == 200:
    print("Student info fetched successfully by enrollment ID!")
    print(response.json())
else:
    print(
        "Failed to fetch student info by enrollment ID. Status code:",
        response.status_code,
    )
