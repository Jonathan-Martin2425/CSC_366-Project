import csv
import re
from typing import List
from time import sleep


def parse_csv(filename: str, has_header: bool = True):
    file = open(filename, "r")

    if has_header:
        res = csv.DictReader(file)
    else:
        res = csv.reader(file)

    return res


def parse_department(line: str) -> tuple:
    if (line == '117508-BCSM-Ctr Sci-Math Teacher Educ'):
        line = "117508-BCSM-Ctr Sci Math Teacher Educ"
    elif (line == "999999-Unknown Department"):
        return None

    split = line.split("-")

    return tuple(split)


def parse_roomtype(line: str) -> tuple:
    split = line.split(" - ", maxsplit=1)
    return tuple(split)


def parse_staff(line: str) -> tuple:
    split = line.split(" (CSM")

    try:
        split2 = split[0].split(", ")
        split[1] = split[1].strip("(-)")
    except:
        split = line.split(" (")
        split2 = split[0].split(", ")
        split[1] = split[1].strip("(-)")

    return split2[0], split2[1], split[1]


def parse_room(line: str):
    split = line.split(' ', 1)
    if("-0" in split[0]):
        return (split[0][:len(split[0]) - 2], split[1])
    else:
        return split


def parse_room_type(line: str):
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


def literal_intstr_to_0intstr(intstr: str):
    if intstr == "43A":
        return "043-A"
    if (len(intstr) == 3):
        return intstr
    elif (len(intstr) == 2):
        return "0" + intstr
    else:
        return "00" + intstr

def parse_action(line:str):
    split = line.split(",")
    return split


def reg_room_num_to_table_notation(room_num: str) -> str | list | None:
    if(room_num == "various"): return None
    if(room_num == "101-107"):
        return [f"10{i}" for i in range(1, 8)]
    if(room_num == "D8-10"):
        return [f"0D{i:02d}-00" for i in range(8, 11)]

    # extracts number and potential letters for a room
    match = re.fullmatch(r"(\d{1,3})([A-Za-z]?)([A-Za-z]?)", room_num.strip())
    number, letter1, letter2 = match.groups()

    # pads number with 0s
    number_padded = number.zfill(3)

    # if there is no letter, uses 0 instead to
    letter1 = letter1.upper() if letter1 else "0"

    letter2 = letter2.upper() if letter2 else "0"

    return f"0{number_padded}-{letter1}{letter2}"

def parse_contact(line: str) -> list[str]:
    split = line.split()
    return split

def floorplan_roomnum_to_table_notation(room_num: str) -> str | list | None:

    # extracts number and potential letters for a room
    match = re.fullmatch(r"([A-Za-z]?)(\d{1,3})([A-Za-z]?)", room_num.strip())
    letter1, number, letter2 = match.groups()

    # pads number with 0s
    number_padded = number.zfill(3)

    # if there is no letter, uses 0 instead to
    letter1 = letter1.upper() if letter1 else "0"

    letter2 = letter2.upper() if letter2 else "0"

    return f"0{number_padded}-{letter2}{letter1}"