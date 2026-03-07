from connector import make_connection

def reset_database(DB, cursor):

    # runs cleanup script
    with open("DB-cleanup.sql", "r") as file:
        sql_script = file.read()
    statements = [
        stmt.strip()
        for stmt in sql_script.split(";")
        if stmt.strip()
    ]
    for statement in statements:
        cursor.execute(statement)
    DB.commit()

    # runs setup script
    with open("DB-setup.sql", "r") as file:
        sql_script = file.read()
    statements = [
        stmt.strip()
        for stmt in sql_script.split(";")
        if stmt.strip()
    ]
    for statement in statements:
        cursor.execute(statement)
    DB.commit()

    # start adding to each table

    cursor.execute("")





