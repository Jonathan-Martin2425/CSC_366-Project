from connector import make_connection
from departments_api import getDeptList, getDeptListEnhanced
from employee_api import getEmployees, getEmployeeInfo
from equipment_api import getEquipmentLocations, getSensitiveEquipmentLocations
from floorplan_api import getFloorplans
from room_api import getRooms, findRoom, getRoomInfo
from dataManipulation_api import *
import json

def ensure_test_user(cursor, email, permission, dept=None, college=None):
    cursor.execute("SELECT Email FROM USERS WHERE Email=%s", (email,))
    
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO USERS (Email, UPermissionLevel, DeptID, CollegeID)
            VALUES (%s, %s, %s, %s)
        """, (email, permission, dept, college))

def setup_users():
    DB = make_connection("settings.config")
    cursor = DB.cursor()

    try:
        # Admin (no restriction needed)
        ensure_test_user(
            cursor,
            "admin@calpoly.edu",
            "God Level",
            "109400",
            "BCSM"
        )

        # Department-level user
        ensure_test_user(
            cursor,
            "testemployee@calpoly.edu",
            "Department Update Level",
            "109400",        # must exist in DEPARTMENTS
            "BCSM"
        )

        # Low privilege user
        ensure_test_user(
            cursor,
            "lowpriv@calpoly.edu",
            "Department View Level",
            "109400",
            "BCSM"
        )

        DB.commit()

    finally:
        DB.close()

if __name__ == "__main__":
    # ensure users exist
    setup_users()

    print("\n==============================")
    print("Testing getFloorplans()")
    print("==============================")
    plans = getFloorplans()
    print(json.dumps(plans, indent=4))

    print("\n==============================")
    print("Testing getRooms()")
    print("==============================")
    rooms = getRooms("033", "1")
    print(json.dumps(rooms, indent=4))

    print("\n==============================")
    print("Testing findRoom()")
    print("==============================")
    room = findRoom("033", "1", 301, 899)
    print(json.dumps(room, indent=4))

    print("\n==============================")
    print("Testing getRoomInfo()")
    print("==============================")
    info = getRoomInfo("033", "0387-00")
    print(json.dumps(info, indent=4))

    print("\n==============================")
    print("Testing getDeptList()")
    print("==============================")
    depts = getDeptList("BCSM")
    print(json.dumps(depts, indent=4))

    print("\n==============================")
    print("Testing getEmployees()")
    print("==============================")
    employees = getEmployees("BCSM", "Statistics")
    for emp in employees:
        print(emp)

    print("\n==============================")
    print("Testing getEmployeeInfo()")
    print("==============================")
    employee = getEmployeeInfo({"Email": "ydeniz@calpoly.edu"})
    print(employee)

    print("\n==============================")
    print("Testing getEquipmentLocations()")
    print("==============================")
    rooms = getEquipmentLocations("Bed")
    for room in rooms:
        print(room)

    print("\n==============================")
    print("Testing getSensitiveEquipmentLocations()")
    print("==============================")
    rooms = getSensitiveEquipmentLocations("BCSM")
    for room in rooms:
        print(room)

    print("\n==============================")
    print("Testing getDeptListEnhanced()")
    print("==============================")
    depts = getDeptListEnhanced("BCSM")
    print(json.dumps(depts, indent=4))

    # --- Data manipulation tests ---
    print("\n==============================")
    print("Testing addEmployee()")
    print("==============================")
    result = addEmployee(
        "admin@calpoly.edu",  # userId
        "Test",
        "Employee",
        "testemployee@calpoly.edu",
        "105-0002310",
        "Professor"
    )
    print("Result:", ERROR_MESSAGES[result])

    print("\n==============================")
    print("Testing assignRoom()")
    print("==============================")
    result = assignRoom("admin@calpoly.edu", "testemployee@calpoly.edu", "033", "0252-00")
    print("Result:", ERROR_MESSAGES[result])

    print("\n==============================")
    print("Testing removeRoomAssignment()")
    print("==============================")
    result = removeRoomAssignment("admin@calpoly.edu", "testemployee@calpoly.edu", "033", "0252-00")
    print("Result:", ERROR_MESSAGES[result])

    print("\n==============================")
    print("Testing assignEquipment()")
    print("==============================")
    result = assignEquipment("admin@calpoly.edu", "033", "0252-00", "Bed", 5)
    print("Result:", ERROR_MESSAGES[result])

    print("\n==============================")
    print("Testing departmentAssignment()")
    print("==============================")
    result = departmentAssignment("admin@calpoly.edu", "105-0002310", "033", "0252-00")
    print("Result:", ERROR_MESSAGES[result])

    print("\n==============================")
    print("Testing addEquipmentType()")
    print("==============================")
    result = addEquipmentType("admin@calpoly.edu", "Laser", 1)
    print("Result:", ERROR_MESSAGES[result])

    print("\n==============================")
    print("Testing Permission Denial (lowpriv)")
    print("==============================")
    result = assignEquipment("lowpriv@calpoly.edu", "033", "0252-00", "Bed", 3)
    print("Result:", ERROR_MESSAGES[result])

    # --- WAL Results ---
    print("\n================================")
    print("WAL Results")
    print("\n==================================")
    DB = make_connection("settings.config")
    cursor = DB.cursor()
    cursor.execute("SELECT * FROM LOGRECORDS")
    results = cursor.fetchall()
    print(results)
    DB.close()