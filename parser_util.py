import csv


def parse_csv(filename: str, has_header: bool = True):
    file = open(filename, "r")

    if has_header:
        res = csv.DictReader(file)
    else:
        res = csv.reader(file)

    return res

def parse_department(line: str) -> tuple:
    if(line == '117508-BCSM-Ctr Sci-Math Teacher Educ'):
        line = "117508-BCSM-Ctr Sci Math Teacher Educ"
    elif (line == "999999-Unknown Department"):
        return None

    split = line.split("-")

    return tuple(split)

def parse_roomtype(line: str) -> tuple:
    split = line.split(" - ", maxsplit=1)
    return tuple(split)

def parse_staff(line:str) -> tuple:
    split = line.split(" (CSM")

    try:
        split2 = split[0].split(", ")
        split[1] = split[1].strip("(-)")
    except:
        split = line.split(" (")
        split2 = split[0].split(", ")
        split[1] = split[1].strip("(-)")

    return split2[0], split2[1], split[1]

def parse_room(line:str):
    split = line.split('-', 1)

    return split

def parse_room_type(line:str):
    split = line.split(' ', 1)

    return split[0]

def parse_multiple_staff(line: str):
    staff = line.split(";")

    res = []
    for person in staff:
        try:
            res.append(parse_staff(person))
        except:
            print(person)
            return staff

    return res


