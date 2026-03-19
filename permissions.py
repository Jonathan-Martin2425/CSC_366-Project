from connector import make_connection

PERMISSION_LEVELS = {
    "God": 5,
    "College Update": 4,
    "Department Update": 3,
    "College View": 2,
    "Department View": 1
}


def check_permission(action_type, userId, affiliation: dict = None):

    try:
        DB = make_connection("settings.config")
        cursor = DB.cursor()

        cursor.execute("""
        SELECT UPermissionLevel, DeptID, CollegeID
        FROM USERS
        WHERE Email = %s
        """, (userId,))

        result = cursor.fetchone()
        DB.close()

        if result is None:
            return False

        userPermissionLevel, userDept, userCollege = result

        if userPermissionLevel not in PERMISSION_LEVELS:
            return False

        # Admin override
        if userPermissionLevel == "God":
            return True

        userLevel = PERMISSION_LEVELS[userPermissionLevel]

        if action_type == "Update":
            if userLevel < 3:
                return False
        elif action_type == "View":
            if userLevel < 1:
                return False
        else:
            return False

        # No affiliation needed
        if not affiliation:
            return True

        # College check
        if "college" in affiliation:
            if userCollege != affiliation["college"]:
                return False

        # Department check
        if "department" in affiliation:
            if userLevel >= 4:
                return True
            allowed = affiliation["department"]
            if isinstance(allowed, str):
                allowed = [allowed]

            if userDept not in allowed:
                return False

        return True

    except Exception as e:
        print("Permission check error:", e)
        return False