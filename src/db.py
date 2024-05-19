import os
import sqlite3


def init_db_root():
    PWD = os.getcwd()
    DB_PATH = PWD + "/db/"
    DB_NAME = DB_PATH + "attendance.db"

    try:
        list_dir = os.listdir(DB_PATH)
        print("listing db: ", list_dir)
        if list_dir.count("attendance.db") == 0:
            with open(DB_NAME, "w+") as file:
                pass

    except Exception as e:
        print("making db...", DB_NAME)
        os.mkdir(DB_PATH)
    return DB_NAME


def open_db():
    conn = sqlite3.connect(init_db_root())
    return conn


conn = open_db()


# mapper = AttendanceMapper(conn)
# mapper.init_table()
# mapper.insert(
#     create_attd(
#         name="test", classroom="test", last_record=0, entry_time=0, subject="test"
#     )
# )
# press = mapper.list()
# res = mapper.get(press[0].id)

# print(press, res)
