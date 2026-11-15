# Auth system: register, login (OAuth2 password flow), JWT access token, protected routes, roles
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt                                        # PyJWT
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from pwdlib import PasswordHash                   # modern password hashing (Argon2)
from pydantic import BaseModel, Field

SECRET_KEY = os.getenv("JWT_SECRET", "dev-only-change-me-32-bytes-minimum!!")   # env in prod
ALGORITHM = "HS256"
ACCESS_MINUTES = 15

pwd = PasswordHash.recommended()                  # Argon2id
oauth2 = OAuth2PasswordBearer(tokenUrl="/login")  # reads "Authorization: Bearer <token>"
app = FastAPI()

USERS: dict[str, dict[str, str]] = {}             # username -> {hash, role}; use a DB in prod


class Register(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    username: str
    role: str


def create_token(sub: str, minutes: int = ACCESS_MINUTES) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": sub, "iat": now, "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def current_user(token: Annotated[str, Depends(oauth2)]) -> UserOut:
    err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token",
                        headers={"WWW-Authenticate": "Bearer"})
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])   # verifies signature + exp
    except jwt.PyJWTError:
        raise err
    user = USERS.get(data.get("sub", ""))
    if user is None:
        raise err
    return UserOut(username=data["sub"], role=user["role"])


def require_admin(user: Annotated[UserOut, Depends(current_user)]) -> UserOut:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admins only")
    return user


@app.post("/register", response_model=UserOut, status_code=201)
def register(body: Register) -> UserOut:
    if body.username in USERS:
        raise HTTPException(409, "Username taken")
    role = "admin" if not USERS else "user"       # first user is admin (demo only)
    USERS[body.username] = {"hash": pwd.hash(body.password), "role": role}
    return UserOut(username=body.username, role=role)


@app.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = USERS.get(form.username)
    # same error for unknown user and bad password: no username enumeration
    if user is None or not pwd.verify(form.password, user["hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")
    return Token(access_token=create_token(form.username))


@app.get("/me", response_model=UserOut)
def me(user: Annotated[UserOut, Depends(current_user)]) -> UserOut:
    return user


@app.get("/admin/stats")
def stats(_: Annotated[UserOut, Depends(require_admin)]) -> dict[str, int]:
    return {"users": len(USERS)}


if __name__ == "__main__":
    c = TestClient(app)
    assert c.post("/register", json={"username": "root", "password": "supersecret"}).json()["role"] == "admin"
    assert c.post("/register", json={"username": "bob", "password": "password123"}).json()["role"] == "user"
    assert c.post("/register", json={"username": "bob", "password": "password123"}).status_code == 409
    assert c.get("/me").status_code == 401                                   # no token
    assert c.post("/login", data={"username": "bob", "password": "wrongpass1"}).status_code == 401
    tok = c.post("/login", data={"username": "bob", "password": "password123"}).json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    assert c.get("/me", headers=h).json() == {"username": "bob", "role": "user"}
    assert c.get("/admin/stats", headers=h).status_code == 403               # wrong role
    atok = c.post("/login", data={"username": "root", "password": "supersecret"}).json()["access_token"]
    assert c.get("/admin/stats", headers={"Authorization": f"Bearer {atok}"}).json() == {"users": 2}
    expired = create_token("bob", minutes=-1)
    assert c.get("/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    tampered = tok[:-2] + ("AA" if tok[-2:] != "AA" else "BB")
    assert c.get("/me", headers={"Authorization": f"Bearer {tampered}"}).status_code == 401
    print("all auth tests passed")
