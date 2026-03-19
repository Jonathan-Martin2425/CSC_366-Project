from connector import make_connection
from permissions import check_permission
from errors_api import *
import json

def computeEmployeeRooms(cursor, email):
    rooms_query = """
        SELECT
            ROOMS.BNumber,
            ROOMS.RNumber,
            ROOMS.SqFt,
            ROOMTYPE.TypeName
        FROM ROOMOCCUPANTS
        JOIN ROOMS
            ON ROOMOCCUPANTS.BNumber = ROOMS.BNumber
            AND ROOMOCCUPANTS.RNumber = ROOMS.RNumber
        JOIN ROOMTYPE
            ON ROOMS.RoomType = ROOMTYPE.TypeId
        WHERE ROOMOCCUPANTS.Email = %s
    """

    cursor.execute(rooms_query, (email,))
    rooms = cursor.fetchall()

    total_sqft = 0.0
    room_list = []
    for room in rooms:
        occupant_count_query = """
            SELECT COUNT(*) AS OccupantCount
            FROM ROOMOCCUPANTS
            WHERE BNumber = %s
            AND RNumber = %s
        """

        cursor.execute(occupant_count_query, (room["BNumber"], room["RNumber"]))
        count_result = cursor.fetchone()
        occupant_count = count_result["OccupantCount"]

        sqft_share = float(room["SqFt"]) / occupant_count
        total_sqft += sqft_share

        room_list.append({
            "BuildingNumber": room["BNumber"],
            "RoomNumber": room["RNumber"],
            "RoomType": room["TypeName"],
            "SqFt": float(room["SqFt"]),
            "AssignedSqFt": round(sqft_share, 2)
        })

    return room_list, round(total_sqft, 2)


def getEmployees(college, department):
    DB = make_connection("settings.config")
    cursor = DB.cursor(dictionary=True, buffered=True)

    employee_query = """
        SELECT
            STAFFandFACULTY.Email,
            STAFFandFACULTY.FirstName,
            STAFFandFACULTY.LastName,
            STAFFandFACULTY.Title
        FROM COLLEGES
        JOIN DEPARTMENTS
            ON COLLEGES.Abbreviation = DEPARTMENTS.College
        JOIN STAFFandFACULTY
            ON DEPARTMENTS.DId = STAFFandFACULTY.DeptID
        WHERE (COLLEGES.CName = %s OR COLLEGES.Abbreviation = %s)
        AND DEPARTMENTS.DName = %s
    """

    cursor.execute(employee_query, (college, college, department))
    employees = cursor.fetchall()

    result = []
    for employee in employees:
        room_list, total_sqft = computeEmployeeRooms(cursor, employee["Email"])

        result.append({
            "FullName": f"{employee['FirstName']} {employee['LastName']}",
            "Title": employee["Title"],
            "Email": employee["Email"],
            "Rooms": [{"BuildingNumber": r["BuildingNumber"], "RoomNumber": r["RoomNumber"]} for r in room_list],
            "TotalSqFt": total_sqft
        })

    cursor.close()
    DB.close()
    return result


def getEmployeeInfo(user: str, identifier):
    DB = make_connection("settings.config")
    cursor = DB.cursor(dictionary=True, buffered=True)

    if "Email" in identifier:
        employee_query = """
            SELECT
                STAFFandFACULTY.Email,
                STAFFandFACULTY.FirstName,
                STAFFandFACULTY.LastName,
                STAFFandFACULTY.Title,
                DEPARTMENTS.DName,
                DEPARTMENTS.DId,
                DEPARTMENTS.College
            FROM STAFFandFACULTY
            JOIN DEPARTMENTS
                ON STAFFandFACULTY.DeptID = DEPARTMENTS.DId
            WHERE STAFFandFACULTY.Email = %s
        """

        cursor.execute(employee_query, (identifier["Email"],))

    elif "FirstName" in identifier and "LastName" in identifier and "Department" in identifier:
        employee_query = """
            SELECT
                STAFFandFACULTY.Email,
                STAFFandFACULTY.FirstName,
                STAFFandFACULTY.LastName,
                STAFFandFACULTY.Title,
                DEPARTMENTS.DName,
                DEPARTMENTS.DId,
                DEPARTMENTS.College
            FROM STAFFandFACULTY
            JOIN DEPARTMENTS
                ON STAFFandFACULTY.DeptID = DEPARTMENTS.DId
            WHERE STAFFandFACULTY.FirstName = %s
            AND STAFFandFACULTY.LastName = %s
            AND DEPARTMENTS.DName = %s
        """

        cursor.execute(employee_query, (
            identifier["FirstName"],
            identifier["LastName"],
            identifier["Department"]
        ))

    else:
        cursor.close()
        DB.close()
        return {"error": "Invalid identifier. Provide 'Email' or 'FirstName' + 'LastName' + 'Department'."}

    employee = cursor.fetchone()

    if employee is None:
        cursor.close()
        DB.close()
        return None

    affiliation = {
        "department": [employee["DId"]],
        "college": employee["College"]
    }

    if not check_permission("Department View", user, affiliation):
        cursor.close()
        DB.close()
        return {"error": ERR_PERMISSION}

    room_list, total_sqft = computeEmployeeRooms(cursor, employee["Email"])

    cursor.close()
    DB.close()

    return {
        "FullName": f"{employee['FirstName']} {employee['LastName']}",
        "Department": employee["DName"],
        "Email": employee["Email"],
        "Title": employee["Title"],
        "TotalAssignedSqFt": total_sqft,
        "Rooms": room_list
    }


if __name__ == "__main__":
    print("Testing getEmployees()")
    employees = getEmployees("BCSM", "Statistics")
    print(json.dumps(employees, indent=4))

    print("\nTesting getEmployeeInfo()")
    employee = getEmployeeInfo({"Email": "atheobol@calpoly.edu"})
    print(json.dumps(employee, indent=4))
