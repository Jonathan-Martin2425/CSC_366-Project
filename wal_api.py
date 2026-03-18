from connector import make_connection
from errors_api import *
import datetime

def _write_log(action, userId, building=None, room=None, email=None, equipID=None, details=None):

    try:

        DB = make_connection("settings.config")
        cursor = DB.cursor()

        # 🔥 FIX: replace None with dummy values
        if building is None:
            building = "N/A"
        if room is None:
            room = "N/A"

        query = """
        INSERT INTO LOGRECORDS
        (RTime, RType, RUser, BNumber, RNumber, Email, EquipID, RAction)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (
            datetime.datetime.now(),
            action,
            userId,
            building,
            room,
            email,
            equipID,
            details
        ))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception as e:
        print("LOG ERROR:", e)
        return ERR_LOGGING
    
    
def logLogin(userId):

    return _write_log(
        action="LOGIN",
        userId=userId,
        details="User logged in"
    )

def logLogout(userId):

    return _write_log(
        action="LOGOUT",
        userId=userId,
        details="User logged out"
    )

def logRoomAssignmentPerson(userId, building, room, employeeId, actionType):

    details = f"{actionType} employee {employeeId}"

    return _write_log(
        action="ROOM_PERSON_ASSIGNMENT",
        userId=userId,
        building=building,
        room=room,
        email=employeeId,
        details=details
    )

def logEquipmentAssignment(userId, building, room, equipmentType, before, after):

    details = f"{equipmentType}: {before} -> {after}"

    return _write_log(
        action="EQUIPMENT_ASSIGNMENT",
        userId=userId,
        building=building,
        room=room,
        equipID=equipmentType,
        details=details
    )

def logRoomDeptChange(userId, building, room, fromDept, toDept):

    details = f"{fromDept} -> {toDept}"

    return _write_log(
        action="ROOM_DEPT_CHANGE",
        userId=userId,
        building=building,
        room=room,
        details=details
    )

