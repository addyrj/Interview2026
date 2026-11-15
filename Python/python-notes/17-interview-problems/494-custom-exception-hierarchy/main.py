"""Custom Exception Hierarchy: base error, codes, chaining, FastAPI handler."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


class AppError(Exception):
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str = "", **details: object) -> None:
        super().__init__(message or self.code)
        self.message = message or self.code
        self.details = details

    def to_dict(self) -> dict:
        return {"error": {"code": self.code, "message": self.message, "details": self.details}}


class NotFoundError(AppError):
    status_code, code = 404, "not_found"


class ValidationFailed(AppError):
    status_code, code = 422, "validation_failed"


class PaymentError(AppError):
    status_code, code = 402, "payment_error"


class InsufficientFunds(PaymentError):  # deeper level: catchable as PaymentError or AppError
    code = "insufficient_funds"


class DatabaseError(AppError):
    code = "database_error"


app = FastAPI()


@app.exception_handler(AppError)  # one handler covers the whole hierarchy
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@app.get("/users/{uid}")
def get_user(uid: int) -> dict:
    if uid != 1:
        raise NotFoundError("user not found", user_id=uid)
    return {"id": 1}


@app.post("/pay/{amount}")
def pay(amount: int) -> dict:
    try:
        balance = {"a": 100}["a"]
        if amount > balance:
            raise InsufficientFunds("balance too low", balance=balance, needed=amount)
        return {"ok": True}
    except KeyError as e:  # wrap low-level errors, keep the cause
        raise DatabaseError("lookup failed") from e


if __name__ == "__main__":
    print([c.__name__ for c in InsufficientFunds.__mro__])
    c = TestClient(app)
    r = c.get("/users/9"); print(r.status_code, r.json())
    r2 = c.post("/pay/500"); print(r2.status_code, r2.json())
    assert r.status_code == 404 and r2.json()["error"]["code"] == "insufficient_funds"
    try:
        try:
            {}["x"]
        except KeyError as e:
            raise DatabaseError("db down") from e
    except AppError as e:
        print(type(e).__name__, "caused by", repr(e.__cause__))
    assert issubclass(InsufficientFunds, AppError) and not issubclass(NotFoundError, PaymentError)
    print("all ok")
