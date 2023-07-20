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
        return self._repository_role.get(id=role_id)

    async def list(self):
        return self._repository_role.list()

    async def delete(self, role_id):
        return self._repository_role.delete(
            db_obj=self._repository_role.get(id=role_id)
        )

    async def update(self, role_id, role_item: RoleIn):
        return self._repository_role.update(
            db_obj=self._repository_role.get(id=role_id),
            obj_in={
                "role_name": role_item.role_name,
                "description": role_item.description,
                "permission_class": role_item.permission_class
            }
        )

    async def add_role_to_user(self, user_id, role_id):
        role = self._repository_role.get(id=role_id)
        if not role:
            raise ValueError("Такой роли нет")
        return self._repository_user.update(
            db_obj=self._repository_user.get(id=user_id),
            obj_in={
                "user_role_id": role.id,
                "role": role
            }
        )