SUCCESS = 0
ERR_UNAUTHORIZED = 1
ERR_DUPLICATE = 2
ERR_CONSTRAINT = 3
ERR_TYPE = 4
ERR_LOGGING = 5
ERR_NOT_FOUND = 6
ERR_UNKNOWN = 7
ERR_PERMISSION = 8

ERROR_MESSAGES = {
    SUCCESS: "Success",
    ERR_UNAUTHORIZED: "Unauthorized user",
    ERR_DUPLICATE: "Duplicate record exists",
    ERR_CONSTRAINT: "Foreign key constraint violation",
    ERR_TYPE: "Invalid data type",
    ERR_LOGGING: "Logging failure",
    ERR_NOT_FOUND: "Record not found",
    ERR_UNKNOWN: "Unknown error occurred",
    ERR_PERMISSION: "Incorrect permission level"
}