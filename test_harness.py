from departments_api import getDeptListEnhanced
from employee_api import getEmployees, getEmployeeInfo
from equipment_api import getEquipmentLocations, getSensitiveEquipmentLocations
from floorplan_api import getFloorplans
from room_api import getRooms, findRoom, getRoomInfo
from dataManipulation_api import *


if __name__ == "__main__":

    print("\n==============================")
    print("Testing getFloorplans()")
    print("==============================")

    plans = getFloorplans()
    for plan in plans:
        print(plan)


    print("\n==============================")
    print("Testing getRooms()")
    print("==============================")

    rooms = getRooms("033", "1")
    for room in rooms:
        print(room)


    print("\n==============================")
    print("Testing findRoom()")
    print("==============================")

    room = findRoom("033", "1", 100, 200)
    print(room)


    print("\n==============================")
    print("Testing getRoomInfo()")
    print("==============================")

    info = getRoomInfo("033", "0 0378-00")
    print(info)


    print("\n==============================")
    print("Testing getEmployees()")
    print("==============================")

    employees = getEmployees("BCSM", "Statistics")
    for emp in employees:
        print(emp)


    print("\n==============================")
    print("Testing getEmployeeInfo()")
    print("==============================")

    employee = getEmployeeInfo({
        "Email": "wcrow@calpoly.edu"
    })
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
    for dept in depts:
        print(dept)

    from dataManipulation_api import addEmployee

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

    print("Result:", result)

    from dataManipulation_api import assignRoom

print("\n==============================")
print("Testing assignRoom()")
print("==============================")

result = assignRoom(
    "admin@calpoly.edu",
    "testemployee@calpoly.edu",
    "033",
    "101"
)

print("Result:", result)

from dataManipulation_api import removeRoomAssignment

print("\n==============================")
print("Testing removeRoomAssignment()")
print("==============================")

result = removeRoomAssignment(
    "admin@calpoly.edu",
    "testemployee@calpoly.edu",
    "033",
    "101"
)

print("Result:", result)

from dataManipulation_api import assignEquipment

print("\n==============================")
print("Testing assignEquipment()")
print("==============================")

result = assignEquipment(
    "admin@calpoly.edu",
    "033",
    "101",
    "Bed",
    5
)

print("Result:", result)

from dataManipulation_api import departmentAssignment

print("\n==============================")
print("Testing departmentAssignment()")
print("==============================")

result = departmentAssignment(
    "admin@calpoly.edu",
    "105-0002310",
    "033",
    "101"
)

print("Result:", result)

from dataManipulation_api import addEquipmentType

print("\n==============================")
print("Testing addEquipmentType()")
print("==============================")

result = addEquipmentType(
    "admin@calpoly.edu",
    "Laser",
    1
)

print("Result:", result)

print("\n==============================")
print("Testing Permission Denial")
print("==============================")

result = assignEquipment(
    "lowpriv@calpoly.edu",
    "033",
    "101",
    "Bed",
    3
)

print("Result:", result)

print("\n================================")
print("WAL Results")
print("\n==================================")

DB = make_connection("settings.config")
cursor = DB.cursor()

query = """
SELECT * FROM WAL_LOG;
"""

cursor.execute(query)
results = cursor.fetchall()

print(results)