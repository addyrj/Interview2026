# File Upload API: validate type/size by streaming in chunks, safe filenames, download, delete
import hashlib
import tempfile
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.testclient import TestClient

UPLOAD_DIR = Path(tempfile.mkdtemp(prefix="uploads_"))   # use a real volume/S3 in prod
MAX_BYTES = 1024 * 1024                                  # 1 MB limit
CHUNK = 64 * 1024                                        # read 64 KB at a time
ALLOWED = {"image/png": ".png", "image/jpeg": ".jpg", "application/pdf": ".pdf"}
MAGIC = {b"\x89PNG": "image/png", b"\xff\xd8\xff": "image/jpeg", b"%PDF": "application/pdf"}

app = FastAPI()


def sniff(head: bytes) -> str | None:             # trust file bytes, not the client header
    for magic, mime in MAGIC.items():
        if head.startswith(magic):
            return mime
    return None


@app.post("/upload", status_code=201)
async def upload(file: Annotated[UploadFile, File()]) -> dict[str, str | int]:
    if file.content_type not in ALLOWED:
        raise HTTPException(415, f"Unsupported type {file.content_type}")
    file_id = uuid.uuid4().hex                     # never use the client filename on disk
    dest = UPLOAD_DIR / f"{file_id}{ALLOWED[file.content_type]}"
    size, sha, first = 0, hashlib.sha256(), b""
    try:
        with dest.open("wb") as out:
            while chunk := await file.read(CHUNK): # stream: constant memory
                if not first:
                    first = chunk[:8]
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(413, "File too large")
                sha.update(chunk)
                out.write(chunk)
        if sniff(first) != file.content_type:      # header lied about the type
            raise HTTPException(400, "Content does not match declared type")
    except HTTPException:
        dest.unlink(missing_ok=True)               # remove partial file
        raise
    return {"id": file_id, "size": size, "sha256": sha.hexdigest(), "original_name": Path(file.filename or "").name}


def _find(file_id: str) -> Path:
    if not file_id.isalnum():                      # blocks ../ path traversal
        raise HTTPException(400, "Bad id")
    for p in UPLOAD_DIR.glob(f"{file_id}.*"):
        return p
    raise HTTPException(404, "Not found")


@app.get("/files/{file_id}")
def download(file_id: str) -> FileResponse:
    return FileResponse(_find(file_id))


@app.delete("/files/{file_id}", status_code=204)
def remove(file_id: str) -> None:
    _find(file_id).unlink()


if __name__ == "__main__":
    c = TestClient(app)
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 100
    r = c.post("/upload", files={"file": ("../../evil.png", png, "image/png")})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["size"] == len(png) and body["original_name"] == "evil.png"
    assert body["sha256"] == hashlib.sha256(png).hexdigest()
    assert c.get(f"/files/{body['id']}").content == png
    assert c.post("/upload", files={"file": ("a.txt", b"hi", "text/plain")}).status_code == 415
    assert c.post("/upload", files={"file": ("a.png", b"not a png", "image/png")}).status_code == 400
    big = b"\x89PNG" + b"0" * (MAX_BYTES + 10)
    assert c.post("/upload", files={"file": ("b.png", big, "image/png")}).status_code == 413
    assert len(list(UPLOAD_DIR.iterdir())) == 1    # failed uploads left no partial files
    assert c.get("/files/..%2Fetc").status_code in (400, 404)
    assert c.delete(f"/files/{body['id']}").status_code == 204
    assert c.get(f"/files/{body['id']}").status_code == 404
    import shutil; shutil.rmtree(UPLOAD_DIR)
    print("all upload tests passed")
