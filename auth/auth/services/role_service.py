from typing import List

from loguru import logger

from auth.models import Role
from auth.repository.role import RepositoryRole
from auth.repository.user import RepositoryUser
from auth.schemas.role import RoleIn, RoleOut
from auth.utils import const, errors_const


class RoleService:
    def __init__(
        self,
        repository_role: RepositoryRole,
        repository_user: RepositoryUser,
    ):
        self._repository_role = repository_role
        self._repository_user = repository_user

    async def _get_role(self, role_id: str) -> Role:
        role = self._repository_role.get(id=role_id)
        if not role:
            logger.warning(f"Role not found with ID: {role_id}")
            raise ValueError(errors_const.ROLE_NOT_FOUND)
        return role

    async def _get_user(self, user_id: str):
        user = self._repository_user.get(id=user_id)
        if not user:
            logger.warning(f"User not found with ID: {user_id}")
            raise ValueError(errors_const.USER_NOT_FOUND)
        return user

    async def get(self, role_id: str) -> RoleOut:
        return RoleOut.parse_obj(await self._get_role(role_id))

    async def list(self) -> List[RoleOut]:
        roles = self._repository_role.list()
        if not roles:
            raise ValueError(errors_const.ROLES_NOT_FOUND)
        return roles

    async def delete(self, role_id: str) -> str:
        role = await self._get_role(role_id)
        logger.info(f"Role to delete: {role}")
        self._repository_role.delete(db_obj=role)
        return const.DELETED

    async def update(self, role_id: str, role_item: RoleIn):
        role = await self._get_role(role_id)
        logger.info(f"Role to update: {role}")
        return await self._repository_role.update(
            db_obj=role,
            obj_in={
                "role_name": role_item.role_name,
                "description": role_item.description,
                "permission_class": role_item.permission_class,
            },
        )

    async def add_role_to_user(self, user_id: str, role_id: str):
        role = await self._get_role(role_id)
        user = await self._get_user(user_id)
        return await self._repository_user.update(
            db_obj=user, obj_in={"user_role_id": role.id, "role": role}
        )

    async def create(self, role_item: RoleIn) -> RoleOut:
        role = self._repository_role.create(
            obj_in={
                "role_name": role_item.role_name,
                "description": role_item.description,
                "permission_class": role_item.permission_class,
            }
        )
        return RoleOut.parse_obj(role)
