"""
models/user.py
Defines the User model representing the 'users' table.
Auth-ready from day one — unused in V1 UI.
Passwords are never stored in plain text — only bcrypt hashes.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database import Base


class User(Base):
    tablename = "users"

    id            = Column(Integer,      primary_key=True, index=True)
    username      = Column(String(50),   unique=True, nullable=False, index=True)
    email         = Column(String(255),  unique=True, nullable=False, index=True)
    password_hash = Column(String(255),  nullable=False)
    role          = Column(String(20),   nullable=False, default="user")  # "admin" | "user"
    is_active     = Column(Boolean,      nullable=False, default=True)
    created_at    = Column(DateTime,     server_default=func.now(), nullable=False)

    def __repr__(self):
        return (
            f"<User("
            f"username='{self.username}', "
            f"email='{self.email}', "
            f"role='{self.role}'"
            f")>"
        )