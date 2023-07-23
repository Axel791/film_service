from loguru import logger

from auth.repository.role import RepositoryRole
from auth.repository.user import RepositoryUser

from auth.schemas.role import RoleOut, RoleIn


class RoleService:

    def __init__(
            self,
            repository_role: RepositoryRole,
            repository_user: RepositoryUser,
    ):
        self._repository_role = repository_role
        self._repository_user = repository_user

    async def get(self, role_id):
        role = self._repository_role.get(id=role_id)
        if role:
            logger.info(f"Role retrieved: {role}")
        else:
            logger.warning(f"Role not found with ID: {role_id}")
        return role

    async def list(self):
        roles = self._repository_role.list()
        logger.info(f"Roles retrieved: {roles}")
        return roles

    async def delete(self, role_id):
        role = self._repository_role.get(id=role_id)
        if role:
            logger.info(f"Role to delete: {role}")
            return self._repository_role.delete(db_obj=role)
        else:
            logger.warning(f"Role not found with ID: {role_id}")

    async def update(self, role_id, role_item: RoleIn):
        role = self._repository_role.get(id=role_id)
        if role:
            logger.info(f"Role to update: {role}")
            return self._repository_role.update(
                db_obj=role,
                obj_in={
                    "role_name": role_item.role_name,
                    "description": role_item.description,
                    "permission_class": role_item.permission_class
                }
            )
        else:
            logger.warning(f"Role not found with ID: {role_id}")

    async def add_role_to_user(self, user_id, role_id):
        role = self._repository_role.get(id=role_id)
        if not role:
            logger.warning(f"Role not found with ID: {role_id}")
            raise ValueError("Такой роли нет")

        user = self._repository_user.get(id=user_id)
        if user:
            logger.info(f"User to update with role: {user}")
            return self._repository_user.update(
                db_obj=user,
                obj_in={
                    "user_role_id": role.id,
                    "role": role
                }
            )
        else:
            logger.warning(f"User not found with ID: {user_id}")
