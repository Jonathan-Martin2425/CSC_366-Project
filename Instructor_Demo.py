from connector import make_connection
from departments_api import getDeptList, getDeptListEnhanced
from employee_api import getEmployees, getEmployeeInfo
from equipment_api import getEquipmentLocations, getSensitiveEquipmentLocations
from floorplan_api import getFloorplans
from room_api import getRooms, findRoom, getRoomInfo
from dataManipulation_api import *
import json
import sys


if __name__ == "__main__":

    print("\n========================")
    print("captures the output in a file")
    print("========================")

    # sys.stdout = open("demo.txt", "w")


    print("========================================================")
    print("establishes DB connection, access the database instance")
    print("========================================================")

    # DB = make_connection("settings.config")
    # cursor = DB.cursor()
    #
    # cursor.execute('SHOW TABLES')
    # tables = cursor.fetchall()
    #
    # for table in tables:
    #     print(table)


    print("\n========================")
    print("sets the specific user")
    print("===========================")

    # user = "aamendes@calpoly.edu"


    print("\n========================")
    print("calls an API function")
    print("========================")

    # print("\nTesting getFloorplans()")
    # plans = getFloorplans("aamendes@calpoly.edu")
    # print(json.dumps(plans, indent=4))
    #
    # print("\nTesting getRooms()")
    # rooms = getRooms("aamendes@calpoly.edu", "033", "1")
    # print(json.dumps(rooms, indent=4))
    #
    # print("\nTesting findRoom(buildingNumber: 033, floorNumber: 1, x: 301, y: 899)")
    # room = findRoom("aamendes@calpoly.edu", "033", "1", 301, 899)
    # print(json.dumps(room, indent=4))
    #
    # print("\nTesting getRoomInfo()")
    # info = getRoomInfo("aamendes@calpoly.edu", "033", "0387-00")
    # print(json.dumps(info, indent=4))
    #
    # print("\nTesting getDeptList()")
    # depts = getDeptList("aamendes@calpoly.edu", "BCSM")
    # print(json.dumps(depts, indent=4))
    #
    # print("\nTesting getEmployees()")
    # employees = getEmployees("aamendes@calpoly.edu", "BCSM", "Statistics")
    # print(json.dumps(employees, indent=4))
    #
    # print("\nTesting getEmployeeInfo()")
    # employee = getEmployeeInfo("aamendes@calpoly.edu", {"Email": "atheobol@calpoly.edu"})
    # print(json.dumps(employee, indent=4))
    #
    # print("\nTesting getEquipmentLocations()")
    # Rooms = getEquipmentLocations("aamendes@calpoly.edu", "ULT Freezer")
    # print(json.dumps(Rooms, indent=4))
    #
    # print("\nTesting getSensitiveEquipmentLocations()")
    # rooms = getSensitiveEquipmentLocations("aamendes@calpoly.edu", "BCSM")
    # print(json.dumps(rooms, indent=4))
    #
    # print("\nTesting getDeptListEnhanced(college: BCSM)")
    # depts = getDeptListEnhanced("aamendes@calpoly.edu", "BCSM")
    # print(json.dumps(depts, indent=4))
    #
    # print("\nTesting addEmployee()")
    # result = addEmployee(
    #     "aamendes@calpoly.edu",  # userId
    #     "Test",
    #     "Employee",
    #     "testemployee@calpoly.edu",
    #     "999999",
    #     "Professor"
    # )
    # print("Result:", ERROR_MESSAGES[result])
    #
    # print("\nTesting assignRoom()")
    # result = assignRoom("aamendes@calpoly.edu", "jmmerria@calpoly.edu", "033", "0252-00")
    # print("Result:", ERROR_MESSAGES[result])
    #
    # print("\nTesting removeRoomAssignment()")
    # result = removeRoomAssignment("aamendes@calpoly.edu", "jmmerria@calpoly.edu", "033", "0252-00")
    # print("Result:", ERROR_MESSAGES[result])
    #
    # print("\nTesting assignEquipment()")
    # result = assignEquipment("aamendes@calpoly.edu", "033", "0252-00", "Bed", 5)
    # print("Result:", ERROR_MESSAGES[result])
    #
    # print("\nTesting departmentAssignment()")
    # result = departmentAssignment("aamendes@calpoly.edu", "115400", "033", "0252-00")
    # print("Result:", ERROR_MESSAGES[result])
    #
    # print("\nTesting addEquipmentType()")
    # result = addEquipmentType("aamendes@calpoly.edu", "Laser", 1)
    # print("Result:", ERROR_MESSAGES[result])


    print("\n===============================")
    print("retrieves the last log record")
    print("===============================")

    # DB = make_connection("settings.config")
    # cursor = DB.cursor()
    #
    # cursor.execute("SELECT * FROM LOGRECORDS")
    # results = cursor.fetchall()
    #
    # if results:
    #     print(results[-1])
    #
    # DB.close()