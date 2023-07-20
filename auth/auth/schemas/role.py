from pydantic import BaseModel, validator

from auth.models.roles import Permissions


class RoleOut(BaseModel):
    role_name: str | None
    description: str | None
    permission_class: Permissions | None


class RoleIn(RoleOut):

    @validator("permission_class", allow_reuse=True)
    def validate_permission(self, v):
        if v not in [
            Permissions.NOT_ALL,
            Permissions.SOME,
            Permissions.MEDIUM,
            Permissions.ALL
        ]:
            raise ValueError("Такого статуса доступа нет")

        return v
