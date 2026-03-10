from connector import make_connection
from permissions import check_permission

def getFloorplans():
    if not check_permission("getFloorplans"):
        raise PermissionError("Permission denied")

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    query = """
        SELECT
            FLOORPLANS.FImagePath,
            BUILDINGS.BName,
            BUILDINGS.BNumber,
            FLOORPLANS.FNumber
        FROM FLOORPLANS
        JOIN BUILDINGS
        ON FLOORPLANS.BNumber = BUILDINGS.BNumber
    """

    cursor.execute(query)
    results = cursor.fetchall()

    floorplans = []

    for uri, building_name, building_number, floor_number in results:
        floorplans.append({
            "URI": uri,
            "BuildingName": building_name,
            "BuildingNumber": building_number,
            "FloorNumber": floor_number
        })

    cursor.close()
    DB.close()

    return floorplans

if __name__ == "__main__":
    plans = getFloorplans()

    for plan in plans:
        print(plan)