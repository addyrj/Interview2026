---

# 092. Nested Structured Output
# हिंदी में: Nested (भीतर-भीतर) Structured Output

---

## 🔵 Simple Definition (English)
Nested structured output means a schema that contains other schemas: an object with sub-objects, or lists of objects. Example: a customs declaration contains a `shipper` object and a list of `items`, and each item has its own `classification` object. Pydantic models can reference other models, and OpenAI/Claude schemas support this through `$defs`/`$ref`.

## 🔵 सरल परिभाषा (Hindi)
Nested structured output ऐसा schema है जिसमें दूसरे schemas हों: object के अंदर sub-objects, या objects की lists। उदाहरण: customs declaration में `shipper` object और `items` की list है, और हर item में अपना `classification` object है। Pydantic models एक-दूसरे को refer कर सकते हैं, और OpenAI/Claude schemas इसे `$defs`/`$ref` से support करते हैं।

---

## 🔴 Problem it Solves
Real documents are hierarchical: an invoice has header, parties and many line items. A flat schema (`item1_name`, `item2_name`, ...) is limited, ugly and breaks when the count changes. Nesting mirrors the real structure and lets you reuse sub-models.

## 🔴 यह क्यों बना? (Hindi)
असली documents hierarchical होते हैं: invoice में header, parties और कई line items होते हैं। Flat schema (`item1_name`, `item2_name`, ...) सीमित, भद्दा है और count बदलने पर टूटता है। Nesting असली structure को दर्शाती है और sub-models को reuse करने देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify entities: Declaration -> Shipper, Items[] -> Classification
Step 2 → Create small Pydantic models for each entity
Step 3 → Compose them: items: list[Item], item.classification: Classification
Step 4 → Pydantic generates a JSON Schema with $defs and $ref
Step 5 → Send as response_format (strict mode supports nesting; each object needs all fields required)
Step 6 → LLM returns nested JSON
Step 7 → Pydantic validates every level and gives you nested objects (decl.items[0].classification.hs_code)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Entities पहचानो: Declaration -> Shipper, Items[] -> Classification
Step 2 → हर entity का छोटा Pydantic model बनाओ
Step 3 → उन्हें जोड़ो: items: list[Item], item.classification: Classification
Step 4 → Pydantic $defs और $ref वाला JSON Schema बनाता है
Step 5 → response_format में भेजो (strict mode nesting support करता है; हर object के सारे fields required)
Step 6 → LLM nested JSON लौटाता है
Step 7 → Pydantic हर level validate करता है और nested objects देता है (decl.items[0].classification.hs_code)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A shipment email lists 3 products. Output: `Declaration { shipper: Party, consignee: Party, items: [Item { name, quantity, value_usd, classification: { hs_code, duty_percent } }] }`. Total duty is computed in Python by summing item values times duty.

**Amazon-style**: An order has an address object and many line items, each with a product and quantity.

## 🟡 Real Example Hindi mein
**Tariff System**: Shipment email में 3 products हैं। Output: `Declaration { shipper: Party, consignee: Party, items: [Item { name, quantity, value_usd, classification: { hs_code, duty_percent } }] }`। Total duty Python में items की value × duty जोड़कर निकलती है।

**Amazon-style**: Order में address object और कई line items हैं, हर item में product और quantity।

---

## 💻 Code Example — Basic
```python
# Basic: nested Pydantic models, schema peek, validate a nested fake reply.
# Needs: pip install pydantic
import json                                             # to print
from pydantic import BaseModel, Field                   # modelling

class Classification(BaseModel):                        # innermost object
    hs_code: str
    duty_percent: float = Field(ge=0, le=100)

class Item(BaseModel):                                  # middle object
    name: str
    quantity: int = Field(ge=1)
    value_usd: float = Field(ge=0)
    classification: Classification                      # nested object

class Party(BaseModel):                                 # reusable sub-model
    name: str
    country: str

class Declaration(BaseModel):                           # top object
    shipper: Party
    consignee: Party
    items: list[Item]                                   # list of nested objects

schema = Declaration.model_json_schema()                # note $defs for sub-models
print(sorted(schema["$defs"].keys()))                   # ['Classification', 'Item', 'Party']

reply = json.dumps({
    "shipper": {"name": "Acme Ltd", "country": "CN"},
    "consignee": {"name": "Ravi Traders", "country": "IN"},
    "items": [
        {"name": "Earbuds", "quantity": 100, "value_usd": 2000,
         "classification": {"hs_code": "8518.30", "duty_percent": 10}},
        {"name": "Cable", "quantity": 500, "value_usd": 500,
         "classification": {"hs_code": "8544.42", "duty_percent": 5}},
    ]})                                                 # fake LLM reply
decl = Declaration.model_validate_json(reply)           # validate all levels
total = sum(i.value_usd * i.classification.duty_percent / 100 for i in decl.items)
print(f"Total duty: ${total:.2f}")                      # 2000*0.10 + 500*0.05 = 225.00
```

## 💻 Code Example — Advanced
```python
# Production: nested parse() with OpenAI, async, error handling and a flattening helper.
import asyncio
from typing import Optional
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError, model_validator

client = AsyncOpenAI()

class Classification(BaseModel):
    hs_code: str = Field(description="HS code 8518.30")
    duty_percent: float = Field(description="Duty percent")

class Item(BaseModel):
    name: str
    quantity: int
    value_usd: float
    classification: Classification

class Declaration(BaseModel):
    shipper_name: str
    items: list[Item] = Field(description="One entry per distinct product")

    @model_validator(mode="after")
    def at_least_one(self) -> "Declaration":
        if not self.items:                              # business rule
            raise ValueError("declaration needs at least one item")
        return self

    def total_duty(self) -> float:
        """Compute duty in code (never ask the LLM to do arithmetic)."""
        return sum(i.value_usd * i.classification.duty_percent / 100 for i in self.items)

async def extract(email_text: str) -> Optional[Declaration]:
    try:
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Extract the customs declaration."},
                      {"role": "user", "content": email_text}],
            response_format=Declaration, temperature=0, max_tokens=800)
    except (OpenAIError, ValidationError) as exc:
        print("extraction failed:", exc)
        return None
    msg = completion.choices[0].message
    return None if msg.refusal else msg.parsed

if __name__ == "__main__":
    d = asyncio.run(extract("Acme Ltd ships 100 earbuds ($2000) and 500 cables ($500)."))
    print(d.total_duty() if d else "no result")        # needs API key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class EmailIn(BaseModel):
    text: str

class DeclarationOut(BaseModel):
    declaration: Declaration
    total_duty_usd: float

@app.post("/extract-declaration", response_model=DeclarationOut)
async def extract_route(body: EmailIn) -> DeclarationOut:
    decl = await extract(body.text)
    if decl is None:
        raise HTTPException(status_code=422, detail="Could not extract declaration")
    return DeclarationOut(declaration=decl, total_duty_usd=decl.total_duty())   # nested response
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
extractor = llm.with_structured_output(Declaration)       # nested models work directly
decl = extractor.invoke("Acme Ltd ships 100 earbuds ($2000) and 500 cables ($500).")
# LangGraph: state = {"declaration": Declaration}; later nodes loop over decl.items,
# e.g. fan-out with Send() to classify each item in parallel.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Very deep nesting (5+ levels)
✅ Correct: Keep 2-3 levels; flatten or split into several calls.

```python
# Wrong: A.b.c.d.e.f  -> accuracy drops, schema limits (depth ~5, ~100 properties in OpenAI strict mode)
# Right: flatten or extract level by level
```

❌ Mistake 2: Asking the LLM to compute totals inside the schema
✅ Correct: Extract raw values, compute in Python.

```python
# Wrong: total_duty: float   # LLM does arithmetic, often off
# Right: def total_duty(self) -> float: sum(...)
```

---

## 🧠 Tricky Interview Question

**Q**: "The nested schema works with 3 items but with a 40-item invoice the JSON is cut off and invalid. Why, and what do you do?"

**Answer**: Output tokens hit `max_tokens` (or the model's output limit), so the JSON ends mid-array. Fixes: raise `max_tokens`, shrink field names/descriptions, split the document into chunks (e.g. 10 items per call) and merge results, or use streaming with incremental parsing. Always check `finish_reason == "length"`.

---

## ⚫ Interview Questions + Answers

Q1: How do you represent nested data in Pydantic?
A1: Use a model as a field type, e.g. `classification: Classification`, or `list[Item]`.

Q2: What are `$defs` and `$ref`?
A2: JSON Schema's way to define a reusable sub-schema once and reference it from many places.

Q3: Does strict mode support nested objects?
A3: Yes, as long as each object lists all properties as required with `additionalProperties: false`, within depth/size limits.

Q4: Why compute totals in code?
A4: LLMs are unreliable at arithmetic; code is exact and free.

Q5: How would you extract a 200-line invoice reliably?
A5: Chunk by page/sections, extract each chunk with the same nested schema, merge and de-duplicate, validate totals against the document's stated total, and flag mismatches for review.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Natural hierarchies (invoice, order, resume)
- Repeating groups of fields

❌ Avoid when:
- Simple key-value data (keep flat)
- Very deep or huge structures (split the task)

---

## 📊 Visual Diagram
```
 Declaration
 ├── shipper : Party {name, country}
 ├── consignee : Party {name, country}
 └── items : [ Item, Item, ... ]
              └── Item
                   ├── name, quantity, value_usd
                   └── classification : {hs_code, duty_percent}
```

---

## 💰 Cost Impact
Nested schemas have more tokens in the prompt (each sub-model's fields) and bigger outputs (repeated keys per item). A 40-item invoice can produce 3,000+ output tokens.
Optimise: short key names, drop optional descriptions, chunk long documents, use `gpt-4o-mini`, compute derived values in code instead of asking the LLM.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Nested schema | Schema inside schema | Schema के अंदर schema |
| $defs / $ref | Reusable sub-schema | दोबारा use होने वाला sub-schema |
| Line item | One row in a list | List की एक row |
| Flattening | Reduce nesting | Nesting घटाना |
| Depth limit | Max allowed nesting | अधिकतम गहराई |

---

## ⚡ 3-Line Summary
English: Nested outputs mirror real documents using models inside models. Keep depth small, compute totals in code and watch output length. Pydantic validates every level.
Hindi: Nested outputs models के अंदर models से असली documents जैसे होते हैं। Depth छोटी रखो, totals code में निकालो और output length देखो। Pydantic हर level validate करता है।

---

## ➡️ Next Topic
**093. Array Output** — returning lists of items safely (wrappers, ordering, limits).
