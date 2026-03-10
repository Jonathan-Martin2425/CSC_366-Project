from connector import make_connection
from permissions import check_permission


def getEquipmentLocations(equipmentType):
    if not check_permission("getEquipmentLocations"):
        raise PermissionError("Permission denied")

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


if __name__ == "__main__":
    print("Testing getEquipmentLocations()")
    Rooms = getEquipmentLocations("Bed")
    for room in Rooms:
        print(room)