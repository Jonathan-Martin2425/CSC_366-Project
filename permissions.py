from connector import make_connection

PERMISSION_LEVELS = {
    "God Level": 5,
    "College Update Level": 4,
    "Department Update Level": 3,
    "College View Level": 2,
    "Department View Level": 1
}


def validatePermission(requiredLevel, userId, affiliation):

    try:

        DB = make_connection("settings.config")
        cursor = DB.cursor()

        query = """
        SELECT USERS.URole, STAFFandFACULTY.DeptID, DEPARTMENTS.College
        FROM USERS
        JOIN STAFFandFACULTY
            ON USERS.Email = STAFFandFACULTY.Email
        JOIN DEPARTMENTS
            ON STAFFandFACULTY.DeptID = DEPARTMENTS.DId
        WHERE USERS.Email = %s
        """

        cursor.execute(query, (userId,))
        result = cursor.fetchone()

        DB.close()

        if result is None:
            return False

        userRole, userDept, userCollege = result

        # Check permission level
        if PERMISSION_LEVELS[userRole] < PERMISSION_LEVELS[requiredLevel]:
            return False

        # If no affiliation check needed
        if not affiliation:
            return True

        # College check
        if "college" in affiliation:
            if affiliation["college"] != userCollege:
                return False

        # Department check
        if "department" in affiliation:

            allowed = affiliation["department"]

            if isinstance(allowed, str):
                allowed = [allowed]

            if userDept not in allowed:
                return False

        return True

    except Exception:
        return False