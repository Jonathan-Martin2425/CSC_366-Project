# Pathfinder Project

## Overview
This project is a Python-based API system for managing and querying room, department, employee, and equipment data for Cal Poly's buildings. It connects to a MySQL database and provides a set of API functions for retrieving and managing this data with role-based access control.

## Prerequisites
- Python 3.9
- MySQL Connector for Python
- Access to the project's MySQL database server

Install the MySQL connector via pip:
```bash
pip install mysql-connector-python
```

## Setup
1. Clone or download all files from the repository into your Python IDE or working directory.
2. Create a `settings.config` file in the same directory with your database credentials in the following format:
```
[database]
host = your_host
user = your_username
password = your_password
database = your_database_name
```

## File Structure
- **`connector.py`** — contains the `make_connection()` function used to connect to the database server. All API files depend on this.
- **`permissions.py`** — contains the `check_permission()` function used to handle role-based access control. All API files depend on this.
- **`wal_api.py`** — contains functions for handling write-ahead log records.
- **`*_api.py`** — each file contains API call functions covering a specific area of the system (e.g. `rooms_api.py` covers room-related API calls). These files automatically import and use `connector.py`, `permissions.py`, and `wal_api.py` as needed — you do not need to call these separately.
- **`test_harness.py` / `test_harness_client.py`** — contains test cases for all API functions. These are the main files to run to see the system in action.
- **`output.txt`** — the test harness writes all output to this file. Check here after running the test harness to see results.

## Running the Project
Once your `settings.config` file is in place, simply run either test harness file:
```bash
python test_harness.py
```
or
```bash
python test_harness_client.py
```
Output will be written to `output.txt` in the same directory.

## Notes
- You do not need to run `connector.py`, `permissions.py`, or `wal_api.py` directly — they are automatically used by the API files.
- You do not need to run any `*_api.py` files directly — the test harness handles all API calls.
- Make sure `settings.config` is in the same directory as all other files, otherwise the database connection will fail.
