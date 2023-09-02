from pydantic import BaseModel, validator

from auth.models.roles import Permissions
from auth.utils import errors_const


class RoleOut(BaseModel):
    role_name: str | None
    description: str | None
    permission_class: Permissions | None


class RoleIn(RoleOut):
    @validator("role_name", "description", allow_reuse=True)
    def validate_fields(cls, v):
        if not v:
            raise ValueError(errors_const.THE_FIELD_CANNOT_BE_EMPTY)
        return v

    # @validator("permission_class", allow_reuse=True)
    def validate_permission(self, v):
        if v not in [
            Permissions.NOT_ALL,
            Permissions.SOME,
            Permissions.MEDIUM,
            Permissions.ALL,
        ]:
            raise ValueError(errors_const.NO_SUCH_ACCESS_STATUS)
        return v


class RoleId(BaseModel):
    role_id: str
