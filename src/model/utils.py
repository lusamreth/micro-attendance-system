import sqlite3

from src.model.model_exception import NotFoundError


def check_constraints(conn: sqlite3.Connection, table: str, id: str):
    cursor = conn.execute("SELECT * FROM '{}' where id = '{}'".format(table, id))
    # cursor = conn.execute("SELECT id FROM '{}'".format(table, id))
    entity = cursor.fetchone()
    if entity is None:
        raise NotFoundError("Invalid {} id for attendance".format(table))
    return entity
