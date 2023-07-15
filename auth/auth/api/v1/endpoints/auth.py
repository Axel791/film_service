from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from auth.api.deps import commit_and_close_session, get_current_user
from dependency_injector.wiring import inject, Provide
from auth.core.containers import Container
from auth.schemas.auth import Token, UserInDB


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


@router.post('/profile', response_model=MyProfileOut)
@inject
async def my_profile(
    #! Сюда нужно вставить функцию получения айди по тому какой пользователь обращается
        # user_id: str = Depends(get_current_user_auth),
        registration_service=Depends(Provide[Container.registration_service])):
    """Личный кабинет."""
    return registration_service.my_profile(user_id="ID")


@router.post
@inject
async def get_post():
    return {"Hello world": "Hello world!"}


@router.app
@inject
async def get_user(user=Depends(get_current_user)):
    if get_current_user is None:
        raise ValueError("Нет нужного пользователя.")
    return get_current_user.id