from connector import make_connection
from permissions import check_permission
import json


def getEquipmentLocations(email, equipmentType):
    if not check_permission("Department View", email):
        return {"error": "Access denied."}

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    query = """
        SELECT
            ER.BNumber,
            ER.RNumber,
            COUNT(*) AS EquipmentCount
        FROM EQUIPMENT E
        JOIN EQUIPtoROOM ER
            ON E.TypeId = ER.EquipType
        WHERE E.EquipName = %s
        GROUP BY ER.BNumber, ER.RNumber
        ORDER BY ER.BNumber, ER.RNumber
    """

    cursor.execute(query, (equipmentType,))
    results = cursor.fetchall()

    rooms = []

    for bnum, rnum, count in results:
        rooms.append({
            "BuildingNumber": bnum,
            "RoomNumber": rnum,
            "EquipmentCount": count
        })

    cursor.close()
    DB.close()

    return rooms


def getSensitiveEquipmentLocations(email, college):
    if not check_permission("Department View", email):
        return {"error": "Access denied."}

    DB = make_connection("settings.config")
    cursor = DB.cursor(dictionary=True, buffered=True)

    query = """
        SELECT
            ER.BNumber,
            ER.RNumber,
            E.EquipName,
            COUNT(*) AS EquipCount
        FROM COLLEGES C
        JOIN DEPARTMENTS D
            ON C.Abbreviation = D.College
        JOIN DEPTOCCUPANT DO
            ON D.DId = DO.DeptID
        JOIN EQUIPtoROOM ER
            ON DO.BNumber = ER.BNumber
            AND DO.RNumber = ER.RNumber
        JOIN EQUIPMENT E
            ON ER.EquipType = E.TypeId
        WHERE (C.CName = %s OR C.Abbreviation = %s)
        AND E.isSensitive = 1
        GROUP BY ER.BNumber, ER.RNumber, E.EquipName
        ORDER BY ER.BNumber, ER.RNumber
    """

    cursor.execute(query, (college, college))
    results = cursor.fetchall()

    rooms = {}
    for row in results:
        key = (row["BNumber"], row["RNumber"])

        if key not in rooms:
            rooms[key] = {
                "BuildingNumber": row["BNumber"],
                "RoomNumber": row["RNumber"],
                "SensitiveEquipment": []
            }

        rooms[key]["SensitiveEquipment"].append({
            "EquipmentType": row["EquipName"],
            "Count": row["EquipCount"]
        })

    cursor.close()
    DB.close()
    return list(rooms.values())

if __name__ == "__main__":
    print("Testing getEquipmentLocations()")
    Rooms = getEquipmentLocations("jperrine@calpoly.edu", "ULT Freezer")
    print(json.dumps(Rooms, indent=4))


    print("\nTesting getSensitiveEquipmentLocations()")
    rooms = getSensitiveEquipmentLocations("jperrine@calpoly.edu", "BCSM")
    print(json.dumps(rooms, indent=4))
