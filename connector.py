import mysql.connector
import json


# tries to connect to the host using data found in
# the given file that has everything needed
# to connect to the DB as a JSON object file
# returns a DB/SQL connection object
def make_connection(file):
    with open(file, "r") as settings:
        d = json.load(settings)
        # get data from given file, then connect to DB
        return mysql.connector.connect(
            host=d["host"],
            user=d["user"],
            password=d["password"],
            port=d["port"],
            database=d["database"],
        )


if __name__ == "__main__":
    DB = make_connection("settings.config")
    cursor = DB.cursor()

    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()

    for table in tables:
        print(table)
