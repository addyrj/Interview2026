---

# 303. Pydantic Models — Complete Guide
# हिंदी में: Pydantic Models — पूरी Guide

---

## 🔵 Simple Definition (English)
Pydantic is a data validation library that uses Python type annotations to validate, serialize, and document data. You define a `BaseModel` class with typed fields — Pydantic automatically validates input data, converts types, and raises clear errors. FastAPI uses Pydantic for all request/response bodies.

## 🔵 सरल परिभाषा (Hindi)
Pydantic एक data validation library है जो Python type annotations से data validate, serialize, और document करती है। आप `BaseModel` class type fields के साथ define करते हो — Pydantic automatically input data validate करती है, types convert करती है, और clear errors raise करती है। FastAPI सभी request/response bodies के लिए Pydantic use करता है।

---

## 🔴 Problem it Solves
Without Pydantic: manually validate every field (`if not isinstance(age, int): raise ValueError...`), manually convert types (`age = int(request.json["age"])`), manually generate JSON schema for docs, write repetitive boilerplate for every model. Pydantic eliminates all of this.

## 🔴 यह क्यों बना? (Hindi)
Pydantic के बिना: हर field manually validate करो, types manually convert करो, JSON schema manually generate करो। Pydantic सब automatically करती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a class that inherits from BaseModel with typed fields
Step 2 → Create instance: MyModel(field1=value1, field2=value2)
Step 3 → Pydantic coerces types (str "42" → int 42 if field is int)
Step 4 → Validators run (built-in + custom)
Step 5 → If validation fails → ValidationError with detailed error list
Step 6 → On success → immutable (v2) or mutable (v1) model instance
Step 7 → Call .model_dump() (v2) or .dict() (v1) to serialize to dict/JSON
```

---

## 🟡 Real World Example
User registration at Zepto: frontend sends `{"email": "user@zepto.com", "age": "25", "phone": "+919876543210"}`. Pydantic validates email format, coerces `"25"` to int, validates phone regex, ensures required fields are present — all with one class definition and zero manual validation code.

## 🟡 Real Example Hindi mein
Zepto user registration: frontend `{"email": "user@zepto.com", "age": "25"}` भेजता है। Pydantic email format validate करती है, `"25"` को int में convert करती है, required fields check करती है — एक class definition से, zero manual validation code से।

---

## 💻 Code Example — Basic
```python
# Pydantic v2 (current — default from pydantic 2.0+)
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str                        # required, must be string
    email: EmailStr                  # validates email format (needs 'email-validator' package)
    age: int = Field(ge=18, le=120)  # int, ≥18 and ≤120
    phone: Optional[str] = None      # optional, defaults to None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Valid data:
user = UserCreate(name="Priya", email="priya@zepto.com", age=25)
print(user.name)            # "Priya"
print(user.age)             # 25
print(user.phone)           # None
print(user.model_dump())    # {'name': 'Priya', 'email': 'priya@zepto.com', ...}
print(user.model_dump_json())  # '{"name":"Priya",...}' (JSON string)

# Type coercion — Pydantic v2 is stricter:
user2 = UserCreate(name="Raj", email="raj@example.com", age="30")  # "30" → 30 (coerced)
print(user2.age)  # 30 (int, not "30")

# Validation error — clear, structured:
try:
    bad_user = UserCreate(name="", email="not-an-email", age=15)
except Exception as e:
    print(type(e).__name__)  # ValidationError
    print(e)                 # lists all errors: email invalid, age < 18

# Access validation errors programmatically:
from pydantic import ValidationError
try:
    UserCreate(name="x", email="bad", age=15)
except ValidationError as e:
    errors = e.errors()   # list of dicts with loc, msg, type
    print(errors[0])      # {'type': 'value_error', 'loc': ('email',), 'msg': '...', ...}
    print(e.error_count()) # 2
```

## 💻 Code Example — Advanced
```python
# Custom validators + nested models + model config
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Annotated, Literal
import re

# Type aliases with Annotated:
PositiveInt = Annotated[int, Field(gt=0)]
ShortStr    = Annotated[str, Field(min_length=1, max_length=100)]

class Address(BaseModel):
    street: ShortStr
    city: ShortStr
    pincode: str

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v: str) -> str:
        """field_validator: runs on a single field."""
        if not re.match(r"^\d{6}$", v):
            raise ValueError("Pincode must be exactly 6 digits")
        return v                    # return the value (possibly transformed)

class OrderItem(BaseModel):
    product_id: PositiveInt
    quantity: PositiveInt
    unit_price: float = Field(gt=0)

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price

class Order(BaseModel):
    model_config = ConfigDict(
        frozen=True,              # makes instances immutable (hashable)
        str_strip_whitespace=True,# strips whitespace from all str fields
        extra="forbid",           # raises error for unknown fields
        populate_by_name=True,    # allow both alias and field name
    )

    order_id: str = Field(alias="orderId")   # JSON sends camelCase, model uses snake_case
    items: list[OrderItem] = Field(min_length=1)
    delivery_address: Address
    status: Literal["pending", "confirmed", "shipped", "delivered"] = "pending"

    @model_validator(mode="after")
    def validate_order(self) -> "Order":
        """model_validator: runs after all fields are set, has access to all fields."""
        total = sum(item.subtotal for item in self.items)
        if total > 100_000:
            raise ValueError(f"Order total ₹{total:.2f} exceeds limit")
        return self

# FastAPI response model with field exclusion:
from pydantic import model_serializer

class UserDB(BaseModel):
    id: int
    name: str
    email: str
    hashed_password: str   # never expose!

    def model_dump(self, **kwargs):
        """Override to always exclude hashed_password."""
        kwargs.setdefault("exclude", set())
        kwargs["exclude"].add("hashed_password")
        return super().model_dump(**kwargs)

class UserResponse(BaseModel):
    """Separate response model (cleaner than exclude)."""
    id: int
    name: str
    email: str
    # hashed_password intentionally omitted

# Convert from DB model to response model:
db_user = UserDB(id=1, name="Priya", email="p@z.com", hashed_password="$2b$...")
response = UserResponse.model_validate(db_user)  # v2: model_validate
# or: UserResponse(**db_user.model_dump(exclude={"hashed_password"}))

# Pydantic v1 vs v2 quick differences:
# v1:                          v2:
# .dict()           →          .model_dump()
# .json()           →          .model_dump_json()
# .from_orm(obj)    →          .model_validate(obj)
# @validator         →          @field_validator (classmethod!)
# class Config:     →          model_config = ConfigDict(...)
# orm_mode = True   →          from_attributes = True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python + Pydantic: type safety + validation in one step
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool = True

p = Product(name="Laptop", price="999.99")   # "999.99" coerced to float
print(p.price)    # 999.99 (float)
print(p.in_stock) # True (default)
```

```javascript
// JavaScript: manual validation OR Zod (closest equivalent to Pydantic)
import { z } from "zod";

const ProductSchema = z.object({
    name: z.string(),
    price: z.number(),
    in_stock: z.boolean().default(true),
});

const result = ProductSchema.safeParse({ name: "Laptop", price: 999.99 });
if (result.success) {
    console.log(result.data.price);    // 999.99
} else {
    console.log(result.error);         // ZodError with path + message
}
// Zod is JS's Pydantic equivalent — same philosophy, different syntax
```

---

## 🟠 FastAPI Connection

```python
# Pydantic IS FastAPI's core — request validation, response serialization, OpenAPI docs
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

app = FastAPI()

class ProductCreate(BaseModel):
    """Request body — FastAPI validates automatically using Pydantic."""
    name: str = Field(min_length=1, max_length=200, examples=["iPhone 15"])
    price: float = Field(gt=0, description="Price in INR")
    category: str
    stock: int = Field(ge=0, default=0)

class ProductResponse(BaseModel):
    """Response model — excludes internal fields, shapes the JSON output."""
    id: int
    name: str
    price: float
    available: bool

    model_config = ConfigDict(from_attributes=True)  # allows ORM object → Pydantic

@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    # FastAPI:
    # 1. Parsed JSON body → validates using ProductCreate
    # 2. If invalid → 422 Unprocessable Entity with error details (automatic!)
    # 3. Calls this function with valid ProductCreate instance
    # 4. Response serialized using ProductResponse (filters out internal fields)
    
    db_product = save_to_db(product.model_dump())
    return ProductResponse.model_validate(db_product)

# Settings with Pydantic (BaseSettings):
from pydantic_settings import BaseSettings   # separate package: pydantic-settings

class Settings(BaseSettings):
    """Reads from environment variables automatically (case-insensitive)."""
    db_url: str                              # reads DB_URL or db_url from env
    secret_key: str
    debug: bool = False
    max_connections: int = 10

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()   # reads DB_URL, SECRET_KEY etc. from environment
print(settings.db_url)  # typed access, validated on startup
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `@validator` (v1) syntax in Pydantic v2
```python
# Wrong — Pydantic v1 syntax:
class User(BaseModel):
    age: int
    
    @validator("age")               # v1 style — works in v2 compat mode but deprecated
    def validate_age(cls, v):
        return v

# Correct — Pydantic v2 syntax:
class User(BaseModel):
    age: int
    
    @field_validator("age")
    @classmethod                    # required in v2!
    def validate_age(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Age cannot be negative")
        return v
```

❌ Mistake 2: Mutating a frozen model
```python
from pydantic import ConfigDict

class ImmutableUser(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str

u = ImmutableUser(name="Priya")
u.name = "Raj"    # ValidationError: Instance is frozen — use copy with update instead

# Correct:
u2 = u.model_copy(update={"name": "Raj"})   # returns new instance
```

---

## 🧠 Tricky Interview Question

```python
from pydantic import BaseModel
from typing import Optional

class Child(BaseModel):
    name: str

class Parent(BaseModel):
    name: str
    child: Optional[Child] = None

# What happens here?
p = Parent(name="Amit", child={"name": "Aarav"})
print(type(p.child))
print(p.child.name)
```
Answer:
- `type(p.child)` → `<class 'Child'>` — NOT `dict`!
- Pydantic automatically converts the nested dict `{"name": "Aarav"}` to a `Child` instance.
- This is Pydantic's **model coercion**: nested models are automatically validated and converted from dicts.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Pydantic v1 and v2?
A1: v2 (released 2023) is rewritten in Rust — 5-50x faster validation. Key changes: `@validator` → `@field_validator` (must be `@classmethod`), `@root_validator` → `@model_validator`, `.dict()` → `.model_dump()`, `.json()` → `.model_dump_json()`, `parse_obj()` → `model_validate()`, `class Config` → `model_config = ConfigDict(...)`, `orm_mode = True` → `from_attributes = True`. v2 is stricter about type coercion by default.

Q2: What is `model_config` and what are the most important settings?
A2: `model_config = ConfigDict(...)` replaces v1's inner `class Config`. Key settings: `frozen=True` (immutable instances, enables hashing), `extra="forbid"` (raise on unknown fields), `extra="ignore"` (silently drop unknown fields, default), `str_strip_whitespace=True` (auto-strip strings), `from_attributes=True` (allows ORM objects as input — was `orm_mode=True` in v1), `populate_by_name=True` (allow both alias and field name).

Q3: What is the difference between `field_validator` and `model_validator`?
A3: `@field_validator("field_name")` validates a single field — receives the field value, returns the validated/transformed value. `@model_validator(mode="after")` runs after all fields are set — receives the full model instance, can access multiple fields and their relationships. `mode="before"` runs before individual field validators, receives raw input data as a dict.

Q4: How does FastAPI use Pydantic for request validation?
A4: FastAPI inspects function parameter types. If a parameter is `body: SomeModel`, FastAPI: reads the JSON body, passes it to `SomeModel.model_validate(body_dict)`, and if `ValidationError` is raised → returns `422 Unprocessable Entity` with structured error details automatically. If a parameter is a query/path param with type annotation, FastAPI validates it individually. Response models (`response_model=SomeModel`) filter and serialize the return value.

Q5: What is `Annotated` and how does it work with Pydantic's `Field`?
A5: `Annotated[type, metadata]` is a Python typing construct that attaches metadata to a type without changing its meaning. Pydantic reads the metadata: `Annotated[int, Field(gt=0)]` means "int, validated with `gt=0`". This allows creating reusable type aliases: `PositiveInt = Annotated[int, Field(gt=0, description="Must be positive")]` — use it in multiple models without repeating the Field kwargs.

---

## 🔷 When to Use + When Not to Use

✅ Use Pydantic when:
- Validating API request/response data (FastAPI)
- Reading and validating configuration from environment (BaseSettings)
- Parsing external data (JSON APIs, CSV, DB results) with type safety
- Sharing data contracts between services (schema-as-code)
- Auto-generating OpenAPI docs

❌ Avoid when:
- Simple internal data classes with no validation (use `@dataclass`)
- Performance-critical hot paths where validation overhead matters (use TypedDict or raw dicts)
- When you only need serialization without validation (use `dataclasses.asdict`)

---

## 📊 Visual Diagram
```
Input (dict/JSON)
        │
        ▼
Pydantic BaseModel
┌───────────────────────────────────┐
│  1. Field type coercion           │  "25" → int 25
│  2. Built-in constraints (Field)  │  ge=18, min_length=1
│  3. @field_validator              │  custom single-field logic
│  4. @model_validator              │  cross-field validation
│                                   │
│  → ValidationError (422)          │  if any step fails
│  → Model instance                 │  if all pass
└───────────────────────────────────┘
        │
        ▼
.model_dump()     → dict  (for DB, internal use)
.model_dump_json() → str   (for HTTP response)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BaseModel | Base class for all Pydantic models | सब Pydantic models की base class |
| ValidationError | Raised when validation fails | Validation fail होने पर raise |
| field_validator | Decorator for single-field validation | Single field validate करने का decorator |
| model_validator | Decorator for cross-field validation | Multiple fields together validate करना |
| model_dump() | Serialize model to dict | Model को dict में convert करो |
| ConfigDict | Model configuration class | Model की configuration |
| from_attributes | Allow ORM objects as input | ORM objects को input में accept करो |

---

## ⚡ 3-Line Summary
English: Pydantic validates, coerces, and serializes data using Python type annotations — zero manual validation code. FastAPI uses it for all request bodies, query params, and response models, auto-generating 422 errors and OpenAPI docs. Key v1→v2 changes: `@field_validator` (must be `@classmethod`), `.model_dump()`, `ConfigDict`.
Hindi: Pydantic type annotations से data validate, coerce, serialize करती है — zero manual validation। FastAPI इसे request/response के लिए use करता है। V2 में `@field_validator` + `@classmethod`, `.model_dump()`, `ConfigDict` — याद रखो।

---

## ➡️ Next Topic
**304. Pydantic Field Types and Validators** — `HttpUrl`, `UUID`, `constr`, `conlist`, custom types. Then **305. Pydantic Settings** — `BaseSettings`, environment variables, `.env` files.
