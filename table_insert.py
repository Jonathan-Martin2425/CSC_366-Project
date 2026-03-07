from mysql.connector.abstracts import MySQLCursorAbstract, MySQLConnectionAbstract
from mysql.connector.aio import PooledMySQLConnection

import reset_database
from connector import make_connection

import parser_util


deptAbbrivationDict = {
    "PHYS": "115500",
    "BIO": "115100",
    "EDUC": "117600",
    "DEAN": "117502",
    "LS": "109400",
    "Advising": "117501",
    "STAR": "117512",
    "LSAMP": "117511",
    "KINE": "115600",
    "KIN": "115600",
    "STAT": "115300",
    "STA": "115300",
    "Advancement": "117504",
    "Advanc": "117504",
    "MATI": "117509",
    "DFAB": "117513",
    "CCMS": "117506",
    "CHEM": "115200",
    "MATH": "115400",
    "AFD-Audit": "", # all following entries are from different colleges, therefore will not be included
    "CENG-CSC": "",
    "CENG-BMED": "",
}

def insert_building(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract):
    cursor.execute("INSERT INTO COLLEGES (Abbreviation, CName) "
                   "VALUES ('BCSM', 'Bailey College of Science and Mathematics');")
    DB.commit()


def insert_departments(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    departmentCSV = parser_util.parse_csv(filename, has_header=False)

    data = []
    for department in departmentCSV:
        department = department[0]
        curTuple = parser_util.parse_department(department)

        if(curTuple == None):
            continue
        data.append(curTuple)

    statement = "INSERT INTO DEPARTMENTS (DId, College, DName) VALUES (%s, %s, %s);"
    cursor.executemany(statement, data)

    cursor.execute("INSERT INTO DEPARTMENTS (DId, College, DName) VALUES ('999999', NULL, 'Unknown Department');")

    DB.commit()

def insert_RoomUseCodes(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    roomTypeCSV = parser_util.parse_csv(filename, has_header=False)

    data = []
    for roomtype in roomTypeCSV:
        roomtype = roomtype[0]
        curTuple = parser_util.parse_roomtype(roomtype)
        data.append(curTuple)

    statement = "INSERT INTO ROOMTYPE (TypeId, TypeName) VALUES (%s, %s);"
    cursor.executemany(statement, data)

    DB.commit()

def insert_RoomSpaceCategories(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    roomSpaceCSV = parser_util.parse_csv(filename, has_header=False)

    data = []
    for roomSpace in roomSpaceCSV:
        id = roomSpace[0]
        name = roomSpace[1]
        curTuple = (id, name)
        data.append(curTuple)

    statement = "INSERT INTO ROOMSPACE (TypeId, TypeName) VALUES (%s, %s);"
    cursor.executemany(statement, data)

    DB.commit()

def insert_from_furniture(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    equipmentCSV = parser_util.parse_csv(filename, has_header=False)

    data = []
    for equip in equipmentCSV:
        id = equip[0]
        name = equip[1]
        curTuple = (id, name, 0)
        data.append(curTuple)

    statement = "INSERT INTO EQUIPMENT (TypeId, EquipName, isSensitive) VALUES (%s, %s, %s);"
    cursor.executemany(statement, data)

    DB.commit()


# inserts into
def insert_staffAndFaculty(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    staffCSV = parser_util.parse_csv(filename, has_header=False)

    data = []
    nullData = []
    emails = []
    i = 1
    for staff in staffCSV:
        staff = staff[0]
        staffTuple = parser_util.parse_staff(staff)
        email: str = staffTuple[0][0] + staffTuple[1] + "@calpoly.edu"
        email = email.lower()

        if (any(email == row[0] for row in data) or any(email == row[0] for row in nullData)):
            atIndex = email.index('@')
            email = email[:atIndex] + str(i) + email[atIndex:]
            i += 1

        if(staffTuple[2] not in deptAbbrivationDict.keys()):
            curTuple = (email, staffTuple[1], staffTuple[0])
            nullData.append(curTuple)
        else:
            deptID = deptAbbrivationDict[staffTuple[2]]
            curTuple = (email, staffTuple[1], staffTuple[0], deptID)
            data.append(curTuple)
        emails.append(email)

    statement = "INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, NULL, %s);"
    cursor.executemany(statement, data)

    statement = "INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, NULL, NULL);"
    cursor.executemany(statement, nullData)

    DB.commit()

    return emails

def insert_rooms(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str, emails: list):
    roomsCSV = parser_util.parse_csv(filename)

    building_data = {}
    floor_data = []
    room_data = {}
    room_occupants_data = []
    room_image_data = []
    i = 0

    emails_not_in_staff = []
    for room in roomsCSV:
        room_split = parser_util.parse_room(room["Building & Room ID"])

        # get all building attributes, then add it to building data if it doesn't already exist
        building_id = room_split[0]
        building_name = room["Building Name"]
        if(building_id not in building_data.keys()):
            building_data[building_id] = (building_id, building_name, 0)

        # get all floor attributes, then add it to floor data if it doesn't exist
        floor_num = room["Floor"]
        if((building_id, floor_num) not in floor_data):
            floor_data.append((building_id, floor_num))
            building_data[building_id] = (building_id, building_name, building_data[building_id][2] + 1)

        # get room other attributes, then add it to room data
        room_number = room_split[1]
        sqft = float(room[" Room size (SF)"].replace(",", ""))
        room_type = int(parser_util.parse_room_type(room["Room Use Code"]))
        room_space = int(parser_util.parse_room_type(room["Space Category"]))
        room_data[(building_id, room_number)] = (building_id, room_number, sqft, floor_num, building_id, room_type, room_space)

        # get occupants in rooms to add to ROOMOCUPANTS table
        if(room["Occupants"].strip(" ") != ""):
            curStaff = parser_util.parse_multiple_staff(room["Occupants"])
            for staffTuple in curStaff:
                email: str = staffTuple[0][0] + staffTuple[1] + "@calpoly.edu"
                email = email.lower()

                if(email not in emails and email not in emails_not_in_staff):
                    deptID = deptAbbrivationDict[staffTuple[2]]
                    if(deptID == ""): continue
                    staffTuple = (email, staffTuple[1], staffTuple[0], deptID)
                    emails_not_in_staff.append(staffTuple)

                if((email, building_id, room_number) not in room_occupants_data):
                    room_occupants_data.append((email, building_id, room_number))


        # get values from each room_image column and record them
        # if they exist
        for i in range (1, 5):
            room_image = room[f"Room Photo{i}"]
            if(room_image != ""):
                room_image_data.append((room_image, room_number, building_id))

    # add any staff and faculty that were mentioned here but not faculty csv to table



    # execute all statments in order to populate each table
    statement = "INSERT INTO BUILDINGS (BNumber, BName, BFloorCount) VALUES (%s, %s, %s);"
    cursor.executemany(statement, list(building_data.values()))

    statement = "INSERT INTO FLOORS (BNumber, FNumber) VALUES (%s, %s);"
    cursor.executemany(statement, floor_data)

    statement = "INSERT INTO ROOMS (BNumber, RNumber, SqFt, BoxCoordinates, HasBackup, FNumber, FBNumber, RoomType, RoomSpace) VALUES (%s, %s, %s, NULL, 0, %s, %s, %s, %s);"
    cursor.executemany(statement, list(room_data.values()))

    statement = "INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, NULL, %s);"
    cursor.executemany(statement, emails_not_in_staff)

    statement = "INSERT INTO ROOMOCCUPANTS (Email, BNumber, RNumber, DateAssigned) VALUES (%s, %s, %s, NOW());"
    cursor.executemany(statement, room_occupants_data)

    statement = "INSERT INTO ROOMIMAGES (RImagePath, RNumber, BNumber) VALUES (%s, %s, %s);"
    cursor.executemany(statement, room_image_data)

    DB.commit()

# wip
def insert_equipment(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    return

if __name__ == "__main__":
    DB = make_connection("settings.config")
    cursor = DB.cursor()

    reset_database.reset_database(DB, cursor)

    insert_building(cursor, DB)
    insert_departments(cursor, DB, "Lab Project Data/BCSM Departments.csv")
    insert_RoomUseCodes(cursor, DB, "Lab Project Data/Room use codes.csv")
    insert_RoomSpaceCategories(cursor, DB, "Lab Project Data/Space Catagories.csv")
    insert_from_furniture(cursor, DB, "Lab Project Data/Furniture type.csv")
    emails = insert_staffAndFaculty(cursor, DB, "Lab Project Data/BCSM Faculty and departments.csv")
    insert_rooms(cursor, DB, "Lab Project Data/BCSM Rooms.csv", emails)
    insert_equipment(cursor, DB, "Lab Project Data/Critical BCSM Equipment.csv")


    # close connections to end program
    cursor.close()
    DB.close()
