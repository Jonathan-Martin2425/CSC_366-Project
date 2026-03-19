from connector import make_connection
from permissions import check_permission
import json

def getFloorplans():
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

    cursor.close()
    DB.close()

    return [
        {
            "URI": uri,
            "BuildingName": building_name,
            "BuildingNumber": building_number,
            "FloorNumber": floor_number
        }
        for uri, building_name, building_number, floor_number in results
    ]

if __name__ == "__main__":
    print("Testing getFloorplans()")
    plans = getFloorplans()
    print(json.dumps(plans, indent=4))