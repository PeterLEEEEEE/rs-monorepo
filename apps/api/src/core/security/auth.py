from enum import StrEnum


class Authority(StrEnum):
    
    ADMIN = ("ADMIN", "1", "admin authority")
    USER = ("USER", "2", "user authority")
    # ADMIN = ("ADMIN", "3", "admin authority")