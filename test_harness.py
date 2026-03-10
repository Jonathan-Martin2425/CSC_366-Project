from departments_api import getDeptListEnhanced
from employee_api import getEmployees, getEmployeeInfo
from equipment_api import getEquipmentLocations, getSensitiveEquipmentLocations
from floorplan_api import getFloorplans
from room_api import getRooms, findRoom, getRoomInfo


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