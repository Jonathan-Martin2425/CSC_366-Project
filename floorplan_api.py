from connector import make_connection
from permissions import check_permission

def getFloorplans():
    # Connect to the database using the credentials
    DB = make_connection("settings.config")
    cursor = DB.cursor()

    # The SQL query that'll be executed
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

    # Execute the SQL query on the database
    cursor.execute(query)
    results = cursor.fetchall()

    # Close the database connection
    cursor.close()
    DB.close()

    # Format the results to be readable and return them
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
    plans = getFloorplans()
    for plan in plans:
        print(plan)