import requests

origin = "http://localhost:8000"
classrooms_url = origin + "/classrooms"  # Replace with actual API URL


def fetch_classrooms():
    response = requests.get(classrooms_url)
    if response.status_code == 200:
        data = response.json()["data"]
        return data
    else:
        print("Failed to fetch classrooms.")
        return []


def select_classroom():
    classrooms = fetch_classrooms()
    if not classrooms:
        return None
    for idx, classroom in enumerate(classrooms):
        print(f"{idx + 1}. {classroom['subject_name']} by {classroom['lecturer_name']}")
    choice = int(input("Select a classroom: ")) - 1
    return classrooms[choice] if 0 <= choice < len(classrooms) else None


def fetch_enrollments(class_id):
    enrollments_url = origin + f"/stats/enrollment/{class_id}"
    response = requests.get(enrollments_url)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print("Failed to fetch enrollments.")
        return []


enrollments = fetch_enrollments(selected_classroom["id"])
enrollment_dict = {enrollment["student_id"]: enrollment for enrollment in enrollments}


def is_student_enrolled(student_id):
    return student_id in enrollment_dict
