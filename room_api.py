from connector import make_connection
from permissions import check_permission

def getRooms(buildingNumber, floorNumber):
    if not check_permission("getRooms"):
        raise PermissionError("Permission denied")

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
if __name__ == "__main__":
    Rooms = getRooms("033", "1")

    for room in Rooms:
        print(room)