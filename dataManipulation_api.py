from connector import make_connection
from errors_api import *
from wal_api import *
from permissions import *
import datetime

def getRoomDepartment(building, room):

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    cursor.execute("""
    SELECT DeptID
    FROM DEPTOCCUPANT
    WHERE BNumber=%s AND RNumber=%s
    """, (building, room))

    result = cursor.fetchone()
    DB.close()

    if result:
        return result[0]

    return None

def addEmployee(userId, first, last, email, dept, title):

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    affiliation = {"department": [dept]}

    if not validatePermission("Department Update Level", userId, affiliation):
        DB.close()
        return ERR_PERMISSION

    try:

        log_result = logRoomAssignmentPerson(userId, None, None, email, "ADD_EMPLOYEE")

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        cursor.execute("""
        INSERT INTO STAFFandFACULTY
        VALUES (%s,%s,%s,%s,%s)
        """, (email, first, last, title, dept))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        DB.close()
        return ERR_DUPLICATE
    
def assignRoom(userId, email, building, room):

    dept = getRoomDepartment(building, room)

    if dept is None:
        return ERR_NOT_FOUND

    affiliation = {"department": [dept]}

    if not validatePermission("Department Update Level", userId, affiliation):
        return ERR_PERMISSION

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:

        log_result = logRoomAssignmentPerson(userId, building, room, email, "ASSIGN")

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        cursor.execute("""
        INSERT INTO ROOMOCCUPANTS
        VALUES (%s,%s,%s,NOW())
        """, (email, building, room))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        DB.close()
        return ERR_DUPLICATE
    
def removeRoomAssignment(userId, email, building, room):

    dept = getRoomDepartment(building, room)

    if dept is None:
        return ERR_NOT_FOUND

    affiliation = {"department": [dept]}

    if not validatePermission("Department Update Level", userId, affiliation):
        return ERR_PERMISSION

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:

        log_result = logRoomAssignmentPerson(userId, building, room, email, "REMOVE")

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        cursor.execute("""
        DELETE FROM ROOMOCCUPANTS
        WHERE Email=%s AND BNumber=%s AND RNumber=%s
        """, (email, building, room))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        DB.close()
        return ERR_UNKNOWN
    
def departmentAssignment(userId, dept, building, room):

    affiliation = {"department": [dept]}

    if not validatePermission("College Update Level", userId, affiliation):
        return ERR_PERMISSION

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:

        cursor.execute("""
        SELECT DeptID
        FROM DEPTOCCUPANT
        WHERE BNumber=%s AND RNumber=%s
        """, (building, room))

        result = cursor.fetchone()
        oldDept = result[0] if result else None

        log_result = logRoomDeptChange(userId, building, room, oldDept, dept)

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        cursor.execute("""
        DELETE FROM DEPTOCCUPANT
        WHERE BNumber=%s AND RNumber=%s
        """, (building, room))

        cursor.execute("""
        INSERT INTO DEPTOCCUPANT
        VALUES (%s,%s,%s,1,NOW())
        """, (dept, building, room))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        DB.close()
        return ERR_UNKNOWN
    
def assignEquipment(userId, building, room, equipType, newCount):

    dept = getRoomDepartment(building, room)

    if dept is None:
        return ERR_NOT_FOUND

    affiliation = {"department": [dept]}

    if not validatePermission("Department Update Level", userId, affiliation):
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

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        DB.close()
        return ERR_UNKNOWN
    
def addEquipmentType(userId, name, sensitive):

    if not validatePermission("God Level", userId, {}):
        return ERR_PERMISSION

    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:

        cursor.execute("""
        INSERT INTO EQUIPMENT (EquipName,isSensitive)
        VALUES (%s,%s)
        """, (name, sensitive))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        DB.close()
        return ERR_DUPLICATE
    
