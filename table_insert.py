from mysql.connector.abstracts import MySQLCursorAbstract, MySQLConnectionAbstract
from mysql.connector.aio import PooledMySQLConnection
import reset_database
from connector import make_connection
import parser_util
import csv

# --- Encoding-safe CSV reader ---
def read_csv_with_encoding(filename, has_header=True):
    """Reads CSV safely; tries utf-8-sig first, falls back to latin1."""
    try:
        f = open(filename, newline='', encoding='utf-8-sig')
        f.read(1)
        f.seek(0)
    except UnicodeDecodeError:
        f = open(filename, newline='', encoding='latin1')

    with f:
        if has_header:
            reader = csv.DictReader(f)
        else:
            reader = csv.reader(f)
        return list(reader)

# --- Dictionaries ---
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
    "AFD-Audit": "",
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

# --- Insert Functions ---
def insert_building(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract):
    cursor.execute(
        "INSERT INTO COLLEGES (Abbreviation, CName) "
        "VALUES ('BCSM', 'Bailey College of Science and Mathematics');"
    )
    DB.commit()

def insert_departments(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    departmentCSV = read_csv_with_encoding(filename, has_header=False)
    data = []
    for department in departmentCSV:
        department = department[0]
        curTuple = parser_util.parse_department(department)
        if curTuple is None:
            continue
        data.append(curTuple)
    cursor.executemany("INSERT INTO DEPARTMENTS (DId, College, DName) VALUES (%s, %s, %s);", data)
    cursor.execute("INSERT INTO DEPARTMENTS (DId, College, DName) VALUES ('999999', NULL, 'Unknown Department');")
    DB.commit()

def insert_RoomUseCodes(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    roomTypeCSV = read_csv_with_encoding(filename, has_header=False)
    data = [parser_util.parse_roomtype(r[0]) for r in roomTypeCSV]
    cursor.executemany("INSERT INTO ROOMTYPE (TypeId, TypeName) VALUES (%s, %s);", data)
    DB.commit()

def insert_RoomSpaceCategories(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    roomSpaceCSV = read_csv_with_encoding(filename, has_header=False)
    data = [(r[0], r[1]) for r in roomSpaceCSV]
    cursor.executemany("INSERT INTO ROOMSPACE (TypeId, TypeName) VALUES (%s, %s);", data)
    DB.commit()

def insert_from_furniture(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    equipmentCSV = read_csv_with_encoding(filename, has_header=False)
    data = [(equip[0], equip[1], 0) for equip in equipmentCSV]
    cursor.executemany("INSERT INTO EQUIPMENT (TypeId, EquipName, isSensitive) VALUES (%s, %s, %s);", data)
    DB.commit()

def insert_staffAndFaculty(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    staffCSV = read_csv_with_encoding(filename, has_header=True)
    data, nullData, emails, i = [], [], [], 1
    for staff in staffCSV:
        email = staff["Email Address"]
        deptID = staff["Deptid Code"]
        firstName = staff["Preferred First Name"]
        lastName = staff["Preferred Last Name"]
        emplType = staff["Empl Type Descr"]
        if (staff["College Name"] == "College of Science and Mathematics") and not (any(row[0] == email for row in data)):
            data.append((email, firstName, lastName, emplType, deptID))
            emails.append(email)

    """
        statement = "SELECT * FROM DEPARTMENTS WHERE DId = %s"
        for staff in data:
            deptID = staff[4]
    
            cursor.execute(statement, [deptID])
    
            res = cursor.fetchall()
            if(len(res) == 0):
                print(staff)
    """

    cursor.executemany("INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, %s, %s);", data)
    DB.commit()
    return emails

def insert_rooms(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    roomsCSV = read_csv_with_encoding(filename, has_header=True)
    building_data, floor_data, room_data, room_occupants_data, room_image_data, emails_not_in_staff, nullStaff = {}, [], {}, [], [], [], []

    for room in roomsCSV:
        room_split = parser_util.parse_room(room["Building & Room ID"])
        building_id, room_number = room_split[0], room_split[1]
        building_name = room["Building Name"]
        if building_id not in building_data:
            building_data[building_id] = (building_id, building_name, 0)
        floor_num = room["Floor"]
        if (building_id, floor_num) not in floor_data:
            floor_data.append((building_id, floor_num))
            building_data[building_id] = (building_id, building_name, building_data[building_id][2]+1)
        sqft = float(room[" Room size (SF)"].replace(",", ""))
        room_type = int(parser_util.parse_room_type(room["Room Use Code"]))
        room_space = int(parser_util.parse_room_type(room["Space Category"]))
        room_data[(building_id, room_number)] = (building_id, room_number, sqft, floor_num, building_id, room_type, room_space)
        occupants_str = room["Occupants"].strip()
        if occupants_str != "":
            occupants = parser_util.parse_multiple_staff(occupants_str)
            for staffTuple in occupants:
                lastName = staffTuple[0]
                firstName = staffTuple[1]

                statement = "SELECT Email FROM STAFFandFACULTY WHERE FirstName = %s AND LastName = %s;"
                cursor.execute(statement, (firstName, lastName))

                emails = cursor.fetchall()
                if len(emails) != 1:
                    email = firstName[0] + lastName + "47@calpoly.edu"
                    email = email.lower()
                    deptID = deptAbbrivationDict[staffTuple[2]]

                    if not any(row[0] == email for row in emails_not_in_staff + nullStaff):
                        if(deptID == ""):
                            nullStaff.append((email, firstName, lastName))
                        else:
                            emails_not_in_staff.append((email, firstName, lastName, deptID))
                else:
                    email = emails[0][0]
                if (email, building_id, room_number) not in room_occupants_data:
                    room_occupants_data.append((email, building_id, room_number))
        for i in range(1, 5):
            room_image = room.get(f"Room Photo{i}", "")
            if room_image != "":
                room_image_data.append((room_image, room_number, building_id))

    cursor.executemany("INSERT INTO BUILDINGS (BNumber, BName, BFloorCount) VALUES (%s, %s, %s);", list(building_data.values()))
    cursor.executemany("INSERT INTO FLOORS (BNumber, FNumber) VALUES (%s, %s);", floor_data)
    cursor.executemany("INSERT INTO ROOMS (BNumber, RNumber, SqFt, BoxCoordinates, HasBackup, FNumber, FBNumber, RoomType, RoomSpace) VALUES (%s, %s, %s, NULL, 0, %s, %s, %s, %s);", list(room_data.values()))
    for staff in emails_not_in_staff:
        deptID = staff[3]

        statement = "SELECT * FROM DEPARTMENTS WHERE DId = %s;"
        cursor.execute(statement, [deptID])

        res = cursor.fetchall()

        if(len(res) != 1):
            print(staff)
    cursor.executemany("INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, NULL, %s);", emails_not_in_staff)
    cursor.executemany("INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, NULL, NULL);", nullStaff)
    for staff in room_occupants_data:
        email = staff[0]

        statement = "SELECT Email FROM STAFFandFACULTY WHERE Email = %s;"
        cursor.execute(statement, [email])

        emails = cursor.fetchall()

        if(len(emails) != 1):
            print(email)
            print(emails)

    cursor.executemany("INSERT INTO ROOMOCCUPANTS (Email, BNumber, RNumber, DateAssigned) VALUES (%s, %s, %s, NOW());", room_occupants_data)
    cursor.executemany("INSERT INTO ROOMIMAGES (RImagePath, RNumber, BNumber) VALUES (%s, %s, %s);", room_image_data)
    DB.commit()

    print(emails_not_in_staff)

# wip
def insert_equipment(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
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

        if(equipment_name not in [x[1] for x in equipment_data.values()]):
            equipment_data[equipment_name] = (i, equipment_name)
            i += 1

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
                    cur_rnum = f"0D{int(cur_rnum[1:]):02d}-00"
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
            firstName, lastName = parser_util.parse_contact(primary_contact)

            statement = "SELECT Email FROM STAFFandFACULTY WHERE FirstName = %s AND LastName = %s;"
            cursor.execute(statement, (firstName, lastName))

            emails = cursor.fetchall()
            if len(emails) != 1:
                email = firstName[0] + lastName + "47@calpoly.edu"
                email = email.lower()
                if not any(row[0] == email for row in emails_not_in_staff):
                    emails_not_in_staff.append((email, firstName, lastName))
            else:
                email = emails[0][0]

            primary_contact_data.append((equipment_id, room_num, building_id, email))

        backup_contact = equipment["Contact person"]
        if (backup_contact != ""):
            firstName, lastName = parser_util.parse_contact(primary_contact)

            statement = "SELECT Email FROM STAFFandFACULTY WHERE FirstName = %s AND LastName = %s;"
            cursor.execute(statement, (firstName, lastName))

            emails = cursor.fetchall()
            if len(emails) != 1:
                email = firstName[0] + lastName + "47@calpoly.edu"
                email = email.lower()
                if not any(row[0] == email for row in emails_not_in_staff):
                    emails_not_in_staff.append((email, firstName, lastName))
            else:
                email = emails[0][0]

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
    statement = "INSERT INTO ROOMS (BNumber, RNumber, SqFt, BoxCoordinates, HasBackup, FNumber, FBNumber, RoomType, RoomSpace) VALUES ('043', '0251-00', NULL, NULL, 0, '2', '043', NULL, NULL);"
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

    DB.commit()

def insert_floorplans(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str):
    floorPlanCSV = read_csv_with_encoding(filename, has_header=True)

    roomCoordinates = []
    floor_plan_data = set()
    newRooms = []

    for plan in floorPlanCSV:
        plan_name = plan["Filename"]
        building_id = parser_util.literal_intstr_to_0intstr(plan["Building"])
        room_num = parser_util.floorplan_roomnum_to_table_notation(plan["Room"])
        floor_num = plan["Floor"]
        BoxCords = (float(plan["TopLeftX"]), float(plan["TopLeftY"]), float(plan["BottomRightX"]), float(plan["BottomRightY"]))

        if (room_num[-1] != "0" and (building_id, room_num, floor_num, building_id) not in newRooms):
            newRooms.append((building_id, room_num, floor_num, building_id))
        roomCoordinates.append((BoxCords[0], BoxCords[3], BoxCords[2], BoxCords[3], BoxCords[2], BoxCords[1], BoxCords[0], BoxCords[1], BoxCords[0], BoxCords[3], building_id, room_num))
        floor_plan_data.add((plan_name, building_id, floor_num))

    statement = "INSERT INTO ROOMS (BNumber, RNumber, SqFt, BoxCoordinates, HasBackup, FNumber, FBNumber, RoomType, RoomSpace) VALUES (%s, %s, NULL, NULL, 0, %s, %s, NULL, NULL);"
    cursor.executemany(statement, newRooms)

    statement = """
    UPDATE ROOMS
        SET BoxCoordinates = ST_GeomFromText(
          CONCAT(
            'POLYGON((',
            %s, ' ', %s, ', ',
            %s, ' ', %s, ', ',
            %s, ' ', %s, ', ',
            %s, ' ', %s, ', ',
            %s, ' ', %s,
            '))'
          )
        )
        WHERE BNumber = %s AND RNumber = %s;
    """
    cursor.executemany(statement, roomCoordinates)

    statement = "INSERT INTO FLOORPLANS (FImagePath, BNumber, FNumber) VALUES (%s, %s, %s);"
    cursor.executemany(statement, list(floor_plan_data))

    DB.commit()




# --- Main Script ---
if __name__ == "__main__":
    DB = make_connection("settings.config")
    cursor = DB.cursor()
    reset_database.reset_database(DB, cursor)

    insert_building(cursor, DB)
    insert_departments(cursor, DB, "Lab Project Data/BCSM Departments.csv")
    insert_RoomUseCodes(cursor, DB, "Lab Project Data/Room use codes.csv")
    insert_RoomSpaceCategories(cursor, DB, "Lab Project Data/Space Catagories.csv")
    insert_from_furniture(cursor, DB, "Lab Project Data/Furniture type.csv")
    insert_staffAndFaculty(cursor, DB, "Lab Project Data/Current Employees 20251031.csv")
    insert_rooms(cursor, DB, "Lab Project Data/BCSM Rooms.csv")
    insert_equipment(cursor, DB, "Lab Project Data/Critical BCSM Equipment.csv")
    insert_floorplans(cursor, DB, "Lab Project Data/Floorplans.csv")

    # Add default users
    users_to_add = [
        {"Email": "admin@calpoly.edu", "FirstName": "Admin", "LastName": "User", "URole": "Admin", "UPassword": "adminpass"},
        {"Email": "lowpriv@calpoly.edu", "FirstName": "Low", "LastName": "Privilege", "URole": "User", "UPassword": "lowpass"}
    ]
    for user in users_to_add:
        cursor.execute("SELECT COUNT(*) FROM USERS WHERE Email = %s;", (user["Email"],))
        exists = cursor.fetchone()[0]
        if exists == 0:
            cursor.execute("INSERT INTO USERS (Email, FirstName, LastName, URole, UPassword) VALUES (%s, %s, %s, %s, %s);",
                           (user["Email"], user["FirstName"], user["LastName"], user["URole"], user["UPassword"]))
            print(f"Added user {user['Email']} with role {user['URole']}")
        else:
            print(f"User {user['Email']} already exists, skipping.")

    DB.commit()

    cursor.close()
    DB.close()
