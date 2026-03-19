from connector import make_connection
from permissions import check_permission
import json

def getRooms(email, buildingNumber, floorNumber):
    if not check_permission("View", email):
        return {"error": "Access denied."}

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
        ORDER BY ROOMS.RNumber
    """

    cursor.execute(query, (buildingNumber, floorNumber))
    results = cursor.fetchall()

    cursor.close()
    DB.close()

    if results is None:
        return None

    return [
        {
            "BuildingNumber": bnum,
            "RoomNumber": rnum,
            "BoundingBox": box,
            "Department": dept_name
        }
        for bnum, rnum, box, dept_name in results
    ]


def findRoom(email, buildingNumber, floorNumber, x, y):
    if not check_permission("View", email):
        return {"error": "Access denied."}

    DB = make_connection("settings.config")
    cursor = DB.cursor()

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


from decimal import Decimal

def getRoomInfo(email, buildingNumber, roomNumber):
    if not check_permission("View", email):
        return {"error": "Access denied."}

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
            FBNumber,
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
        ORDER BY STAFFandFACULTY.LastName, STAFFandFACULTY.FirstName
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

    # ✅ FIXED: use Quantity instead of COUNT(*)
    equipment_query = """
        SELECT
            EQUIPMENT.EquipName,
            EQUIPMENT.isSensitive,
            EQUIPtoROOM.Quantity
        FROM EQUIPtoROOM
        JOIN EQUIPMENT
        ON EQUIPtoROOM.EquipType = EQUIPMENT.TypeId
        WHERE EQUIPtoROOM.BNumber = %s
        AND EQUIPtoROOM.RNumber = %s
        ORDER BY EQUIPMENT.EquipName
    """

    cursor.execute(equipment_query, (buildingNumber, roomNumber))
    equip_results = cursor.fetchall()

    equipment = []
    for equip in equip_results:
        equipment.append({
            "Name": equip["EquipName"],
            "Sensitive": bool(equip["isSensitive"]),
            # ✅ FIX: convert Decimal → int
            "Count": int(equip["Quantity"]) if equip["Quantity"] is not None else 0
        })

    cursor.close()
    DB.close()

    return {
        "RoomID": {
            "BuildingNumber": buildingNumber,
            "RoomNumber": roomNumber
        },
        "RoomAttributes": {
            # ✅ FIX: convert Decimal → float
            "SqFt": float(room["SqFt"]) if room["SqFt"] is not None else None,
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
    rooms = getRooms("jperrine@calpoly.edu", "033", "1")
    print(json.dumps(rooms, indent=4))

    print("\nTesting findRoom()")
    room = findRoom("jperrine@calpoly.edu", "033", "1", 301, 899)
    print(json.dumps(room, indent=4))

    print("\nTesting getRoomInfo()")
    info = getRoomInfo("jperrine@calpoly.edu", "033", "0387-00")
    print(json.dumps(info, indent=4))