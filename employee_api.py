from connector import make_connection
from permissions import check_permission


def getEmployees(collegeName, departmentName):
    if not check_permission("getEmployees"):
        raise PermissionError("Permission denied")

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    query = """
        SELECT
            SF.FirstName,
            SF.LastName,
            SF.Title,
            SF.Email,
            RO.BNumber,
            RO.RNumber,
            RM.SqFt,
            occ.OccupantCount
        FROM DEPARTMENTS D
        JOIN STAFFandFACULTY SF
            ON SF.DeptID = D.DId
        LEFT JOIN ROOMOCCUPANTS RO
            ON SF.Email = RO.Email
        LEFT JOIN ROOMS RM
            ON RO.BNumber = RM.BNumber
            AND RO.RNumber = RM.RNumber
        LEFT JOIN (
            SELECT BNumber, RNumber, COUNT(*) AS OccupantCount
            FROM ROOMOCCUPANTS
            GROUP BY BNumber, RNumber
        ) occ
            ON RO.BNumber = occ.BNumber
            AND RO.RNumber = occ.RNumber
        WHERE D.DName = %s
        AND D.College = %s
        ORDER BY SF.LastName, SF.FirstName
    """

    cursor.execute(query, (departmentName, collegeName))
    results = cursor.fetchall()

    employees = {}

    for fname, lname, title, email, bnum, rnum, sqft, occ_count in results:

        if email not in employees:
            employees[email] = {
                "FullName": f"{fname} {lname}",
                "Title": title,
                "Email": email,
                "Rooms": [],
                "TotalSpace": 0
            }

        if bnum and rnum:
            employees[email]["Rooms"].append({
                "BuildingNumber": bnum,
                "RoomNumber": rnum
            })

            if sqft and occ_count:
                if occ_count == 1:
                    employees[email]["TotalSpace"] += float(sqft)
                else:
                    employees[email]["TotalSpace"] += float(sqft) / occ_count

    cursor.close()
    DB.close()

    return list(employees.values())


def getEmployeeInfo(employeeIdentifier):
    if not check_permission("getEmployeeInfo"):
        raise PermissionError("Permission denied")

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    if "Email" in employeeIdentifier:
        filter_clause = "SF.Email = %s"
        params = (employeeIdentifier["Email"],)

    elif "Name" in employeeIdentifier and "Department" in employeeIdentifier:
        filter_clause = "CONCAT(SF.FirstName, ' ', SF.LastName) = %s AND D.DName = %s"
        params = (employeeIdentifier["Name"], employeeIdentifier["Department"])

    else:
        raise ValueError("Provide either Email or Name + Department")

    query = f"""
        SELECT
            SF.FirstName,
            SF.LastName,
            SF.Title,
            SF.Email,
            D.DName,
            RO.BNumber,
            RO.RNumber,
            RT.TypeName,
            RM.SqFt,
            occ.OccupantCount
        FROM STAFFandFACULTY SF
        JOIN DEPARTMENTS D
            ON SF.DeptID = D.DId
        LEFT JOIN ROOMOCCUPANTS RO
            ON SF.Email = RO.Email
        LEFT JOIN ROOMS RM
            ON RO.BNumber = RM.BNumber
            AND RO.RNumber = RM.RNumber
        LEFT JOIN ROOMTYPE RT
            ON RM.RoomType = RT.TypeId
        LEFT JOIN (
            SELECT BNumber, RNumber, COUNT(*) AS OccupantCount
            FROM ROOMOCCUPANTS
            GROUP BY BNumber, RNumber
        ) occ
            ON RO.BNumber = occ.BNumber
            AND RO.RNumber = occ.RNumber
        WHERE {filter_clause}
    """

    cursor.execute(query, params)
    results = cursor.fetchall()

    employee = None

    for fname, lname, title, email, dept, bnum, rnum, rtype, sqft, occ_count in results:

        if employee is None:
            employee = {
                "FullName": f"{fname} {lname}",
                "Department": dept,
                "Title": title,
                "Email": email,
                "TotalSpace": 0,
                "Rooms": []
            }

        if bnum and rnum:
            if sqft and occ_count:
                if occ_count == 1:
                    assigned_space = float(sqft)
                else:
                    assigned_space = float(sqft) / occ_count
            else:
                assigned_space = 0

            employee["Rooms"].append({
                "BuildingNumber": bnum,
                "RoomNumber": rnum,
                "RoomType": rtype,
                "RoomSquareFootage": sqft,
                "AssignedSquareFootage": assigned_space
            })

            employee["TotalSpace"] += assigned_space

    cursor.close()
    DB.close()

    return employee


if __name__ == "__main__":
    print("Testing getEmployees()")
    employees = getEmployees("BCSM", "Statistics")
    for emp in employees:
        print(emp)

    print("\nTesting getEmployeeInfo()")
    employee = getEmployeeInfo({
        "Email": "wcrow@calpoly.edu"
    })
    print(employee)