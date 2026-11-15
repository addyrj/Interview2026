"""Build CSV Import/Export (pip install python-multipart): validated import with row errors + streaming export. Run: python main.py"""
from __future__ import annotations

import csv
import io
from typing import Iterator

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError, field_validator

app = FastAPI()
DB: list[dict] = []


class UserRow(BaseModel):
    name: str
    email: str
    age: int

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("invalid email")
        return v.lower().strip()


def import_csv(text: str) -> tuple[list[UserRow], list[dict]]:
    good: list[UserRow] = []
    errors: list[dict] = []
    reader = csv.DictReader(io.StringIO(text, newline=""))  # header row -> dict keys
    for line_no, row in enumerate(reader, start=2):  # line 1 is the header
        try:
            good.append(UserRow(**row))
        except (ValidationError, TypeError) as exc:
            msg = "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in exc.errors()) if isinstance(exc, ValidationError) else str(exc)
            errors.append({"line": line_no, "error": msg})  # report the line so users can fix the file
    return good, errors


def export_csv(rows: list[dict]) -> Iterator[str]:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["name", "email", "age"])
    writer.writeheader()
    yield buf.getvalue()  # header chunk
    for r in rows:
        buf.seek(0); buf.truncate()  # reuse the buffer: constant memory
        writer.writerow(r)
        yield buf.getvalue()


@app.post("/import")
async def import_endpoint(file: UploadFile = File(...)) -> dict:
    text = (await file.read()).decode("utf-8-sig")  # utf-8-sig strips Excel's BOM
    good, errors = import_csv(text)
    DB.extend(u.model_dump() for u in good)
    return {"imported": len(good), "errors": errors}


@app.get("/export")
def export_endpoint() -> StreamingResponse:
    return StreamingResponse(export_csv(DB), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=users.csv"})


if __name__ == "__main__":
    data = 'name,email,age\nAsha,ASHA@x.com,30\nRavi,bad-email,25\nZoya,z@x.com,abc\n"Lee, Jr",lee@x.com,40\n'
    c = TestClient(app)
    r = c.post("/import", files={"file": ("u.csv", data.encode(), "text/csv")})
    print(r.json())
    assert r.json()["imported"] == 2 and len(r.json()["errors"]) == 2
    out = c.get("/export")
    print(out.text)
    assert '"Lee, Jr"' in out.text  # csv module quoted the comma
    print("all ok")
