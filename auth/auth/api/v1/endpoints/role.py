from fastapi import APIRouter, Depends

from dependency_injector.wiring import inject, Provide

from typing import List

from auth.api.deps import commit_and_close_session
from auth.core.containers import Container
from auth.services.role_service import RoleService
from auth.schemas.role import RoleOut, RoleIn, RoleId
from auth.api.deps import filter_user_superuser, filter_user_moderator

router = APIRouter()


@router.post('/create_role', response_model=RoleIn)
@inject
@commit_and_close_session
async def create_role(
        role_item: RoleIn,
        user=Depends(filter_user_superuser),
        role_service: RoleService = Depends(Provide[Container.role_service])
):
    return await role_service.create(role_item=role_item)


@router.post('/update_role', response_model=RoleIn)
@inject
@commit_and_close_session
async def update_role(
        role_id: str,
        role_item: RoleIn,
        user=Depends(filter_user_superuser),
        role_service: RoleService = Depends(Provide[Container.role_service])
):
    return await role_service.update(
        role_id=role_id,
        role_item=role_item
    )


@router.get('/get_role')
@inject
@commit_and_close_session
async def get_role(
        role_id: str,
        user=Depends(filter_user_moderator),
        role_service: RoleService = Depends(Provide[Container.role_service])
) -> RoleOut:
    return await role_service.get(role_id=role_id)


@router.get('/list_roles')
@inject
@commit_and_close_session
async def list_role(
        user=Depends(filter_user_moderator),
        role_service: RoleService = Depends(Provide[Container.role_service])
) -> List[RoleOut]:
    return await role_service.list()


@router.post('/delete_role', response_model=RoleId)
@inject
@commit_and_close_session
async def delete_role(
        role_id: RoleId,
        user=Depends(filter_user_superuser),
        role_service: RoleService = Depends(Provide[Container.role_service])
) -> str:
    return await role_service.delete(role_id=role_id.role_id)


@router.post('/add_role_to_user', response_model=RoleId)
@inject
@commit_and_close_session
async def add_role_to_user(
        role_id: RoleId,
        user=Depends(filter_user_moderator),
        role_service: RoleService = Depends(Provide[Container.role_service])
) -> RoleOut:
    return await role_service.add_role_to_user(
        user_id=user.id,
        role_id=role_id.role_id
    )
