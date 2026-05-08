from sqlalchemy import Enum
import enum

class UserRole(str, enum.Enum):
    """
    Python enum for roles.
    Inheriting str means the value is stored as a plain string in the DB.
    So the DB column stores "user" or "admin", not an integer code.
    """
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class AssignableRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
