from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from loguru import logger
from starlette.requests import Request

from auth.api.deps import commit_and_close_session
from auth.core.commons import PaginateQueryParams
from auth.core.config import settings
from auth.core.containers import Container
from auth.schemas.login_event import LoginEvent
from auth.schemas.token import Token
from auth.schemas.user import RegUserIn

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CID,
    client_secret=settings.GOOGLE_SECRET,
    server_metadata_url=settings.GOOGLE_DISCOVERY_URL,
    client_kwargs={"scope": "openid email profile"},
)

router = APIRouter()


@router.post("/login", response_model=Token)
@inject
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service=Depends(Provide[Container.auth_service]),
):
    logger.info("Received login request for user: %s", form_data.username)
    return await auth_service.login(form_data=form_data)


@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = "http://localhost"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/login/callback")
async def login_callback(
        request: Request, auth_service=Depends(Provide[Container.auth_service])
):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    access_token = auth_service.create_access_token(user.login)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/registration")
@inject
@commit_and_close_session
async def registration(
        user: RegUserIn, auth_service=Depends(Provide[Container.auth_service])
):
    logger.info("Received registration request for user: %s", user.login)
    return await auth_service.registration(user=user)


@router.post("/refresh", response_model=Token)
@inject
async def refresh(
        access_token: Token,
        redis=Depends(Provide[Container.redis]),
        auth_service=Depends(Provide[Container.auth_service]),
):
    logger.info("Received refresh token request")
    return await auth_service.refresh_access_token(redis, access_token)


@router.post("/get_login_history", response_model=LoginEvent)
@inject
async def get_login_history(
        commons: Annotated[PaginateQueryParams, Depends(PaginateQueryParams)],
        user_login: str,
        auth_service=Depends(Provide[Container.auth_service]),
):
    logger.info("Received request to get login history for user: %s", user_login)
    return await auth_service.get_login_history(
        user_login, page=commons.page, page_size=commons.page_size
    )
