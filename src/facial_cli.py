from datetime import datetime


def collect_classroom_info():
    classroom_info = {}

    print("Please enter the classroom information:")

    classroom_info["lecturer_name"] = input("Lecturer Name: ")
    classroom_info["duration"] = int(input("Duration (in hours): ")) * 3600

    while True:
        lecture_time_input = input("Lecture Time (in 24-hour format, e.g., 13:30): ")
        try:
            lecture_time = datetime.strptime(lecture_time_input, "%H:%M")
            classroom_info["lecture_time"] = (
                lecture_time.hour + lecture_time.minute / 60.0
            )
            break
        except ValueError:
            print(
                "Invalid time format. Please enter the time in 24-hour format (HH:MM)."
            )

    classroom_info["late_penalty_duration"] = (
        float(input("Late Penalty Duration (in hours): ")) * 3600
    )
    classroom_info["subject_name"] = input("Subject Name: ")

    return classroom_info


if __name__ == "__main__":
    classroom_info = collect_classroom_info()
    print("\nCollected Classroom Information:")
    for key, value in classroom_info.items():
        print(f"{key}: {value}")
