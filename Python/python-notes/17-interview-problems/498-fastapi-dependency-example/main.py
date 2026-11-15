"""FastAPI Depends example: sub-dependencies, yield cleanup, auth, class deps, overrides."""
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.testclient import TestClient

app = FastAPI()
events: list[str] = []  # records lifecycle for the demo


class FakeDB:
    def __init__(self) -> None:
        self.users = {"t-asha": {"id": 1, "name": "Asha", "role": "admin"},
                      "t-ravi": {"id": 2, "name": "Ravi", "role": "user"}}


def get_db() -> Iterator[FakeDB]:
    events.append("open db")
    db = FakeDB()
    try:
        yield db  # handler runs here
    finally:
        events.append("close db")  # always runs


DB = Annotated[FakeDB, Depends(get_db)]


def current_user(db: DB, x_token: Annotated[str | None, Header()] = None) -> dict:
    if x_token is None or x_token not in db.users:
        raise HTTPException(status_code=401, detail="invalid token")
    return db.users[x_token]


User = Annotated[dict, Depends(current_user)]


def require_admin(user: User) -> dict:  # sub-dependency of a sub-dependency
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    return user


class Pagination:  # class as dependency
    def __init__(self, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> None:
        self.offset = (page - 1) * size
        self.size = size


@app.get("/me")
def me(user: User) -> dict:
    return user


@app.get("/admin/stats")
def stats(admin: Annotated[dict, Depends(require_admin)]) -> dict:
    return {"by": admin["name"]}


@app.get("/items")
def items(p: Annotated[Pagination, Depends()]) -> dict:
    return {"offset": p.offset, "size": p.size}


def main() -> None:
    c = TestClient(app)
    print(c.get("/me").status_code, c.get("/me").json())
    print(c.get("/me", headers={"x-token": "t-asha"}).json())
    print(c.get("/admin/stats", headers={"x-token": "t-ravi"}).json())
    print(c.get("/admin/stats", headers={"x-token": "t-asha"}).json())
    print(c.get("/items?page=3&size=20").json(), c.get("/items?page=0").status_code)
    print(events[:2], len(events))

    class StubDB(FakeDB):  # test override
        def __init__(self) -> None:
            self.users = {"t-x": {"id": 9, "name": "Stub", "role": "admin"}}
    app.dependency_overrides[get_db] = lambda: StubDB()
    print(c.get("/me", headers={"x-token": "t-x"}).json())
    app.dependency_overrides.clear()
    assert c.get("/me", headers={"x-token": "t-x"}).status_code == 401
    assert events.count("open db") == events.count("close db")
    print("all ok")


if __name__ == "__main__":
    main()
