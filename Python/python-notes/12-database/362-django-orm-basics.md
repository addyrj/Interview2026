---

# 362. Django ORM Basics
# हिंदी में: Django ORM की बुनियादी बातें (Models और QuerySets)

---

## 🔵 Simple Definition (English)
The Django ORM lets you describe tables as Python classes (models) and query them with `Model.objects`. Queries are lazy `QuerySet`s: Django builds SQL only when you actually read the results. It ships with Django, including migrations and an admin.

## 🔵 सरल परिभाषा (Hindi)
Django ORM tables को Python classes (models) की तरह बताने देता है और `Model.objects` से query करने देता है। Queries lazy `QuerySet` होती हैं: Django SQL तभी बनाता है जब आप results सच में पढ़ते हैं। यह Django के साथ आता है, migrations और admin समेत।

---

## 🔴 Problem it Solves
Writing SQL strings by hand for every screen is slow and error-prone. A Django project needs forms, admin, auth and migrations all sharing one definition of the data. The ORM gives one model class that feeds all of these, protects against SQL injection, and works on SQLite, PostgreSQL and MySQL with the same code.

## 🔴 यह क्यों बना? (Hindi)
हर screen के लिए हाथ से SQL strings लिखना धीमा और गलतियों वाला है। Django project में forms, admin, auth और migrations सबको data की एक ही परिभाषा चाहिए। ORM एक model class देता है जो इन सबको चलाती है, SQL injection से बचाती है और SQLite, PostgreSQL, MySQL पर वही code चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define class Product(models.Model) with fields (CharField, IntegerField, ...)
Step 2 → python manage.py makemigrations   writes the migration file
Step 3 → python manage.py migrate          creates/updates the table
Step 4 → Product.objects.create(...) INSERTs; Product.objects.filter(...) builds a QuerySet
Step 5 → QuerySets are LAZY: chaining .filter().order_by() only builds SQL
Step 6 → SQL runs when you iterate, slice with a step, len(), list(), bool(), or call .get()/.first()/.count()
Step 7 → Result is cached inside the QuerySet, so a second loop does not hit the DB again
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → class Product(models.Model) बनाएं, fields के साथ (CharField, IntegerField, ...)
Step 2 → python manage.py makemigrations   migration फ़ाइल लिखता है
Step 3 → python manage.py migrate          table बनाता/बदलता है
Step 4 → Product.objects.create(...) INSERT करता है; Product.objects.filter(...) QuerySet बनाता है
Step 5 → QuerySets LAZY हैं: .filter().order_by() chain करने से सिर्फ SQL बनता है
Step 6 → SQL तब चलता है जब आप iterate, len(), list(), bool() करें या .get()/.first()/.count() बुलाएं
Step 7 → Result QuerySet के अंदर cache होता है, इसलिए दूसरा loop DB को दोबारा नहीं छूता
```

---

## 🟡 Real World Example
An e-commerce admin panel at a company like Flipkart: `Product.objects.filter(stock__lt=10, active=True).order_by("stock")` shows low-stock items; `Order.objects.filter(user=u).select_related("user")` lists orders; `F("stock") - 1` decrements stock atomically in the database to avoid race conditions between two buyers.

## 🟡 Real Example Hindi mein
Flipkart जैसी कंपनी के e-commerce admin panel में: `Product.objects.filter(stock__lt=10, active=True).order_by("stock")` कम stock वाले items दिखाता है; `Order.objects.filter(user=u).select_related("user")` orders की list देता है; `F("stock") - 1` stock को database में atomically घटाता है ताकि दो खरीदारों के बीच race condition न हो।

---

## 💻 Code Example — Basic
```python
# Basic Django ORM in a single script (no project folder needed)
import django
from django.conf import settings

settings.configure(                                       # minimal settings
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    INSTALLED_APPS=[],                                    # no apps: our model uses an explicit app_label
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()                                            # initialise Django

from django.db import connection, models                  # imports after setup()


class Product(models.Model):                              # one class = one table
    name = models.CharField(max_length=50)                # VARCHAR(50)
    price = models.IntegerField()                         # integer column
    active = models.BooleanField(default=True)            # default value

    class Meta:
        app_label = "shop"                                # needed because there is no installed app

    def __str__(self) -> str:
        return f"{self.name} ({self.price})"


with connection.schema_editor() as editor:                # what `migrate` does for a model
    editor.create_model(Product)

Product.objects.create(name="Pen", price=10)              # INSERT
Product.objects.bulk_create([Product(name="Book", price=250), Product(name="Bag", price=900, active=False)])

qs = Product.objects.filter(price__gte=100)               # lazy: no SQL yet
print(qs.query)                                           # shows the SQL Django will run
print([str(p) for p in qs.order_by("-price")])            # runs now: ['Bag (900)', 'Book (250)']
print(Product.objects.filter(active=True).count())        # 2
print(Product.objects.get(name="Pen"))                    # exactly one row, else exception
print(Product.objects.filter(name="Nope").first())        # None, no exception
Product.objects.filter(name="Pen").update(price=12)       # UPDATE in SQL, no object loaded
print(Product.objects.values_list("name", "price").order_by("name"))   # tuples
Product.objects.filter(active=False).delete()            # DELETE
print(Product.objects.count())                            # 2

# Output:
# SELECT "shop_product"."id", "shop_product"."name", "shop_product"."price", "shop_product"."active" FROM "shop_product" WHERE "shop_product"."price" >= 100
# ['Bag (900)', 'Book (250)']
# 2
# Pen (10)
# None
# <QuerySet [('Bag', 900), ('Book', 250), ('Pen', 12)]>
# 2
```

## 💻 Code Example — Advanced
```python
# Production style: relations, Q/F, aggregates, select_related, atomic, error handling
import django
from django.conf import settings

settings.configure(
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    INSTALLED_APPS=["__main__"],                          # this script itself acts as the app
    DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()

from django.db import connection, models, transaction
from django.db.models import Avg, Count, F, Q, Sum


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)   # unique constraint


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    class Meta:
        indexes = [models.Index(fields=["price"])]        # DB index


with connection.schema_editor() as editor:
    editor.create_model(Category)
    editor.create_model(Product)

food, tech = Category.objects.create(name="food"), Category.objects.create(name="tech")
Product.objects.bulk_create([
    Product(name="Tea", price=100, stock=5, category=food),
    Product(name="Rice", price=400, stock=50, category=food),
    Product(name="Phone", price=20000, stock=3, category=tech),
])

cheap_or_low = Product.objects.filter(Q(price__lt=150) | Q(stock__lt=4))   # OR with Q objects
print(sorted(p.name for p in cheap_or_low))               # ['Phone', 'Tea']

print(Product.objects.aggregate(avg=Avg("price"), total=Sum("stock")))     # {'avg': 6833.33..., 'total': 58}
per_cat = Category.objects.annotate(n=Count("products")).order_by("name").values_list("name", "n")
print(list(per_cat))                                      # [('food', 2), ('tech', 1)]


def buy(product_id: int, qty: int) -> None:
    """Atomic stock decrement using F() so concurrent buyers cannot oversell."""
    with transaction.atomic():                            # all-or-nothing
        updated = Product.objects.filter(pk=product_id, stock__gte=qty).update(stock=F("stock") - qty)
        if updated == 0:                                  # condition failed: not enough stock
            raise ValueError("out of stock")


buy(1, 2)                                                 # Tea: 5 -> 3
try:
    buy(1, 10)
except ValueError as e:
    print("Error:", e)
print(Product.objects.get(pk=1).stock)                    # 3

with connection.cursor() as c:                            # count SQL statements with select_related
    from django.test.utils import CaptureQueriesContext
    with CaptureQueriesContext(connection) as ctx:
        names = [(p.name, p.category.name) for p in Product.objects.all()]            # N+1
    print("without select_related:", len(ctx))
    with CaptureQueriesContext(connection) as ctx:
        names = [(p.name, p.category.name) for p in Product.objects.select_related("category")]
    print("with select_related:", len(ctx))
try:
    Category.objects.create(name="food")                  # duplicate
except Exception as e:
    print(type(e).__name__)                               # IntegrityError

# Output:
# ['Phone', 'Tea']
# {'avg': 6833.333333333333, 'total': 58}
# [('food', 2), ('tech', 1)]
# Error: out of stock
# 3
# without select_related: 4
# with select_related: 1
# IntegrityError
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Django ORM | Prisma / Sequelize (JS) |
|---------|-----------|--------------------------|
| Model | `class X(models.Model)` | `model X {}` / `sequelize.define` |
| Query | `X.objects.filter(a__gt=1)` | `findMany({where:{a:{gt:1}}})` |
| Lazy | yes (QuerySet) | no (Promise runs at once) |
| Migrations | built in (`makemigrations`) | `prisma migrate` |
| Atomic update | `F("stock") - 1` | `{ decrement: 1 }` |

```python
# Python way
Product.objects.filter(price__gte=100).order_by("-price")[:5]    # lazy until used
```
```javascript
// JavaScript way (Prisma)
await prisma.product.findMany({ where: { price: { gte: 100 } }, orderBy: { price: "desc" }, take: 5 });
```

Key difference: a Django QuerySet is lazy and reusable. You can build it step by step and pass it around, the SQL runs only when evaluated. In JS ORMs, calling the function runs the query immediately.

---

## 🟠 FastAPI Connection
Django ORM can be used with FastAPI, but it is mostly sync and tied to Django settings. In an async endpoint use the async QuerySet methods (`aget`, `acount`, `async for`) or `sync_to_async`, otherwise Django raises `SynchronousOnlyOperation`. Most FastAPI projects use SQLAlchemy; Django ORM makes sense when sharing models with an existing Django project.

```python
# FastAPI + Django ORM (async QuerySet API, Django 4.1+/6.x)
import tempfile
import django
from django.conf import settings

db_file = tempfile.NamedTemporaryFile(suffix=".sqlite3").name    # a file DB works across the worker threads
settings.configure(
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": db_file}},
    INSTALLED_APPS=[], DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
)
django.setup()
from django.db import connection, models
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


class Note(models.Model):
    text = models.CharField(max_length=100)

    class Meta:
        app_label = "notes"


with connection.schema_editor() as editor:
    editor.create_model(Note)

app = FastAPI()


@app.post("/notes")
async def add(text: str) -> dict[str, int]:
    note = await Note.objects.acreate(text=text)          # async create
    return {"id": note.pk}


@app.get("/notes/{note_id}")
async def get(note_id: int) -> dict[str, str]:
    try:
        note = await Note.objects.aget(pk=note_id)        # async get
    except Note.DoesNotExist:
        raise HTTPException(404, "not found")
    return {"text": note.text}


c = TestClient(app)
print(c.post("/notes", params={"text": "hello"}).json())  # {'id': 1}
print(c.get("/notes/1").json(), c.get("/notes/7").status_code)   # {'text': 'hello'} 404
```
Note: Django's async ORM methods run the sync database code in a worker thread, and an in-memory SQLite database is private to each connection, so the demo uses a temporary file database.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: N+1 queries on foreign keys
✅ Correct: `select_related` (FK / one-to-one) and `prefetch_related` (reverse FK / many-to-many)

```python
# Wrong: 1 + N queries
for p in Product.objects.all():
    print(p.category.name)
# Right: 1 query with a JOIN
for p in Product.objects.select_related("category"):
    print(p.category.name)
```

❌ Mistake 2: Read-modify-write race condition
✅ Correct: use `F()` expressions so the database does the arithmetic

```python
# Wrong: two requests both read stock=5 and both write 4
p = Product.objects.get(pk=1); p.stock -= 1; p.save()
# Right
Product.objects.filter(pk=1).update(stock=F("stock") - 1)
```

❌ Mistake 3: `len(qs)` or `if qs:` just to count or check
✅ Correct: `.count()` and `.exists()`

```python
# Wrong: loads every row into memory
if len(Product.objects.all()) > 0: ...
# Right
if Product.objects.exists(): ...
n = Product.objects.count()
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (model Product exists, 3 rows)
qs = Product.objects.all()
print(len(qs))                          # evaluates and caches
Product.objects.create(name="New", price=1)
print(qs.count())                       # ?
print(Product.objects.count())          # ?
```
Answer: `3`, `3`, `4`. `len(qs)` runs the query and stores the 3 rows inside the QuerySet (result cache). After the new row is created, `qs.count()` sees the cache and returns its length (3) without asking the database. `Product.objects.count()` builds a fresh QuerySet and runs `SELECT COUNT(*)`, which returns 4. A cached QuerySet is a snapshot; call `qs.all()` or build a new QuerySet to see new data. (Checked by running it on Django 6.1.)

---

## ⚫ Interview Questions + Answers

Q1: What is a lazy QuerySet?
A1: Creating or chaining a QuerySet does not hit the database. SQL runs on evaluation (iteration, `list()`, `len()`, `bool()`, slicing with step, `get()`, `first()`, `count()`, `exists()`). Results are cached on the instance.

Q2: `get()` vs `filter()`?
A2: `get()` returns exactly one object and raises `DoesNotExist` or `MultipleObjectsReturned` otherwise. `filter()` returns a QuerySet (possibly empty). `.first()` returns the first object or `None`.

Q3: `select_related` vs `prefetch_related`?
A3: `select_related` uses a SQL JOIN for forward ForeignKey and OneToOne. `prefetch_related` runs a second query and joins in Python, for reverse FK and many-to-many.

Q4: What are `Q` and `F` objects?
A4: `Q` builds complex conditions with `|`, `&`, `~` (OR, AND, NOT). `F` refers to a column value inside the database (`F("stock") - 1`), avoiding race conditions and extra reads.

Q5: What does `transaction.atomic()` do?
A5: It wraps a block in a database transaction: commit on success, rollback on exception. Nested `atomic()` blocks use savepoints. Use it for multi-step writes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building a Django project (admin, forms, auth need it)
- Standard CRUD with migrations built in
- You prefer convention over configuration

❌ Avoid when:
- You build a pure FastAPI service (SQLAlchemy fits better)
- You need heavy async throughput everywhere (Django's async ORM still uses threads internally)
- Complex reporting SQL (use `.raw()` or a query builder)

---

## 📊 Visual Diagram
```
 models.py              makemigrations           migrate
 class Product  ---->  migrations/0001.py  ---->  table in DB
      |
      v
 Product.objects            QuerySet (lazy)                    DB
   .filter(...)   -->  builds SQL, nothing runs  
   .order_by(...) -->  still nothing
   list()/for/len --> SELECT ... ------------------------>  rows
                      <------ cache result in QuerySet <----
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Model | Python class for a table | Table की Python class |
| QuerySet | Lazy, chainable query | Lazy और chain होने वाली query |
| Manager | `objects`, entry point for queries | Query का प्रवेश द्वार |
| Q object | OR/AND/NOT conditions | जटिल शर्तें |
| F expression | DB-side column reference | DB के अंदर column का संदर्भ |
| Migration | Versioned schema change | Schema बदलने की versioned script |

---

## ⚡ 3-Line Summary
English: Django ORM maps model classes to tables and exposes lazy, chainable QuerySets through `Model.objects`. Use `select_related`/`prefetch_related` against N+1, `F()` for atomic updates and `transaction.atomic()` for multi-step writes. With FastAPI prefer the async methods (`aget`, `acreate`).
Hindi: Django ORM model classes को tables से जोड़ता है और `Model.objects` से lazy, chain होने वाले QuerySets देता है। N+1 के लिए `select_related`/`prefetch_related`, atomic updates के लिए `F()` और multi-step writes के लिए `transaction.atomic()` इस्तेमाल करें। FastAPI के साथ async methods (`aget`, `acreate`) लें।

---

## ➡️ Next Topic
**363. Peewee ORM** — a small, simple ORM that is much lighter than SQLAlchemy or Django.
