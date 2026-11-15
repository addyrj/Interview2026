---

# 431. MVC Pattern
# हिंदी में: MVC Pattern (Model, View, Controller अलग-अलग)

---

## 🔵 Simple Definition (English)
MVC splits an application into three parts: the Model (data and rules), the View (how data is shown), and the Controller (receives a request, uses the model, picks a view). Each part changes without breaking the others.

## 🔵 सरल परिभाषा (Hindi)
MVC application को तीन हिस्सों में बांटता है: Model (data और नियम), View (data कैसे दिखे), और Controller (request लेता है, model इस्तेमाल करता है, view चुनता है)। हर हिस्सा बाकी को तोड़े बिना बदला जा सकता है।

---

## 🔴 Problem it Solves
In a single big function that reads the database, applies business rules, and builds HTML, any change (new JSON format, new column) touches everything and nothing can be tested alone. MVC gives each concern one home, so designers change views, backend developers change models, and the controller stays thin.

## 🔴 यह क्यों बना? (Hindi)
एक बड़े function में जो database पढ़ता है, business rules लगाता है और HTML बनाता है, कोई भी बदलाव (नया JSON format, नया column) सब कुछ छूता है और कुछ भी अकेले test नहीं हो पाता। MVC हर concern को एक घर देता है: designers views बदलते हैं, backend developers models, और controller पतला रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives at the Controller (GET /orders/1)
Step 2 → Controller asks the Model for the data (store.find(1))
Step 3 → Model returns a plain object or None (it knows nothing about HTML/JSON)
Step 4 → Controller chooses a View (TextView, JsonView, HTML template)
Step 5 → View formats the model data into the response
Step 6 → Controller returns the response to the caller
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request Controller तक आती है (GET /orders/1)
Step 2 → Controller Model से data मांगता है (store.find(1))
Step 3 → Model साधारण object या None लौटाता है (उसे HTML/JSON का कुछ पता नहीं)
Step 4 → Controller एक View चुनता है (TextView, JsonView, HTML template)
Step 5 → View model data को response में format करता है
Step 6 → Controller response caller को लौटाता है
```

---

## 🟡 Real World Example
Django is MVC (called MTV): models.py = Model, templates = View, views.py = Controller. Rails and Spring MVC follow the same idea. A Python web app that renders HTML pages for admins and also serves JSON to a mobile app reuses ONE model with two views.

## 🟡 Real Example Hindi mein
Django MVC है (इसे MTV कहते हैं): models.py = Model, templates = View, views.py = Controller। Rails और Spring MVC भी यही सोच रखते हैं। एक Python web app जो admins के लिए HTML pages और mobile app के लिए JSON देती है, वह एक ही model के दो views इस्तेमाल करती है।

---

## 💻 Code Example — Basic
```python
# Basic MVC: Model = data, View = presentation, Controller = glue
from dataclasses import dataclass             # model


@dataclass
class Product:                                # MODEL
    name: str
    price: float


class ProductView:                            # VIEW: only formats output
    def show(self, p: Product) -> str:
        return f"{p.name}: Rs.{p.price:.2f}"


class ProductController:                      # CONTROLLER: handles request
    def __init__(self, view: ProductView) -> None:
        self.view = view
        self.db: dict[int, Product] = {1: Product("Notebook", 99.5)}

    def get(self, pid: int) -> str:
        p = self.db.get(pid)
        return self.view.show(p) if p else "not found"


c: ProductController = ProductController(ProductView())
print(c.get(1))
print(c.get(2))

# Output:
# Notebook: Rs.99.50
# not found
```

## 💻 Code Example — Advanced
```python
# Production style: same model + controller, two interchangeable views (text and JSON)
import json                                   # JSON view
from dataclasses import asdict, dataclass     # model helper
from typing import Protocol                   # view interface


@dataclass(frozen=True)
class Order:                                  # MODEL
    id: int
    item: str
    total: float


class OrderView(Protocol):
    def render(self, o: Order) -> str: ...
    def render_error(self, msg: str) -> str: ...


class TextView:
    def render(self, o: Order) -> str: return f"Order #{o.id}: {o.item} Rs.{o.total}"
    def render_error(self, msg: str) -> str: return f"ERROR: {msg}"


class JsonView:
    def render(self, o: Order) -> str: return json.dumps(asdict(o))
    def render_error(self, msg: str) -> str: return json.dumps({"error": msg})


class OrderModelStore:
    def __init__(self) -> None:
        self._rows: dict[int, Order] = {1: Order(1, "Biryani", 349.0)}
    def find(self, oid: int) -> Order | None:
        return self._rows.get(oid)


class OrderController:
    def __init__(self, store: OrderModelStore, view: OrderView) -> None:
        self.store, self.view = store, view
    def show(self, oid: int) -> str:
        order = self.store.find(oid)
        return self.view.render(order) if order else self.view.render_error(f"order {oid} not found")


store = OrderModelStore()
print(OrderController(store, TextView()).show(1))
print(OrderController(store, JsonView()).show(1))
print(OrderController(store, JsonView()).show(5))

# Output:
# Order #1: Biryani Rs.349.0
# {"id": 1, "item": "Biryani", "total": 349.0}
# {"error": "order 5 not found"}
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| MVC framework | Django (MTV), Flask + Jinja | Express + EJS, NestJS (MVC), Rails-like Adonis |
| Model | Django model / Pydantic / dataclass | Mongoose / Sequelize model |
| View | Jinja2 / JSON serializer | EJS / React (view layer) |
| Controller | route function | route handler |

```python
# Python way (FastAPI)
@app.get("/books/{bid}", response_model=Book)    # route function = controller
def api_book(bid: int) -> Book:
    return DB[bid]                               # model data, JSON view by FastAPI
```
```javascript
// JavaScript way (Express)
app.get("/books/:id", (req, res) => {            // route handler = controller
  const book = Book.find(req.params.id);         // model
  res.render("book", { book });                  // view (template)
});
```

Key difference: React moved the View into the browser, so modern JS apps are often 'API + SPA' instead of server-rendered MVC. FastAPI follows the same split: Pydantic schemas are the data contract, route functions are controllers, and JSON serialization is the view.

---

## 🟠 FastAPI Connection
FastAPI is not strictly MVC, but the same separation applies. Routes (controllers) stay thin and call services/repositories (model layer); `response_model` (Pydantic) shapes the JSON view; `Jinja2Templates` or `HTMLResponse` provide HTML views when needed.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel

app: FastAPI = FastAPI()


class Book(BaseModel):                        # MODEL / schema
    id: int
    title: str


DB: dict[int, Book] = {1: Book(id=1, title="Python")}


@app.get("/api/books/{bid}", response_model=Book)    # route = controller, JSON = view
def api_book(bid: int) -> Book:
    return DB[bid]


@app.get("/books/{bid}", response_class=HTMLResponse)   # same model, HTML view
def page_book(bid: int) -> str:
    return f"<h1>{DB[bid].title}</h1>"


c = TestClient(app)
print(c.get("/api/books/1").json(), c.get("/books/1").text)

# Output:
# {'id': 1, 'title': 'Python'} <h1>Python</h1>
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Fat controller with business rules and SQL
✅ Correct: controller only coordinates

```python
# Wrong: route function computes discounts and writes SQL
# Right: route -> service.apply_discount(order) -> repo.save(order)
```

❌ Mistake 2: Model that formats output (HTML/JSON strings)
✅ Correct: model returns data; the view formats it

```python
# Wrong: class Order: def to_html(self) -> str
# Right: OrderView.render(order) builds the HTML or JSON
```

❌ Mistake 3: Class-level mutable state shared by all controllers
✅ Correct: create it in `__init__` or inject it

```python
class Wrong:
    db: dict[int, str] = {}                  # shared by ALL instances
class Right:
    def __init__(self) -> None:
        self.db: dict[int, str] = {}         # one per instance
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Controller:
    db = {}                                   # class-level: shared!
    def add(self, k, v): self.db[k] = v
a, b = Controller(), Controller()
a.add(1, "x")
print(b.db)
```
Answer: Output: `{1: 'x'}`. `db = {}` is a class attribute, so `a` and `b` share one dict. `a.add(1, 'x')` mutates that shared dict, and `b.db` sees it. Create mutable state in `__init__` (or inject it). This is the same shared-state trap as mutable default arguments.

---

## ⚫ Interview Questions + Answers

Q1: What does each letter in MVC mean?
A1: Model: data and business rules. View: presentation (HTML, JSON, text). Controller: handles input, calls the model, picks the view.

Q2: MVC vs MVT in Django?
A2: Django calls the Model 'Model', the View-as-presentation 'Template', and the Controller 'View'. The framework itself acts as the controller by routing URLs. Same idea, different names.

Q3: Is FastAPI MVC?
A3: Not by design, but you can structure it that way: routers (controller), services/repositories (model layer), Pydantic response models and templates (view).

Q4: What is a fat controller and why is it bad?
A4: A controller containing business logic or SQL. It is hard to test and reuse (a CLI cannot call it). Move logic to services/models.

Q5: MVC vs MVP vs MVVM?
A5: MVC: controller picks the view. MVP: a presenter updates a passive view. MVVM: a view-model exposes bindable state that the view observes (used in frontend frameworks).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Web apps that render pages or several output formats
- Teams where UI and backend work are split
- You want to test business logic without HTTP

❌ Avoid when:
- Tiny JSON-only microservices: routes + services + schemas are enough
- Forcing three layers on a ten-line script
- Business logic stuffed in controllers

---

## 📊 Visual Diagram
```
Request GET /orders/1
   |
   v
Controller.show(1) ----> Model: store.find(1) -> Order(1,"Biryani",349.0)
   |                                  |
   +------- picks a View <------------+
        TextView.render(order)   -> "Order #1: Biryani Rs.349.0"
        JsonView.render(order)   -> '{"id": 1, ...}'
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Model | Data and business rules | Data और business rules |
| View | Presentation of data | Data की प्रस्तुति |
| Controller | Coordinates request, model, view | Request, model, view को जोड़ने वाला |
| Fat controller | Controller with too much logic | बहुत logic वाला controller |
| MVT | Django's name for MVC | Django में MVC का नाम |

---

## ⚡ 3-Line Summary
English: MVC separates data (Model), presentation (View), and request handling (Controller). Keep controllers thin and let models know nothing about output formats. FastAPI follows the same split with routes, services, and Pydantic response models.
Hindi: MVC data (Model), प्रस्तुति (View) और request handling (Controller) को अलग करता है। Controllers पतले रखें और models को output format का पता न हो। FastAPI में routes, services और Pydantic response models से यही बंटवारा होता है।

---

## ➡️ Next Topic
**432. CQRS in Python** — separate the write model from the read model.
