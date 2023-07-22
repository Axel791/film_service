from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from auth.api.deps import commit_and_close_session
from dependency_injector.wiring import inject, Provide
from auth.core.containers import Container
from auth.schemas.user import RegUserIn
from auth.schemas.token import Token
from auth.schemas.login_event import LoginEvent

router = APIRouter()


@router.post('/login', response_model=Token)
@inject
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service=Depends(Provide[Container.auth_service])
):
    return await auth_service.login(form_data=form_data)


@router.post('/registration')
@inject
@commit_and_close_session
async def registration(
        user: RegUserIn,
        auth_service=Depends(Provide[Container.auth_service])
):
    return await auth_service.registration(user=user)


@router.post('/refresh', response_model=Token)
@inject
async def refresh(
        access_token: Token,
        redis=Depends(Provide[Container.redis]),
        auth_service=Depends(Provide[Container.auth_service])
):
    return await auth_service.refresh_access_token(redis, access_token)


@router.post('/get_login_history', response_model=LoginEvent)
@inject
async def get_login_history(
        user_login: str,
        auth_service=Depends(Provide[Container.auth_service])
):
    return await auth_service.get_login_history(user_login)
