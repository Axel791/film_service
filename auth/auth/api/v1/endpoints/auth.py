from fastapi import APIRouter, Depends
from auth.schemas import Token, UserCreate, UserInDB
from auth.services import AuthService

router = APIRouter()
auth_service = AuthService()

@router.post("/register", response_model=UserInDB)
def register(user_data: UserCreate) -> UserInDB:
    user = auth_service.create_user(user_data)
    return user

@router.post("/login", response_model=Token)
def login(username: str, password: str) -> Token:
    user = auth_service.authenticate_user(username, password)
    access_token = auth_service.create_access_token(user)
    return access_token

@router.get("/user/me", response_model=UserInDB)
def get_current_user(current_user: UserInDB = Depends(auth_service.get_current_user)):
    return current_user
