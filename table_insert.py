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
    staffCSV = read_csv_with_encoding(filename, has_header=False)
    data, nullData, emails, i = [], [], [], 1
    for staff in staffCSV:
        staff = staff[0]
        staffTuple = parser_util.parse_staff(staff)
        email = (staffTuple[0][0] + staffTuple[1] + "@calpoly.edu").lower()
        while any(email == row[0] for row in data) or any(email == row[0] for row in nullData):
            atIndex = email.index('@')
            email = email[:atIndex] + str(i) + email[atIndex:]
            i += 1
        if staffTuple[2] not in deptAbbrivationDict:
            nullData.append((email, staffTuple[1], staffTuple[0]))
        else:
            deptID = deptAbbrivationDict[staffTuple[2]]
            data.append((email, staffTuple[1], staffTuple[0], deptID))
        emails.append(email)
    cursor.executemany("INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, NULL, %s);", data)
    cursor.executemany("INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, NULL, NULL);", nullData)
    DB.commit()
    return emails

def insert_rooms(cursor: MySQLCursorAbstract, DB: MySQLConnectionAbstract, filename: str, emails: list):
    roomsCSV = read_csv_with_encoding(filename, has_header=True)
    building_data, floor_data, room_data, room_occupants_data, room_image_data, emails_not_in_staff = {}, [], {}, [], [], []

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
                email = (staffTuple[0][0]+staffTuple[1]+"@calpoly.edu").lower()
                if email not in emails and not any(email == s[0] for s in emails_not_in_staff):
                    deptID = deptAbbrivationDict.get(staffTuple[2], None)
                    if deptID is None or deptID == "":
                        continue
                    emails_not_in_staff.append((email, staffTuple[1], staffTuple[0], deptID))
                if (email, building_id, room_number) not in room_occupants_data:
                    room_occupants_data.append((email, building_id, room_number))
        for i in range(1, 5):
            room_image = room.get(f"Room Photo{i}", "")
            if room_image != "":
                room_image_data.append((room_image, room_number, building_id))

    cursor.executemany("INSERT INTO BUILDINGS (BNumber, BName, BFloorCount) VALUES (%s, %s, %s);", list(building_data.values()))
    cursor.executemany("INSERT INTO FLOORS (BNumber, FNumber) VALUES (%s, %s);", floor_data)
    cursor.executemany("INSERT INTO ROOMS (BNumber, RNumber, SqFt, BoxCoordinates, HasBackup, FNumber, FBNumber, RoomType, RoomSpace) VALUES (%s, %s, %s, NULL, 0, %s, %s, %s, %s);", list(room_data.values()))
    cursor.executemany("INSERT INTO STAFFandFACULTY (Email, FirstName, LastName, Title, DeptID) VALUES (%s, %s, %s, NULL, %s);", emails_not_in_staff)
    cursor.executemany("INSERT INTO ROOMOCCUPANTS (Email, BNumber, RNumber, DateAssigned) VALUES (%s, %s, %s, NOW());", room_occupants_data)
    cursor.executemany("INSERT INTO ROOMIMAGES (RImagePath, RNumber, BNumber) VALUES (%s, %s, %s);", room_image_data)
    DB.commit()
    return emails_not_in_staff

# --- Main Script ---
if __name__ == "__main__":
    DB = make_connection("settings.config")
    cursor = DB.cursor()
    reset_database.reset_database(DB, cursor)

    insert_building(cursor, DB)
    insert_departments(cursor, DB, "BCSM Departments.csv")
    insert_RoomUseCodes(cursor, DB, "Room use codes.csv")
    insert_RoomSpaceCategories(cursor, DB, "Space Catagories.csv")
    insert_from_furniture(cursor, DB, "Furniture type.csv")

    emails = insert_staffAndFaculty(cursor, DB, "BCSM Faculty and departments.csv")
    emails.extend([i[0] for i in insert_rooms(cursor, DB, "BCSM Rooms.csv", emails)])

    # Placeholder: insert_equipment(...) goes here if needed

    # Add default users
    users_to_add = [
        {"Email": "admin@calpoly.edu", "FirstName": "Admin", "LastName": "User", "URole": "Admin", "UPassword": "adminpass"},
        {"Email": "lowpriv@calpoly.edu", "FirstName": "Low", "LastName": "Privilege", "URole": "User", "UPassword": "lowpass"}
    ]
    for user in users_to_add:
        cursor.execute("SELECT COUNT(*) FROM USERS WHERE Email = %s", (user["Email"],))
        exists = cursor.fetchone()[0]
        if exists == 0:
            cursor.execute("INSERT INTO USERS (Email, FirstName, LastName, URole, UPassword) VALUES (%s, %s, %s, %s, %s);",
                           (user["Email"], user["FirstName"], user["LastName"], user["URole"], user["UPassword"]))
            print(f"Added user {user['Email']} with role {user['URole']}")
        else:
            print(f"User {user['Email']} already exists, skipping.")

    cursor.close()
    DB.close()