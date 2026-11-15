---

# 366. MongoEngine
# हिंदी में: MongoEngine (MongoDB के लिए ODM)

---

## 🔵 Simple Definition (English)
MongoEngine is an ODM (Object-Document Mapper) for MongoDB. You define documents as Python classes with typed fields, and it validates data, builds queries (`User.objects(age__gt=18)`) and saves dicts for you. It is like Django ORM, but for MongoDB.

## 🔵 सरल परिभाषा (Hindi)
MongoEngine, MongoDB के लिए ODM (Object-Document Mapper) है। आप documents को typed fields वाली Python classes की तरह लिखते हैं, और यह data validate करता है, queries बनाता है (`User.objects(age__gt=18)`) और dicts save करता है। यह Django ORM जैसा है, पर MongoDB के लिए।

---

## 🔴 Problem it Solves
MongoDB itself has no schema, so with raw PyMongo any typo (`emial`) or wrong type is saved silently and breaks the app later. Teams want required fields, types, defaults, unique rules and reusable query code. MongoEngine adds these as classes and field rules, validated before every save.

## 🔴 यह क्यों बना? (Hindi)
MongoDB में खुद कोई schema नहीं होता, इसलिए raw PyMongo में कोई भी typo (`emial`) या गलत type चुपचाप save हो जाता है और बाद में app तोड़ता है। Teams को required fields, types, defaults, unique rules और दोबारा इस्तेमाल होने वाला query code चाहिए। MongoEngine ये सब classes और field rules के रूप में देता है, जो हर save से पहले validate होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → connect(db="shop", host=..., port=...)        registers a connection (alias "default")
Step 2 → class User(Document): fields...  meta = {...}     maps class -> collection
Step 3 → user.save()      runs validation (required, max_length, regex...) then inserts/updates
Step 4 → User.objects(name="Asha")    lazy QuerySet; runs when you iterate / count / first
Step 5 → Query operators:  age__gt=18, name__icontains="as", tags__in=[...]
Step 6 → EmbeddedDocument for nested data, ReferenceField for links (stored as ObjectId)
Step 7 → Errors: ValidationError, NotUniqueError, DoesNotExist, MultipleObjectsReturned
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → connect(db="shop", host=..., port=...)        connection register करता है (alias "default")
Step 2 → class User(Document): fields...  meta = {...}     class -> collection mapping
Step 3 → user.save()      validation चलाता है (required, max_length, regex...) फिर insert/update
Step 4 → User.objects(name="Asha")    lazy QuerySet; iterate / count / first पर चलता है
Step 5 → Query operators:  age__gt=18, name__icontains="as", tags__in=[...]
Step 6 → Nested data के लिए EmbeddedDocument, links के लिए ReferenceField (ObjectId के रूप में)
Step 7 → Errors: ValidationError, NotUniqueError, DoesNotExist, MultipleObjectsReturned
```

---

## 🟡 Real World Example
An internal HR tool uses MongoEngine models for employees (`EmailField(unique=True)`, embedded `Address`) so bad data is rejected before reaching MongoDB. A Django-style admin panel over MongoDB uses MongoEngine because the model classes look familiar. A content platform references authors from articles with `ReferenceField`.

## 🟡 Real Example Hindi mein
Internal HR tool employees के लिए MongoEngine models इस्तेमाल करता है (`EmailField(unique=True)`, embedded `Address`) ताकि खराब data MongoDB तक पहुंचने से पहले reject हो जाए। MongoDB के ऊपर Django जैसा admin panel MongoEngine चुनता है क्योंकि model classes जानी-पहचानी लगती हैं। Content platform articles से authors को `ReferenceField` से जोड़ता है।

---

## 💻 Code Example — Basic
```python
# Basic MongoEngine: documents as classes
from mongoengine import (Document, StringField, IntField, EmailField, connect, disconnect)   # ODM pieces

connect(db="shop_demo", host="127.0.0.1", port=34201, alias="default")   # register connection


class User(Document):
    """Maps to the 'user' collection."""
    name = StringField(required=True, max_length=50)   # required text
    email = EmailField(required=True, unique=True)     # validated + unique index
    age = IntField(min_value=0, max_value=120)         # range-checked number
    meta = {"collection": "users_me"}                  # explicit collection name


User.drop_collection()                            # clean demo state
u = User(name="Asha", email="asha@x.com", age=25).save()   # validate + insert
print(type(u.id).__name__)                        # ObjectId
User(name="Ravi", email="ravi@x.com", age=31).save()   # second user
print(User.objects.count())                       # 2
print([x.name for x in User.objects(age__gt=26)]) # django-style operators
found = User.objects(email="asha@x.com").first()  # first match or None
found.age = 26                                    # change field
found.save()                                      # update
print(User.objects.get(name="Asha").age)          # 26
disconnect()                                      # close

# Output:
# ObjectId
# 2
# ['Ravi']
# 26
```

## 💻 Code Example — Advanced
```python
# Production style: embedded docs, references, validation + duplicate handling
from typing import Optional                       # type hints
from mongoengine import (Document, EmbeddedDocument, EmbeddedDocumentField, ListField,
                         ReferenceField, StringField, FloatField, EmailField, connect, disconnect)
from mongoengine.errors import NotUniqueError, ValidationError   # ODM errors

connect(db="shop_demo", host="127.0.0.1", port=34201)   # connection


class Address(EmbeddedDocument):
    """Stored INSIDE the user document (no separate collection)."""
    city = StringField(required=True)             # city
    pin = StringField(regex=r"^\d{6}$")           # Indian PIN code


class Customer(Document):
    email = EmailField(required=True, unique=True)    # unique key
    address = EmbeddedDocumentField(Address)      # one embedded address
    meta = {"collection": "customers_me"}         # collection name


class Order(Document):
    customer = ReferenceField(Customer, required=True)   # stored as ObjectId
    items = ListField(StringField())              # list of SKUs
    total = FloatField(min_value=0)               # non-negative total
    meta = {"collection": "orders_me"}            # collection name


def create_customer(email: str, city: str, pin: str) -> Customer:
    try:                                          # translate ODM errors to domain errors
        return Customer(email=email, address=Address(city=city, pin=pin)).save()   # validate + save
    except NotUniqueError as e:                   # unique index hit
        raise ValueError("email already used") from e
    except ValidationError as e:                  # field rule broken
        raise ValueError(f"invalid data: {sorted(e.errors)}") from e


Customer.drop_collection(); Order.drop_collection()   # clean demo
c = create_customer("asha@x.com", "Delhi", "110001")  # ok
Order(customer=c, items=["A1", "B2"], total=350.0).save()   # order referencing customer
o: Optional[Order] = Order.objects.first()        # fetch
print(o.customer.email, o.customer.address.city)  # reference dereferenced lazily (extra query)
for bad in [("asha@x.com", "Delhi", "110001"), ("b@x.com", "Pune", "12")]:   # two failure cases
    try:                                          # try each
        create_customer(*bad)                     # fails
    except ValueError as e:                       # caught
        print("Error:", e)                        # message
disconnect()                                      # close

# Output (the PIN error lists the invalid top-level field 'address'):
# asha@x.com Delhi
# Error: email already used
# Error: invalid data: ['address']
```



---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (MongoEngine) | JavaScript (Mongoose) |
|---------|----------------------|------------------------|
| Model | `class User(Document)` | `mongoose.model("User", schema)` |
| Required | `StringField(required=True)` | `{ type: String, required: true }` |
| Query | `User.objects(age__gt=18)` | `User.find({ age: { $gt: 18 } })` |
| Save | `user.save()` | `await user.save()` |
| Async | sync only | promise-based |

```python
# Python way — model class + validated save
from mongoengine import Document, StringField, connect   # ODM
connect(db="shop_demo", host="127.0.0.1", port=34201)
class Tag(Document):
    name = StringField(required=True)              # required field
    meta = {"collection": "js_cmp3"}
Tag(name="python").save()                          # validate + insert
print(Tag.objects(name="python").count())          # 1
```
```javascript
// JavaScript way (Mongoose)
const Tag = mongoose.model("Tag", new mongoose.Schema({ name: { type: String, required: true } }));
await new Tag({ name: "python" }).save();
console.log(await Tag.countDocuments({ name: "python" }));
```

Key difference: MongoEngine is the Python equivalent of Mongoose. The model/field idea is the same, but MongoEngine is synchronous (no `await`) and query operators use double underscore (`age__gt`) instead of nested `$gt` objects.

---

## 🟠 FastAPI Connection
MongoEngine is synchronous, so use plain `def` endpoints in FastAPI (thread pool). Call `connect()` once at startup. Documents are not Pydantic models: convert to dicts or Pydantic schemas before returning, and translate `NotUniqueError` / `DoesNotExist` / `ValidationError` into `HTTPException` (409 / 404 / 422). For async FastAPI apps consider Beanie (Pydantic + Motor) instead.

```python
# FastAPI + MongoEngine (sync ODM): convert Documents to dicts for the response
from fastapi import FastAPI, HTTPException        # web
from fastapi.testclient import TestClient         # demo client
from mongoengine import Document, StringField, connect, disconnect, DoesNotExist, NotUniqueError, ValidationError   # ODM

connect(db="shop_demo", host="127.0.0.1", port=34201)


class Product(Document):
    sku = StringField(required=True, unique=True)
    name = StringField(required=True)
    meta = {"collection": "fa_me"}


Product.drop_collection()
app = FastAPI()


@app.post("/products", status_code=201)
def create(sku: str, name: str) -> dict[str, str]:
    try:
        p = Product(sku=sku, name=name).save()
    except NotUniqueError:
        raise HTTPException(409, "sku exists")
    except ValidationError as e:
        raise HTTPException(422, str(e))
    return {"id": str(p.id), "sku": p.sku}


@app.get("/products/{sku}")
def read(sku: str) -> dict[str, str]:
    try:
        p = Product.objects.get(sku=sku)
    except DoesNotExist:
        raise HTTPException(404, "not found")
    return {"sku": p.sku, "name": p.name}


c = TestClient(app)
print(c.post("/products", params={"sku": "A1", "name": "Pen"}).status_code)
print(c.post("/products", params={"sku": "A1", "name": "Pen"}).status_code)
print(c.get("/products/A1").json(), c.get("/products/ZZ").status_code)
disconnect()

# Output:
# 201
# 409
# {'sku': 'A1', 'name': 'Pen'} 404
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming `save()` always works without catching validation errors
✅ Correct: catch `ValidationError` / `NotUniqueError` and return a clear 4xx

```python
from mongoengine import Document, StringField, ValidationError, connect
connect(db="shop_demo", host="127.0.0.1", port=34201)
class U(Document):
    name = StringField(required=True)
    meta = {"collection": "m_u"}
# Wrong — crashes with an unhandled exception
# U().save()
# Right
try:
    U().save()
except ValidationError as e:
    print(list(e.errors))             # ['name']
```

❌ Mistake 2: Using `.get()` when 0 or many rows are possible
✅ Correct: use `.first()` or catch both `DoesNotExist` and `MultipleObjectsReturned`

```python
from mongoengine import DoesNotExist, MultipleObjectsReturned
U.drop_collection()
U(name="a").save(); U(name="a").save()
try:
    U.objects.get(name="a")           # Wrong — 2 matches
except MultipleObjectsReturned:
    print("Multiple")
print(U.objects(name="zz").first())   # Right — None when missing
```

❌ Mistake 3: Thinking `User.objects(...)` has already hit the database
✅ Correct: it is a lazy QuerySet; execution happens on iterate / `count()` / `first()` / `list()`

```python
q = U.objects(name="a")               # no query yet
print(type(q).__name__, q.count())    # QuerySet 2  (query runs here)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from mongoengine import Document, StringField, ValidationError, connect, DoesNotExist, MultipleObjectsReturned
connect(db="shop_demo", host="127.0.0.1", port=34201)
class U(Document):
    name = StringField(required=True)
    meta = {"collection": "t3"}
U.drop_collection()
try:
    U().save()
except ValidationError as e:
    print("VE", list(e.errors))
U(name="a").save(); U(name="a").save()
try:
    U.objects.get(name="a")
except MultipleObjectsReturned:
    print("Multiple")
try:
    U.objects.get(name="zz")
except DoesNotExist:
    print("DNE")
print(U.objects(name="zz").first())
```
Answer: `VE ['name']`, `Multiple`, `DNE`, `None`. Validation runs in Python BEFORE any write, so the empty document never reaches MongoDB. `get()` is strict: more than one match raises `MultipleObjectsReturned`, none raises `DoesNotExist`. `first()` is the forgiving version and returns `None`. Verified against a local MongoDB with MongoEngine 0.29.

---

## ⚫ Interview Questions + Answers

Q1: ODM vs ORM?
A1: ORM maps classes to relational tables, ODM maps classes to documents in a document database. Same idea (models, queries, validation), but ODM models can embed other documents instead of using joins.

Q2: Embedded document vs ReferenceField?
A2: Embedded data lives inside the parent document and is returned in one read; it is best for small bounded data. A reference stores an `ObjectId` of another document; dereferencing costs an extra query (use `select_related` or `.only()` carefully). Use references for shared or large data.

Q3: How do you make a field unique?
A3: `unique=True` on the field creates a unique index; duplicates raise `NotUniqueError`. Compound uniqueness: `meta = {"indexes": [{"fields": ["a", "b"], "unique": True}]}`.

Q4: MongoEngine vs PyMongo vs Beanie?
A4: PyMongo is the low-level driver (fastest, no schema). MongoEngine adds schema and validation, sync only. Beanie adds Pydantic models with async Motor/PyMongo Async, which is a better fit for FastAPI.

Q5: What does `meta = {"collection": ...}` do?
A5: It sets the collection name. By default MongoEngine uses the lower-cased class name (`User` -> `user`). `meta` also holds indexes, ordering and `allow_inheritance`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want schema, validation and model classes on top of MongoDB
- Sync frameworks: Flask, Django-like admin tools, Celery workers
- Teams coming from Django ORM / Mongoose

❌ Avoid when:
- You use async FastAPI heavily - prefer Beanie or Motor
- You need maximum raw speed or unusual aggregation - use PyMongo directly
- Your data has no stable shape at all

---

## 📊 Visual Diagram
```
class Order(Document):                    MongoDB collection "orders_me"
    customer = ReferenceField(Customer)  -->  { _id, customer: ObjectId(...), items: [...], total }
    items = ListField(StringField())
    total = FloatField(min_value=0)

save():  Python object -> validate fields -> dict -> insert/update
objects: QuerySet (lazy) -> filter dict -> find() -> Document objects
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ODM | Object-Document Mapper | Object को document से जोड़ने वाला layer |
| Document | Model class for a collection | Collection की model class |
| EmbeddedDocument | Nested sub-document | Document के अंदर document |
| ReferenceField | Link to another document | दूसरे document का link |
| QuerySet | Lazy query object | Lazy query object |
| Validation | Check fields before save | Save से पहले fields जांचना |

---

## ⚡ 3-Line Summary
English: MongoEngine maps Python classes to MongoDB collections with typed, validated fields. Use `save()`, lazy `objects(...)` queries with `field__op` filters, embedded documents for nested data, and catch `ValidationError` / `NotUniqueError` / `DoesNotExist`. It is sync, so use `def` endpoints in FastAPI.
Hindi: MongoEngine, Python classes को typed और validated fields के साथ MongoDB collections से जोड़ता है। `save()`, `field__op` filters वाली lazy `objects(...)` queries, nested data के लिए embedded documents इस्तेमाल करें, और `ValidationError` / `NotUniqueError` / `DoesNotExist` पकड़ें। यह sync है, इसलिए FastAPI में `def` endpoints रखें।

---

## ➡️ Next Topic
**367. Redis-py** — the Python client for the Redis in-memory store: caching, counters, rate limits and queues.
