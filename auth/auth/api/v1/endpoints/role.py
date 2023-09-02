import sys
from typing import List

from fastapi import APIRouter, Depends
from loguru import logger
from starlette.requests import Request

from dependency_injector.wiring import inject, Provide

from auth.api.deps import commit_and_close_session
from auth.core.containers import Container
from auth.services.role_service import RoleService
from auth.schemas.role import RoleOut, RoleIn, RoleId
from auth.api.deps import filter_user_superuser, filter_user_moderator

logger.add(
    "/var/log/auth/access-log.json",
    rotation="500 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

router = APIRouter()


def get_x_request_id(request: Request):
    return request.headers.get("X-Request-Id", "N/A")


@router.post("/create_role", response_model=RoleIn)
@inject
@commit_and_close_session
async def create_role(
    request: Request,
    role_item: RoleIn,
    user=Depends(filter_user_superuser),
    role_service: RoleService = Depends(Provide[Container.role_service]),
):
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Received create_role request")
    return await role_service.create(role_item=role_item)


@router.post("/update_role", response_model=RoleIn)
@inject
@commit_and_close_session
async def update_role(
    request: Request,
    role_id: str,
    role_item: RoleIn,
    user=Depends(filter_user_superuser),
    role_service: RoleService = Depends(Provide[Container.role_service]),
):
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Received update_role request")
    return await role_service.update(role_id=role_id, role_item=role_item)


@router.get("/get_role")
@inject
@commit_and_close_session
async def get_role(
    request: Request,
    role_id: str,
    user=Depends(filter_user_moderator),
    role_service: RoleService = Depends(Provide[Container.role_service]),
) -> RoleOut:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Received get_role request")
    return await role_service.get(role_id=role_id)


@router.get("/list_roles")
@inject
@commit_and_close_session
async def list_role(
    request: Request,
    user=Depends(filter_user_moderator),
    role_service: RoleService = Depends(Provide[Container.role_service]),
) -> List[RoleOut]:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Received list_roles request")
    return await role_service.list()


@router.post("/delete_role", response_model=RoleId)
@inject
@commit_and_close_session
async def delete_role(
    request: Request,
    role_id: RoleId,
    user=Depends(filter_user_superuser),
    role_service: RoleService = Depends(Provide[Container.role_service]),
) -> str:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Received delete_role request")
    return await role_service.delete(role_id=role_id.role_id)


@router.post("/add_role_to_user", response_model=RoleId)
@inject
@commit_and_close_session
async def add_role_to_user(
    request: Request,
    role_id: RoleId,
    user=Depends(filter_user_moderator),
    role_service: RoleService = Depends(Provide[Container.role_service]),
) -> RoleOut:
    x_request_id = get_x_request_id(request)
    logger.bind(x_request_id=x_request_id).info("Received add_role_to_user request")
    return await role_service.add_role_to_user(user_id=user.id, role_id=role_id.role_id)
