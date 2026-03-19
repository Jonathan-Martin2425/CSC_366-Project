from connector import make_connection
from errors_api import *
from wal_api import *
from permissions import *
import datetime


# ----------------------------------------
# Get department + college of a room
# ----------------------------------------
def getRoomAffiliation(building, room):

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    cursor.execute("""
    SELECT D.DId, D.College
    FROM DEPTOCCUPANT DO
    JOIN DEPARTMENTS D ON DO.DeptID = D.DId
    WHERE DO.BNumber=%s AND DO.RNumber=%s
    """, (building, room))

    result = cursor.fetchone()
    DB.close()

    if result:
        dept, college = result
        return {
            "department": [dept],
            "college": college
        }

    return None


# ----------------------------------------
def addEmployee(userId, first, last, email, dept, title):

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    affiliation = {"department": [dept]}

    if not check_permission("Department Update", userId, affiliation):
        DB.close()
        return ERR_PERMISSION

    try:

        cursor.execute("""
        INSERT INTO STAFFandFACULTY
        VALUES (%s,%s,%s,%s,%s)
        """, (email, first, last, title, dept))

        DB.commit()

        log_result = logRoomAssignmentPerson(userId, None, None, email, "ADD_EMPLOYEE")

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING
        DB.close()

        return SUCCESS

    except Exception as e:
        print("addEmployee error:", e)
        DB.close()
        return ERR_DUPLICATE


# ----------------------------------------
def assignRoom(userId, email, building, room):
    affiliation = getRoomAffiliation(building, room)

    if affiliation is None:
        affiliation = {
            "department": [],
            "college": ""
        }

    if not check_permission("Department Update", userId, affiliation):
        return ERR_PERMISSION

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:

        cursor.execute("""
        INSERT INTO ROOMOCCUPANTS
        VALUES (%s,%s,%s,NOW())
        """, (email, building, room))

        log_result = logRoomAssignmentPerson(userId, building, room, email, "ASSIGN")

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception as e:
        print("assignRoom error:", e)
        DB.close()
        return ERR_DUPLICATE


# ----------------------------------------
def removeRoomAssignment(userId, email, building, room):

    affiliation = getRoomAffiliation(building, room)

    if affiliation is None:
        affiliation = {
            "department": [],
            "college": ""
        }

    if not check_permission("Department Update", userId, affiliation):
        return ERR_PERMISSION

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:

        cursor.execute("""
        DELETE FROM ROOMOCCUPANTS
        WHERE Email=%s AND BNumber=%s AND RNumber=%s
        """, (email, building, room))

        log_result = logRoomAssignmentPerson(userId, building, room, email, "REMOVE")

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception as e:
        print("removeRoomAssignment error:", e)
        DB.close()
        return ERR_UNKNOWN


# ----------------------------------------
def departmentAssignment(userId, dept, building, room):

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:
        # Get college of department
        cursor.execute("""
        SELECT College FROM DEPARTMENTS WHERE DId=%s
        """, (dept,))
        result = cursor.fetchone()

        if not result:
            DB.close()
            return ERR_NOT_FOUND

        college = result[0]

        affiliation = {
            "department": [dept],
            "college": college
        }

        if not check_permission("College Update", userId, affiliation):
            DB.close()
            return ERR_PERMISSION

        cursor.execute("""
        SELECT DeptID
        FROM DEPTOCCUPANT
        WHERE BNumber=%s AND RNumber=%s
        """, (building, room))

        result = cursor.fetchone()
        oldDept = result[0] if result else None

        cursor.execute("""
        DELETE FROM DEPTOCCUPANT
        WHERE BNumber=%s AND RNumber=%s
        """, (building, room))

        cursor.execute("""
        INSERT INTO DEPTOCCUPANT
        VALUES (%s,%s,%s,1,NOW())
        """, (dept, building, room))

        log_result = logRoomDeptChange(userId, building, room, oldDept, dept)

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception as e:
        print("departmentAssignment error:", e)
        DB.close()
        return ERR_UNKNOWN


# ----------------------------------------
def assignEquipment(userId, building, room, equipType, newCount):

    affiliation = getRoomAffiliation(building, room)

    if affiliation is None:
        affiliation = {
            "department": [],
            "college": ""
        }

    if not check_permission("Department Update", userId, affiliation):
        return ERR_PERMISSION

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:

        cursor.execute("""
        SELECT COUNT(*)
        FROM EQUIPtoROOM
        WHERE EquipType=%s AND BNumber=%s AND RNumber=%s
        """, (equipType, building, room))

        before = cursor.fetchone()[0]

        if newCount == 0:

            cursor.execute("""
            DELETE FROM EQUIPtoROOM
            WHERE EquipType=%s AND BNumber=%s AND RNumber=%s
            """, (equipType, building, room))

        elif before == 0:

            cursor.execute("""
            INSERT INTO EQUIPtoROOM
            VALUES (%s,%s,%s,NOW(),NULL)
            """, (equipType, room, building))

        else:

            cursor.execute("""
            UPDATE EQUIPtoROOM
            SET DateAssigned=NOW()
            WHERE EquipType=%s AND BNumber=%s AND RNumber=%s
            """, (equipType, building, room))

        log_result = logEquipmentAssignment(
            userId,
            building,
            room,
            equipType,
            before,
            newCount
        )

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception as e:
        print("assignEquipment error:", e)
        DB.close()
        return ERR_UNKNOWN


# ----------------------------------------
def addEquipmentType(userId, name, sensitive):

    if not check_permission("God", userId, {}):
        return ERR_PERMISSION

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:

        cursor.execute("""
INSERT INTO EQUIPMENT (TypeId, EquipName, isSensitive)
SELECT next_id, %s, %s
FROM (
    SELECT IFNULL(MAX(TypeId), 0) + 1 AS next_id
    FROM EQUIPMENT
) AS x
""", (name, sensitive))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception as e:
        print("addEquipmentType error:", e)
        DB.close()
        return ERR_DUPLICATE