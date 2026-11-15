import os

from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel

app = FastAPI(title="items-api")

# In-memory demo store (a warm Lambda reuses it; real data belongs in DynamoDB/RDS)
ITEMS: dict[int, dict] = {}


class Item(BaseModel):
    name: str
    price: float


@app.get("/health")
def health():
    return {"status": "ok", "stage": os.environ.get("STAGE", "dev")}


@app.post("/items", status_code=201)
def create_item(item: Item):
    item_id = len(ITEMS) + 1
    ITEMS[item_id] = item.model_dump()
    return {"id": item_id, **ITEMS[item_id]}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": item_id, **ITEMS[item_id]}


# Lambda entry point: Mangum adapts API Gateway events to ASGI.
# lifespan="off" avoids startup/shutdown event issues on Lambda.
handler = Mangum(app, lifespan="off")
