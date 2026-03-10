from connector import make_connection
from errors_api import *
from wal_api import *
import datetime

def addEmployee(first, last, email, dept, title, userId):

    try:

        DB = make_connection("settings.config")
        cursor = DB.cursor()

        # Check department exists
        cursor.execute(
            "SELECT * FROM DEPARTMENTS WHERE DId=%s",
            (dept,)
        )

        if cursor.fetchone() is None:
            DB.close()
            return ERR_NOT_FOUND

        # WAL logging
        log_result = logRoomAssignmentPerson(userId, None, None, email, "ADD_EMPLOYEE")

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        # Insert employee
        query = """
        INSERT INTO STAFFandFACULTY
        VALUES (%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (email, first, last, title, dept))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        return ERR_DUPLICATE
    
def assignRoom(userId, email, building, room):

    try:

        DB = make_connection("settings.config")
        cursor = DB.cursor()

        # check employee exists
        cursor.execute(
            "SELECT * FROM STAFFandFACULTY WHERE Email=%s",
            (email,)
        )

        if cursor.fetchone() is None:
            DB.close()
            return ERR_NOT_FOUND

        # WAL
        log_result = logRoomAssignmentPerson(
            userId,
            building,
            room,
            email,
            "ASSIGN"
        )

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        # insert assignment
        query = """
        INSERT INTO ROOMOCCUPANTS
        VALUES (%s,%s,%s,NOW())
        """

        cursor.execute(query, (email, building, room))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        return ERR_DUPLICATE
    
def removeRoomAssignment(userId, email, building, room):

    try:

        DB = make_connection("settings.config")
        cursor = DB.cursor()

        # WAL
        log_result = logRoomAssignmentPerson(
            userId,
            building,
            room,
            email,
            "REMOVE"
        )

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        query = """
        DELETE FROM ROOMOCCUPANTS
        WHERE Email=%s AND BNumber=%s AND RNumber=%s
        """

        cursor.execute(query, (email, building, room))

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        return ERR_UNKNOWN
    
def departmentAssignment(userId, dept, building, room):

    try:

        DB = make_connection("settings.config")
        cursor = DB.cursor()

        # find existing assignment
        cursor.execute(
            "SELECT DeptID FROM DEPTOCCUPANT WHERE BNumber=%s AND RNumber=%s",
            (building, room)
        )

        result = cursor.fetchone()

        oldDept = None
        if result:
            oldDept = result[0]

            cursor.execute(
                "DELETE FROM DEPTOCCUPANT WHERE BNumber=%s AND RNumber=%s",
                (building, room)
            )

        # WAL
        log_result = logRoomDeptChange(
            userId,
            building,
            room,
            oldDept,
            dept
        )

        if log_result != SUCCESS:
            DB.close()
            return ERR_LOGGING

        # insert new assignment
        cursor.execute(
            """
            INSERT INTO DEPTOCCUPANT
            VALUES (%s,%s,%s,1,NOW())
            """,
            (dept, building, room)
        )

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        return ERR_UNKNOWN
    
def assignEquipment(userId, building, room, equipType, newCount):

    try:

        DB = make_connection("settings.config")
        cursor = DB.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM EQUIPtoROOM
            WHERE EquipType=%s AND BNumber=%s AND RNumber=%s
            """,
            (equipType, building, room)
        )

        result = cursor.fetchone()
        before = result[0]

        # WAL
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

            cursor.execute(
                """
                DELETE FROM EQUIPtoROOM
                WHERE EquipType=%s AND BNumber=%s AND RNumber=%s
                """,
                (equipType, building, room)
            )

        elif before == 0:

            cursor.execute(
                """
                INSERT INTO EQUIPtoROOM
                VALUES (%s,%s,%s,NOW(),NULL)
                """,
                (equipType, room, building)
            )

        else:

            cursor.execute(
                """
                UPDATE EQUIPtoROOM
                SET DateAssigned=NOW()
                WHERE EquipType=%s AND BNumber=%s AND RNumber=%s
                """,
                (equipType, building, room)
            )

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        return ERR_UNKNOWN
    
def addEquipmentType(name, sensitive):

    try:

        DB = make_connection("settings.config")
        cursor = DB.cursor()

        cursor.execute(
            """
            INSERT INTO EQUIPMENT (EquipName,isSensitive)
            VALUES (%s,%s)
            """,
            (name, sensitive)
        )

        DB.commit()
        DB.close()

        return SUCCESS

    except Exception:
        return ERR_DUPLICATE
    
