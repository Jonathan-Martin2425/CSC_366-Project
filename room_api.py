from connector import make_connection

def getRooms(buildingNumber, floorNumber):
    # Connect to the database using the credentials
    DB = make_connection("settings.config")
    cursor = DB.cursor()

    # The SQL query that'll be executed
    query = """
        SELECT
            ROOMS.BNumber,
            ROOMS.RNumber,
            ST_AsText(ROOMS.BoxCoordinates),
            DEPARTMENTS.DName
        FROM ROOMS
        LEFT JOIN DEPTOCCUPANT
            ON ROOMS.BNumber = DEPTOCCUPANT.BNumber
            AND ROOMS.RNumber = DEPTOCCUPANT.RNumber
        LEFT JOIN DEPARTMENTS
            ON DEPTOCCUPANT.DeptID = DEPARTMENTS.DId
        WHERE ROOMS.BNumber = %s
        AND ROOMS.FNumber = %s
        ORDER BY ROOMS.RNumber
    """

    # Execute the SQL query on the database
    cursor.execute(query, (buildingNumber, floorNumber))
    results = cursor.fetchall()

    # Close the database connection
    cursor.close()
    DB.close()

    # Return None if no such rooms are found
    if results is None:
        return None

    # Format the results to be readable and return them
    return [
        {
            "BuildingNumber": bnum,
            "RoomNumber": rnum,
            "BoundingBox": box,
            "Department": dept_name
        }
        for bnum, rnum, box, dept_name in results
    ]


def findRoom(buildingNumber, floorNumber, x, y):
    # Connect to the database using the credentials
    DB = make_connection("settings.config")
    cursor = DB.cursor()

    # The SQL query that'll be executed
    query = """
        SELECT
            BNumber,
            RNumber
        FROM ROOMS
        WHERE BNumber = %s
        AND FNumber = %s
        AND MBRContains(BoxCoordinates, ST_GeomFromText(%s))
        ORDER BY ST_Area(BoxCoordinates) ASC
        LIMIT 1
    """

    # Execute the SQL query on the database
    point = f"POINT({x} {y})"
    cursor.execute(query, (buildingNumber, floorNumber, point))
    result = cursor.fetchone()

    # Close the database connection
    cursor.close()
    DB.close()

    # Return none if no such room is found
    if result is None:
        return None

    # Format the results to be readable and return them
    bnum, rnum = result
    return {
        "BuildingNumber": bnum,
        "RoomNumber": rnum
    }


def getRoomInfo(buildingNumber, roomNumber):
    # Connect to the database using the credentials
    DB = make_connection("settings.config")
    cursor = DB.cursor(dictionary=True)

    # The Room SQL query that'll be executed
    room_query = """
        SELECT
            BNumber,
            RNumber,
            SqFt,
            ST_AsText(BoxCoordinates) AS BoundingBox,
            HasBackup,
            FNumber,
            FBNumber,
            RoomType,
            RoomSpace
        FROM ROOMS
        WHERE BNumber = %s AND RNumber = %s
    """

    # Execute the SQL query on the database
    cursor.execute(room_query, (buildingNumber, roomNumber))
    room = cursor.fetchone()

    # Return None if no such rooms are found
    if room is None:
        cursor.close()
        DB.close()
        return None

    # The Department SQL query that'll be executed
    dept_query = """
        SELECT DEPARTMENTS.DName
        FROM DEPTOCCUPANT
        JOIN DEPARTMENTS
        ON DEPTOCCUPANT.DeptID = DEPARTMENTS.DId
        WHERE DEPTOCCUPANT.BNumber = %s
        AND DEPTOCCUPANT.RNumber = %s
    """

    # Execute the SQL query on the database
    cursor.execute(dept_query, (buildingNumber, roomNumber))
    dept = cursor.fetchone()

    # Return None if there's no department relationship
    department_name = dept["DName"] if dept else None

    # The Staff/Faculty SQL query that'll be executed
    people_query = """
        SELECT
            STAFFandFACULTY.FirstName,
            STAFFandFACULTY.LastName,
            STAFFandFACULTY.Email,
            STAFFandFACULTY.Title
        FROM ROOMOCCUPANTS
        JOIN STAFFandFACULTY
        ON ROOMOCCUPANTS.Email = STAFFandFACULTY.Email
        WHERE ROOMOCCUPANTS.BNumber = %s
        AND ROOMOCCUPANTS.RNumber = %s
        ORDER BY STAFFandFACULTY.LastName, STAFFandFACULTY.FirstName
    """

    # Execute the SQL query on the database
    cursor.execute(people_query, (buildingNumber, roomNumber))
    people_results = cursor.fetchall()

    # Format the Staff/Faculty results to be readable
    people = []
    for person in people_results:
        people.append({
            "FullName": f"{person['FirstName']} {person['LastName']}",
            "Email": person["Email"],
            "Title": person["Title"]
        })

    # The Equipment SQL query that'll be executed
    equipment_query = """
        SELECT
            EQUIPMENT.EquipName,
            EQUIPMENT.isSensitive,
            COUNT(*) AS Quantity
        FROM EQUIPtoROOM
        JOIN EQUIPMENT
        ON EQUIPtoROOM.EquipType = EQUIPMENT.TypeId
        WHERE EQUIPtoROOM.BNumber = %s
        AND EQUIPtoROOM.RNumber = %s
        GROUP BY EQUIPMENT.TypeId, EQUIPMENT.EquipName, EQUIPMENT.isSensitive
        ORDER BY EQUIPMENT.EquipName
    """

    # Execute the SQL query on the database
    cursor.execute(equipment_query, (buildingNumber, roomNumber))
    equip_results = cursor.fetchall()

    # Format the Equipment results to be readable
    equipment = []
    for equip in equip_results:
        equipment.append({
            "Name": equip["EquipName"],
            "Sensitive": bool(equip["isSensitive"]),
            "Count": equip["Quantity"]
        })

    # Close the database connection
    cursor.close()
    DB.close()

    # Format the results to be readable and return them
    return {
        "RoomID": {
            "BuildingNumber": buildingNumber,
            "RoomNumber": roomNumber
        },
        "RoomAttributes": {
            "SqFt": room["SqFt"],
            "BoundingBox": room["BoundingBox"],
            "HasBackup": room["HasBackup"],
            "FloorNumber": room["FNumber"],
            "FBNumber": room["FBNumber"],
            "RoomType": room["RoomType"],
            "RoomSpace": room["RoomSpace"]
        },
        "Department": department_name,
        "People": people,
        "Equipment": equipment
    }


if __name__ == "__main__":
    print("Testing getRooms()")
    rooms = getRooms("033", "1")
    for room in rooms:
        print(room)

    print("\nTesting findRoom()")
    room = findRoom("033", "1", 301, 899)
    print(room)

    print("\nTesting getRoomInfo()")
    info = getRoomInfo("033", "0387-00")
    import json
    print(json.dumps(info, indent=4))