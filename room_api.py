from connector import make_connection
from permissions import check_permission


def getRooms(buildingNumber, floorNumber):
    DB = make_connection("settings.config")
    cursor = DB.cursor()

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
    """

    cursor.execute(query, (buildingNumber, floorNumber))
    results = cursor.fetchall()

    rooms = []

    for bnum, rnum, box, dept_name in results:
        rooms.append({
            "BuildingNumber": bnum,
            "RoomNumber": rnum,
            "BoundingBox": box,
            "Department": dept_name
        })

    cursor.close()
    DB.close()

    return rooms


def findRoom(buildingNumber, floorNumber, x, y):
    DB = make_connection("settings.config")
    cursor = DB.cursor()

    query = """
        SELECT
            BNumber,
            RNumber
        FROM ROOMS
        WHERE BNumber = %s
        AND FNumber = %s
        AND ST_Contains(BoxCoordinates, ST_PointFromText(%s))
        ORDER BY ST_Area(BoxCoordinates) ASC
        LIMIT 1
    """

    point = f"POINT({x} {y})"

    cursor.execute(query, (buildingNumber, floorNumber, point))

    result = cursor.fetchone()

    cursor.close()
    DB.close()

    if result is None:
        return None

    bnum, rnum = result

    return {
        "BuildingNumber": bnum,
        "RoomNumber": rnum
    }


def getRoomInfo(buildingNumber, roomNumber):
    DB = make_connection("settings.config")
    cursor = DB.cursor(dictionary=True)

    room_query = """
        SELECT
            BNumber,
            RNumber,
            SqFt,
            ST_AsText(BoxCoordinates) AS BoundingBox,
            HasBackup,
            FNumber,
            RoomType,
            RoomSpace
        FROM ROOMS
        WHERE BNumber = %s AND RNumber = %s
    """

    cursor.execute(room_query, (buildingNumber, roomNumber))
    room = cursor.fetchone()

    if room is None:
        cursor.close()
        DB.close()
        return None

    dept_query = """
        SELECT DEPARTMENTS.DName
        FROM DEPTOCCUPANT
        JOIN DEPARTMENTS
        ON DEPTOCCUPANT.DeptID = DEPARTMENTS.DId
        WHERE DEPTOCCUPANT.BNumber = %s
        AND DEPTOCCUPANT.RNumber = %s
    """

    cursor.execute(dept_query, (buildingNumber, roomNumber))
    dept = cursor.fetchone()

    department_name = dept["DName"] if dept else None

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
    """

    cursor.execute(people_query, (buildingNumber, roomNumber))
    people_results = cursor.fetchall()

    people = []

    for person in people_results:
        people.append({
            "FullName": f"{person['FirstName']} {person['LastName']}",
            "Email": person["Email"],
            "Title": person["Title"]
        })

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
        GROUP BY EQUIPMENT.TypeId
    """

    cursor.execute(equipment_query, (buildingNumber, roomNumber))
    equip_results = cursor.fetchall()

    equipment = []

    for equip in equip_results:
        equipment.append({
            "Name": equip["EquipName"],
            "Sensitive": bool(equip["isSensitive"]),
            "Count": equip["Quantity"]
        })

    cursor.close()
    DB.close()

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
    room = findRoom("033", "1", 100, 200)
    print(room)

    print("\nTesting getRoomInfo()")
    info = getRoomInfo("033", "0 0378-00")
    import json
    print(json.dumps(info, indent=4))