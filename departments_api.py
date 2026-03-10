from connector import make_connection
from permissions import check_permission


def getDeptListEnhanced(collegeAbbrev):
    if not check_permission("getDeptListEnhanced"):
        raise PermissionError("Permission denied")

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    dept_query = """
        SELECT DId, DName
        FROM DEPARTMENTS
        WHERE College = %s
        ORDER BY DName
    """

    cursor.execute(dept_query, (collegeAbbrev,))
    departments = cursor.fetchall()

    results = []

    for dept_id, dept_name in departments:

        assigned_query = """
            SELECT COUNT(*), COALESCE(SUM(R.SqFt),0)
            FROM DEPTOCCUPANT DO
            JOIN ROOMS R
                ON DO.BNumber = R.BNumber
                AND DO.RNumber = R.RNumber
            WHERE DO.DeptID = %s
        """

        cursor.execute(assigned_query, (dept_id,))
        assigned_rooms, assigned_sqft = cursor.fetchone()

        rooms_query = """
            SELECT DISTINCT RO.BNumber, RO.RNumber
            FROM STAFFandFACULTY SF
            JOIN ROOMOCCUPANTS RO
                ON SF.Email = RO.Email
            WHERE SF.DeptID = %s
        """

        cursor.execute(rooms_query, (dept_id,))
        emp_rooms = cursor.fetchall()

        room_count = len(emp_rooms)
        emp_sqft = 0

        for bnum, rnum in emp_rooms:

            sqft_query = """
                SELECT SqFt
                FROM ROOMS
                WHERE BNumber = %s AND RNumber = %s
            """
            cursor.execute(sqft_query, (bnum, rnum))
            sqft = cursor.fetchone()[0]

            occ_query = """
                SELECT COUNT(*)
                FROM ROOMOCCUPANTS
                WHERE BNumber = %s AND RNumber = %s
            """
            cursor.execute(occ_query, (bnum, rnum))
            occ_count = cursor.fetchone()[0]

            if occ_count == 1:
                emp_sqft += sqft
            else:
                emp_sqft += sqft / occ_count

        results.append({
            "DepartmentName": dept_name,
            "AssignedRoomCount": assigned_rooms,
            "EmployeeRoomCount": room_count,
            "AssignedSquareFootage": float(assigned_sqft),
            "EmployeeSquareFootage": float(emp_sqft)
        })

    cursor.close()
    DB.close()

    return results


if __name__ == "__main__":
    print("Testing getDeptListEnhanced()")
    depts = getDeptListEnhanced("BCSM")
    for dept in depts:
        print(dept)