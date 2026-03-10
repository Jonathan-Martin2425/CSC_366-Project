from connector import make_connection
from permissions import check_permission


def getEquipmentLocations(equipmentType):
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


def getSensitiveEquipmentLocations(collegeAbbrev):
    DB = make_connection("settings.config")
    cursor = DB.cursor()

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
        WHERE C.Abbreviation = %s
        AND E.isSensitive = 1
        GROUP BY ER.BNumber, ER.RNumber, E.EquipName
        ORDER BY ER.BNumber, ER.RNumber
    """

    cursor.execute(query, (collegeAbbrev,))
    results = cursor.fetchall()

    rooms = {}

    for bnum, rnum, equip_name, count in results:

        key = (bnum, rnum)

        if key not in rooms:
            rooms[key] = {
                "BuildingNumber": bnum,
                "RoomNumber": rnum,
                "SensitiveEquipment": []
            }

        rooms[key]["SensitiveEquipment"].append({
            "EquipmentType": equip_name,
            "Count": count
        })

    cursor.close()
    DB.close()

    return list(rooms.values())

if __name__ == "__main__":
    print("Testing getEquipmentLocations()")
    Rooms = getEquipmentLocations("Bed")
    for room in Rooms:
        print(room)

    print("Testing getSensitiveEquipmentLocations()")
    rooms = getSensitiveEquipmentLocations("BCSM")
    for room in rooms:
        print(room)