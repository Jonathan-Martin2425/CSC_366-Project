from connector import make_connection

PERMISSION_LEVELS = {
    "God": 5,
    "College Update": 4,
    "Department Update": 3,
    "College View": 2,
    "Department View": 1
}


def check_permission(requiredLevel, userId, affiliation: dict = None):
    try:
        DB = make_connection("settings.config")
        cursor = DB.cursor()

        query = """
        SELECT UPermissionLevel, DeptID, CollegeID
        FROM USERS
        WHERE Email = %s
        """

        cursor.execute(query, (userId,))
        result = cursor.fetchone()
        DB.close()

        if result is None:
            return False

        userPermissionLevel, userDept, userCollege = result

        if userPermissionLevel not in PERMISSION_LEVELS:
            return False

        userLevel = PERMISSION_LEVELS[userPermissionLevel]
        requiredLevelVal = PERMISSION_LEVELS[requiredLevel]

        # Admin override
        if userPermissionLevel == "God":
            return True

        if userLevel < requiredLevelVal:
            return False

        if userLevel > requiredLevelVal:
            return True

        if not affiliation:
            return True

        # Department check
        if "department" in affiliation:
            allowed = affiliation["department"]

            # if allowed is a string, make it a list instead for check
            if isinstance(allowed, str):
                allowed = [allowed]

            # check is the DeptID of the user is in one of the permitted departments for the check
            if userDept not in allowed:
                return False

        # College check
        if "college" in affiliation:
            if userCollege != affiliation["college"]:
                return False

        return True

    except Exception as e:
        print("Permission check error:", e)
        return False
