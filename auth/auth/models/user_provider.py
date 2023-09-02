import json
import uuid

from sqlalchemy import JSON, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from auth.db.base_class import Base


class UserProvider(Base):
    __tablename__ = "user_providers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    provider_name = Column(String, nullable=False)
    provider_user_id = Column(String, nullable=False)
    provider_data = Column(JSON)

    user = relationship("User", back_populates="providers")

    def set_provider_data(self, data: dict):
        self.provider_data = json.dumps(data)

    def get_provider_data(self) -> dict:
        if self.provider_data is not None:
            return json.loads(self.provider_data)
        return {}
