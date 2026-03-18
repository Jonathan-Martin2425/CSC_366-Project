from connector import make_connection

PERMISSION_LEVELS = {
    "God Level": 5,
    "College Update Level": 4,
    "Department Update Level": 3,
    "College View Level": 2,
    "Department View Level": 1
}


def check_permission(requiredLevel, userId, affiliation=None):

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
        if userPermissionLevel == "God Level":
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
            if isinstance(allowed, str):
                allowed = [allowed]

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