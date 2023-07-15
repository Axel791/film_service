db = SessionLocal()
redis_client = Redis(host='localhost', port=6379, password='your_redis_password')
auth_service = AuthService(db, redis_client)



@router.post("/register", response_model=UserInDB)
def register(user_data: UserCreate) -> UserInDB:
    user = auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
def login(username: str, password: str) -> Token:
    user = auth_service.authenticate_user(username, password)
    access_token = auth_service.create_access_token(user)

    # Store the access token in Redis
    redis_client.set(username, access_token.access_token)

    return access_token



@router.post("/refresh-token", response_model=Token)
def refresh_token(refresh_token: str) -> Token:
    user = auth_service.verify_refresh_token(refresh_token)
    access_token = auth_service.create_access_token(user)

    # Store the new access token in Redis
    redis_client.set(user.username, access_token.access_token)

    return access_token