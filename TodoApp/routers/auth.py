from datetime import timedelta, datetime, timezone
from typing import Annotated

from starlette.responses import RedirectResponse

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..templates_config import templates

from ..database import SessionLocal
from ..models import Users

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# =========================
# CONFIG
# =========================

SECRET_KEY = "2bd17388c110f7f4fdc14980d2d73fdcea2cd271edcc6984ffe97c3149af52d0"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


# =========================
# DB
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# =========================
# MODELS
# =========================

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str


# =========================
# PAGES
# =========================

@router.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )


@router.get("/register-page")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request}
    )


# =========================
# HELPERS
# =========================

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(
        Users.username == username
    ).first()

    if not user:
        return None

    if not bcrypt_context.verify(password, user.hashed_password):
        return None

    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):

    payload = {
        "sub": username,
        "id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + expires_delta
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# CURRENT USER
# =========================

async def get_current_user(token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return {
            "username": payload.get("sub"),
            "user_id": payload.get("id"),
            "role": payload.get("role")
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_user_from_cookie(request: Request):

    token = request.cookies.get("access_token")

    if not token:
        return None

    token = token.replace("Bearer ", "")
    return await get_current_user(token)


# =========================
# ENDPOINTS
# =========================

@router.post("/", status_code=201)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):

    existing = db.query(Users).filter(
        Users.username == create_user_request.username
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True,
        phone_number=create_user_request.phone_number
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created successfully"}


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency,
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(minutes=20)
    )

    response = RedirectResponse(
        url="/todos/todo-page",
        status_code=302
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax"
    )

    return response