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

deptNameDict = {
    "Biological Sciences": "115100",
    "Mathematics": "115400",
    "Chemistry/Biochemistry": "115200",
    "Kinesiology and Public Health": "115600",
    "Physics": "115500",
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

    return emails_not_in_staff

# wip
def insert_equipment(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str, emails: list):
    equipmentCSV = parser_util.parse_csv(filename)


    backup_power_rooms = []
    equipment_data = {}
    room_to_equip_data = []
    room_to_equip_comment_data = []
    short_action_data = []
    medium_action_data = []
    long_action_data = []
    primary_contact_data = []
    backup_contact_data = []
    emails_not_in_staff = []
    i = 11
    for equipment in equipmentCSV:

        equipment_name = equipment["Critical and/or sensitive equipment or materials requiring attention"]

        for name in equipment_data.keys():
            if(equipment_data[name][1] == equipment_name):
                equipment_id = equipment_data[name][0]
        building_id = parser_util.literal_intstr_to_0intstr(equipment["Building Number"])
        room_num = parser_util.reg_room_num_to_table_notation(equipment[" Room"])
        if(room_num == None): continue
        if(type(room_num) == list):
            primary_contact = equipment["Contact person"]
            staffTuple = parser_util.parse_contact(primary_contact)
            pemail: str = staffTuple[0][0] + staffTuple[1] + "@calpoly.edu"
            pemail = pemail.lower()
            backup_contact = equipment["Contact person"]
            staffTuple = parser_util.parse_contact(backup_contact)
            bemail: str = staffTuple[0][0] + staffTuple[1] + "@calpoly.edu"
            bemail = bemail.lower()
            for cur_rnum in room_num:
                if(cur_rnum[0] == "D"):
                    cur_rnum = f"0 0D{int(cur_rnum[1:]):02d}-00"
                else:
                    continue
                room_to_equip_data.append((equipment_id, cur_rnum, building_id))
                short_action_data.append(("1", equipment_id, building_id, cur_rnum))
                medium_action_data.append(("2", equipment_id, building_id, cur_rnum))
                long_action_data.append(("2", equipment_id, building_id, cur_rnum))
                primary_contact_data.append((equipment_id, cur_rnum, building_id, pemail))
                backup_contact_data.append((equipment_id, cur_rnum, building_id, bemail))
            continue


        if(equipment["Alternative best action"] == ""):
            room_to_equip_data.append((equipment_id, room_num, building_id))
        else:
            room_to_equip_comment_data.append((equipment_id, room_num, building_id, equipment["Alternative best action"]))

        short_actions = parser_util.parse_action(equipment["Short period of time    (1-2 days)"])
        for action in short_actions:
            short_action_data.append((action, equipment_id, building_id, room_num))

        medium_actions = parser_util.parse_action(equipment["Medium period of time (3-5 Days)"])
        for action in medium_actions:
            medium_action_data.append((action, equipment_id, building_id, room_num))

        long_actions = parser_util.parse_action(equipment["Long period of time (7+ days)"])
        for action in long_actions:
            long_action_data.append((action, equipment_id, building_id, room_num))

        primary_contact = equipment["Contact person"]
        if(primary_contact != ""):
            staffTuple = parser_util.parse_contact(primary_contact)
            email: str = staffTuple[0][0] + staffTuple[1] + "@calpoly.edu"
            email = email.lower()

            if email not in emails and not any(i[0] == email for i in emails_not_in_staff):
                staffTuple = (email, staffTuple[0], staffTuple[1])
                emails_not_in_staff.append(staffTuple)

            primary_contact_data.append((equipment_id, room_num, building_id, email))

        backup_contact = equipment["Contact person"]
        if (backup_contact != ""):
            staffTuple = parser_util.parse_contact(backup_contact)
            email: str = staffTuple[0][0] + staffTuple[1] + "@calpoly.edu"
            email = email.lower()

            if email not in emails and not any(i[0] == email for i in emails_not_in_staff):
                staffTuple = (email, staffTuple[0], staffTuple[1])
                emails_not_in_staff.append(staffTuple)

            backup_contact_data.append((equipment_id, room_num, building_id, email))

    statement = "INSERT INTO EQUIPMENT (TypeId, EquipName, isSensitive) VALUES (%s, %s, 1);"
    cursor.executemany(statement, list(equipment_data.values()))

    actions = [
        (1, "No action needed if building is secure and there is continual electrical service."),
        (2, "Authorized staff would need one-time access to safely shut down and stow equipment."),
        (3, "Authorized staff would need one-time access to move hazardous materials to safe storage."),
        (4, "Authorized staff would need regular access to monitor and perform upkeep."),
        (5, "Authorized staff would need perodic access to monitor and perform upkeep."),
        (6, "Equipment and/or materials would need to be relocated for backup power, containment, monitoring, upkeep."),
        (7, "Equipment and/or materials cannot be relocated; authorized staff would need regular access to monitor health and perform upkeep."),
        (8, "Alternative best action"),
    ]
    statement = "INSERT INTO ACTIONS (AId, Descript) VALUES (%s, %s);"
    cursor.executemany(statement, actions)

    statement = "UPDATE ROOMS SET HasBackup = 1 WHERE BNumber = %s, RNumber = %s;"
    cursor.executemany(statement, backup_power_rooms)

    # add this room, because it doesn't exist and is only defined here
    statement = "INSERT INTO ROOMS (BNumber, RNumber, SqFt, BoxCoordinates, HasBackup, FNumber, FBNumber, RoomType, RoomSpace) VALUES ('043', '0 0251-00', NULL, NULL, 0, '2', '043', NULL, NULL);"
    cursor.execute(statement)

    statement = "INSERT INTO EQUIPtoROOM (EquipType, RNumber, BNumber, DateAssigned, Comments) VALUES (%s, %s, %s, NOW(), NULL);"
    cursor.executemany(statement, room_to_equip_data)

    statement = "INSERT INTO EQUIPtoROOM (EquipType, RNumber, BNumber, DateAssigned, Comments) VALUES (%s, %s, %s, NOW(), %s);"
    cursor.executemany(statement, room_to_equip_comment_data)

    statement = "INSERT INTO EQUIPMENTACTIONS (ActionID, EquipID, BNumber, RNumber, Duration) VALUES (%s, %s, %s, %s, 'Short');"
    cursor.executemany(statement, short_action_data)

    statement = "INSERT INTO EQUIPMENTACTIONS (ActionID, EquipID, BNumber, RNumber, Duration) VALUES (%s, %s, %s, %s, 'Medium');"
    cursor.executemany(statement, medium_action_data)

    statement = "INSERT INTO EQUIPMENTACTIONS (ActionID, EquipID, BNumber, RNumber, Duration) VALUES (%s, %s, %s, %s, 'Long');"
    cursor.executemany(statement, long_action_data)

    statement = "INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, NULL, NULL);"
    cursor.executemany(statement, emails_not_in_staff)

    statement = "INSERT INTO CONTACTPERSONS (EquipType, RNumber, BNumber, Email, Type) VALUES (%s, %s, %s, %s, 'Primary');"
    cursor.executemany(statement, primary_contact_data)

    statement = "INSERT INTO CONTACTPERSONS (EquipType, RNumber, BNumber, Email, Type) VALUES (%s, %s, %s, %s, 'Backup');"
    cursor.executemany(statement, backup_contact_data)

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
    emails.extend([i[0] for i in insert_rooms(cursor, DB, "Lab Project Data/BCSM Rooms.csv", emails)])
    insert_equipment(cursor, DB, "Lab Project Data/Critical BCSM Equipment.csv", emails)

    # close connections to end program
    cursor.close()
    DB.close()
