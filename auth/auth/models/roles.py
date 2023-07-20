import uuid
import enum

from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID

from auth.db.base_class import Base


class Permissions(enum.Enum):
    """
    Степени доступа и разрешения в приложении.
    """
    ALL = 1
    MEDIUM = 2
    SOME = 3
    NOT_ALL = 4


class Role(Base):
    __tablename__ = 'role'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    role_name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    permission_class = Column(
        Enum(Permissions),
        default=Permissions.NOT_ALL
    )

    def __str__(self):
        return self.role_name
