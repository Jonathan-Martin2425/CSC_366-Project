from connector import make_connection
from permissions import check_permission
from errors_api import *
import json

def getDeptList(email, college):
    if not check_permission("Department View", email):
        return {"error": "Access denied."}

    DB = make_connection("settings.config")
    cursor = DB.cursor(dictionary=True, buffered=True)

    dept_query = """
        SELECT
            DEPARTMENTS.DId,
            DEPARTMENTS.DName
        FROM COLLEGES
        JOIN DEPARTMENTS
            ON COLLEGES.Abbreviation = DEPARTMENTS.College
        WHERE COLLEGES.CName = %s
        OR COLLEGES.Abbreviation = %s
    """

    cursor.execute(dept_query, (college, college))
    departments = cursor.fetchall()

    result = []
    for dept in departments:
        dept_id = dept["DId"]

        office_query = """
            SELECT
                DEPTOCCUPANT.BNumber,
                DEPTOCCUPANT.RNumber,
                ROOMTYPE.TypeName
            FROM DEPTOCCUPANT
            JOIN ROOMS
                ON DEPTOCCUPANT.BNumber = ROOMS.BNumber
                AND DEPTOCCUPANT.RNumber = ROOMS.RNumber
            JOIN ROOMTYPE
                ON ROOMS.RoomType = ROOMTYPE.TypeId
            WHERE DEPTOCCUPANT.DeptID = %s
            AND ROOMTYPE.TypeId = 312
        """

        cursor.execute(office_query, (dept_id,))
        office = cursor.fetchone()

        head_query = """
            SELECT
                STAFFandFACULTY.FirstName,
                STAFFandFACULTY.LastName
            FROM ROOMOCCUPANTS
            JOIN STAFFandFACULTY
                ON ROOMOCCUPANTS.Email = STAFFandFACULTY.Email
            WHERE ROOMOCCUPANTS.BNumber = %s
            AND ROOMOCCUPANTS.RNumber = %s
        """

        cursor.execute(head_query, (
            office["BNumber"] if office else None,
            office["RNumber"] if office else None
        ))
        head = cursor.fetchone()

        result.append({
            "DepartmentName": dept["DName"],
            "MainOffice": {
                "BuildingNumber": office["BNumber"],
                "RoomNumber": office["RNumber"]
            } if office else None,
            "DepartmentHead": f"{head['FirstName']} {head['LastName']}" if head else None,
            "DepartmentType": "Academic" if office and office["TypeName"] else "Non-Academic"
        })

    cursor.close()
    DB.close()
    return result


def getDeptListEnhanced(email, college):
    if not check_permission("Department View", email):
        return {"error": "Access denied."}

    DB = make_connection("settings.config")
    cursor = DB.cursor(dictionary=True, buffered=True)

    dept_query = """
        SELECT
            DEPARTMENTS.DId,
            DEPARTMENTS.DName
        FROM COLLEGES
        JOIN DEPARTMENTS
            ON COLLEGES.Abbreviation = DEPARTMENTS.College
        WHERE COLLEGES.CName = %s
        OR COLLEGES.Abbreviation = %s
    """

    cursor.execute(dept_query, (college, college))
    departments = cursor.fetchall()

    result = []
    for dept in departments:
        dept_id = dept["DId"]

        office_query = """
            SELECT
                DEPTOCCUPANT.BNumber,
                DEPTOCCUPANT.RNumber,
                ROOMTYPE.TypeName
            FROM DEPTOCCUPANT
            JOIN ROOMS
                ON DEPTOCCUPANT.BNumber = ROOMS.BNumber
                AND DEPTOCCUPANT.RNumber = ROOMS.RNumber
            JOIN ROOMTYPE
                ON ROOMS.RoomType = ROOMTYPE.TypeId
            WHERE DEPTOCCUPANT.DeptID = %s
            AND ROOMTYPE.TypeId = 312
        """

        cursor.execute(office_query, (dept_id,))
        office = cursor.fetchone()

        head_query = """
            SELECT
                STAFFandFACULTY.FirstName,
                STAFFandFACULTY.LastName
            FROM ROOMOCCUPANTS
            JOIN STAFFandFACULTY
                ON ROOMOCCUPANTS.Email = STAFFandFACULTY.Email
            WHERE ROOMOCCUPANTS.BNumber = %s
            AND ROOMOCCUPANTS.RNumber = %s
        """

        cursor.execute(head_query, (
            office["BNumber"] if office else None,
            office["RNumber"] if office else None
        ))
        head = cursor.fetchone()

        assigned_query = """
            SELECT
                COUNT(*) AS RoomCount,
                SUM(ROOMS.SqFt) AS TotalSqFt
            FROM DEPTOCCUPANT
            JOIN ROOMS
                ON DEPTOCCUPANT.BNumber = ROOMS.BNumber
                AND DEPTOCCUPANT.RNumber = ROOMS.RNumber
            WHERE DEPTOCCUPANT.DeptID = %s
        """

        cursor.execute(assigned_query, (dept_id,))
        assigned = cursor.fetchone()

        faculty_query = """
            SELECT Email
            FROM STAFFandFACULTY
            WHERE DeptID = %s
        """

        cursor.execute(faculty_query, (dept_id,))
        faculty = cursor.fetchall()
        faculty_emails = [f["Email"] for f in faculty]

        if faculty_emails:
            format_strings = ",".join(["%s"] * len(faculty_emails))
            employee_rooms_query = f"""
                SELECT
                    COUNT(DISTINCT ROOMS.BNumber, ROOMS.RNumber) AS RoomCount,
                    SUM(DISTINCT ROOMS.SqFt) AS TotalSqFt
                FROM ROOMOCCUPANTS
                JOIN ROOMS
                    ON ROOMOCCUPANTS.BNumber = ROOMS.BNumber
                    AND ROOMOCCUPANTS.RNumber = ROOMS.RNumber
                WHERE ROOMOCCUPANTS.Email IN ({format_strings})
            """
            cursor.execute(employee_rooms_query, faculty_emails)
            employee_rooms = cursor.fetchone()
        else:
            employee_rooms = {"RoomCount": 0, "TotalSqFt": 0}

        result.append({
            "DepartmentName": dept["DName"],
            "MainOffice": {
                "BuildingNumber": office["BNumber"],
                "RoomNumber": office["RNumber"]
            } if office else None,
            "DepartmentHead": f"{head['FirstName']} {head['LastName']}" if head else None,
            "DepartmentType": "Academic" if office and office["TypeName"] else "Non-Academic",
            "AssignedRooms": {
                "RoomCount": assigned["RoomCount"] if assigned else 0,
                "TotalSqFt": assigned["TotalSqFt"] if assigned else 0
            },
            "EmployeeRooms": {
                "RoomCount": employee_rooms["RoomCount"] if employee_rooms else 0,
                "TotalSqFt": employee_rooms["TotalSqFt"] if employee_rooms else 0
            }
        })

    cursor.close()
    DB.close()
    return result


if __name__ == "__main__":
    print("Testing getDeptList()")
    depts = getDeptList("jperrine@calpoly.edu", "BCSM")
    print(json.dumps(depts, indent=4))

    print("\nTesting getDeptListEnhanced()")
    depts = getDeptListEnhanced("jperrine@calpoly.edu", "BCSM")
    print(json.dumps(depts, indent=4))