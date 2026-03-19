from connector import make_connection
from permissions import check_permission
import json

def getFloorplans(email):
    if not check_permission("Department View", email):
        return {"error": "Access denied."}

    DB = make_connection("settings.config")
    cursor = DB.cursor(dictionary=True, buffered=True)

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
            "URI": row["FImagePath"],
            "BuildingName": row["BName"],
            "BuildingNumber": row["BNumber"],
            "FloorNumber": row["FNumber"]
        }
        for row in results
    ]

if __name__ == "__main__":
    print("Testing getFloorplans()")
    plans = getFloorplans("jperrine@calpoly.edu")
    print(json.dumps(plans, indent=4))