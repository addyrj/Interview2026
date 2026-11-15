"""Pydantic v2 validation example: field rules, validators, nested models, errors."""
from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import (BaseModel, ConfigDict, EmailStr, Field, ValidationError,
                      field_validator, model_validator)


class Address(BaseModel):
    city: str = Field(min_length=2)  # city name
    pincode: Annotated[str, Field(pattern=r"^\d{6}$")]  # Indian 6-digit pincode


class SignupRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")  # clean + strict

    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(ge=18, le=120)
    password: str = Field(min_length=8)
    confirm_password: str
    role: Literal["user", "admin"] = "user"
    address: Address | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def title_case(cls, v: str) -> str:
        return v.title()  # normalise

    @field_validator("password")
    @classmethod
    def strong(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain a digit")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "SignupRequest":
        if self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        return self


def main() -> None:
    ok = SignupRequest(name="  asha rao ", email="asha@example.com", age="29",  # "29" -> 29 (lax mode)
                       password="secret123", confirm_password="secret123",
                       address={"city": "Pune", "pincode": "411001"})
    print(ok.name, ok.age, type(ok.age).__name__, ok.address.city)
    dumped = ok.model_dump(exclude={"password", "confirm_password"})
    print(dumped["role"], dumped["address"])
    print(ok.model_dump_json(exclude={"password", "confirm_password", "address"}))

    try:
        SignupRequest(name="A", email="bad", age=10, password="short", confirm_password="x",
                      address={"city": "P", "pincode": "12"}, extra_field=1)
    except ValidationError as e:
        print(e.error_count(), "errors")
        for err in e.errors():
            print(err["loc"], err["type"])

    try:
        SignupRequest(name="Ravi", email="r@example.com", age=30,
                      password="abcdefg1", confirm_password="abcdefg2")
    except ValidationError as e:
        print(e.errors()[0]["type"], "|", e.errors()[0]["msg"])

    # strict-ness: lax mode converts, model_validate_json parses raw JSON
    m = SignupRequest.model_validate_json(
        '{"name":"Zoya","email":"z@example.com","age":"41","password":"pass1234","confirm_password":"pass1234"}')
    print(m.age + 1)
    assert m.age == 41 and ok.name == "Asha Rao" and "password" not in dumped
    print("all ok")


if __name__ == "__main__":
    main()
