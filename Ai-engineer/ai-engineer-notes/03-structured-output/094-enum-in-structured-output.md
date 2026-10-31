---

# 094. Enum in Structured Output
# हिंदी में: Structured Output में Enum

---

## 🔵 Simple Definition (English)
An enum limits a field to a fixed list of allowed values, such as `"low" | "medium" | "high"` or a list of valid HS chapters. In Python you use `enum.Enum` (as `str, Enum`) or `typing.Literal`. In JSON Schema this becomes `"enum": [...]`, and with strict mode the model cannot output anything outside the list.

## 🔵 सरल परिभाषा (Hindi)
Enum किसी field को allowed values की fixed list तक सीमित करता है, जैसे `"low" | "medium" | "high"` या valid HS chapters की list। Python में `enum.Enum` (`str, Enum` के रूप में) या `typing.Literal` use होता है। JSON Schema में यह `"enum": [...]` बन जाता है, और strict mode में model list के बाहर कुछ output नहीं कर सकता।

---

## 🔴 Problem it Solves
Free-text categories drift: "Electronics", "electronic", "Electronic goods", "elec." all mean the same but break `if category == "electronics"`. Enums make classification outputs consistent and eliminate invented labels.

## 🔴 यह क्यों बना? (Hindi)
Free-text categories बदलती रहती हैं: "Electronics", "electronic", "Electronic goods", "elec." सब एक ही मतलब के हैं पर `if category == "electronics"` तोड़ देते हैं। Enums classification outputs को consistent रखते हैं और बनावटी labels खत्म करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List the allowed values (from DB, config or business rules)
Step 2 → Declare Enum / Literal in the Pydantic model
Step 3 → Schema gets {"enum": ["electronics", "footwear", ...]}
Step 4 → Strict decoding allows only those strings
Step 5 → Model picks one (add an "other" or "unknown" value for the rest)
Step 6 → Pydantic converts the string into the Enum member
Step 7 → Use `category is Category.ELECTRONICS`, safe from typos
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Allowed values की list बनाओ (DB, config या business rules से)
Step 2 → Pydantic model में Enum / Literal declare करो
Step 3 → Schema में {"enum": ["electronics", "footwear", ...]} आ जाता है
Step 4 → Strict decoding सिर्फ वही strings allow करती है
Step 5 → Model एक चुनता है (बाकी के लिए "other" या "unknown" रखो)
Step 6 → Pydantic string को Enum member में बदलता है
Step 7 → `category is Category.ELECTRONICS` use करो, typos से सुरक्षित
```

---

## 🟡 Real World Example
**Tariff Classification System**: Step 1 of a two-stage pipeline picks the HS **chapter** from an enum of 97 chapters (or the top 5 retrieved by RAG). Step 2 picks the exact code only from that chapter's codes. Enums keep the model inside real codes.

**Zomato-style**: Complaint `category: Literal["late_delivery","wrong_item","quality","payment","other"]` routes tickets to the right team.

## 🟡 Real Example Hindi mein
**Tariff System**: दो-stage pipeline के step 1 में HS **chapter** 97 chapters के enum (या RAG के top 5) में से चुना जाता है। Step 2 में exact code सिर्फ उसी chapter के codes में से। Enums model को असली codes के अंदर रखते हैं।

**Zomato-style**: Complaint `category: Literal["late_delivery","wrong_item","quality","payment","other"]` ticket को सही team तक पहुँचाता है।

---

## 💻 Code Example — Basic
```python
# Basic: Enum and Literal in Pydantic; see the schema and the rejection of bad values.
# Needs: pip install pydantic
import json
from enum import Enum                                   # Python enum
from typing import Literal                              # alternative to Enum
from pydantic import BaseModel, ValidationError

class Category(str, Enum):                              # str mixin -> JSON friendly
    ELECTRONICS = "electronics"
    FOOTWEAR = "footwear"
    FOOD = "food"
    OTHER = "other"                                     # escape hatch for unknowns

class Product(BaseModel):
    name: str
    category: Category                                  # restricted to the enum
    risk: Literal["low", "medium", "high"]              # inline alternative

print(json.dumps(Product.model_json_schema()["$defs"]["Category"]["enum"]))   # allowed values

ok = Product.model_validate_json('{"name": "Earbuds", "category": "electronics", "risk": "low"}')
print(ok.category is Category.ELECTRONICS, ok.category.value)                 # True electronics

try:
    Product.model_validate_json('{"name": "Earbuds", "category": "Electronic goods", "risk": "low"}')
except ValidationError as exc:                          # invented label rejected
    print("Rejected:", exc.errors()[0]["msg"])
```

## 💻 Code Example — Advanced
```python
# Production: build the Enum dynamically from a DB list, two-stage classification, async.
import asyncio
from enum import Enum
from typing import Optional
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError, create_model

client = AsyncOpenAI()

def load_chapters() -> list[str]:
    """Pretend DB read: valid HS chapters for this tenant."""
    return ["8517", "8518", "8471", "6403"]

def make_choice_model(values: list[str], name: str = "Choice") -> type[BaseModel]:
    """Create a Pydantic model whose `value` is a dynamic Enum of the given values."""
    members = {"V_" + v.replace(".", "_").replace("-", "_"): v for v in values}   # valid member names
    dyn_enum = Enum("Dyn", members, type=str)             # str-based dynamic Enum
    return create_model(name, value=(dyn_enum, ...), reason=(str, Field(description="One short sentence")))

async def pick(product: str, options: list[str]) -> Optional[str]:
    """Ask the LLM to choose exactly one of `options`."""
    Choice = make_choice_model(options)                    # schema now has enum: options
    try:
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": f"Pick the best option for: {product}"},
                      {"role": "user", "content": product}],
            response_format=Choice, temperature=0, max_tokens=100)
    except (OpenAIError, ValidationError) as exc:
        print("pick failed:", exc)
        return None
    parsed = completion.choices[0].message.parsed
    return parsed.value.value if parsed else None          # enum member -> plain string

async def classify(product: str) -> Optional[str]:
    chapter = await pick(product, load_chapters())         # stage 1: chapter
    if chapter is None:
        return None
    codes = [f"{chapter}.{n:02d}" for n in (10, 30, 90)]   # stage 2: codes of that chapter (demo)
    return await pick(product, codes)

if __name__ == "__main__":
    print(asyncio.run(classify("Wireless earbuds")))        # needs API key
```

---

## 🟠 FastAPI Integration
```python
from enum import Enum
from fastapi import FastAPI

app = FastAPI()

class Severity(str, Enum):
    LOW = "low"
    HIGH = "high"

@app.get("/tickets")
async def tickets(severity: Severity) -> dict:
    # FastAPI validates the query against the same enum and shows the choices in /docs
    return {"severity": severity.value}
# The same Enum can be reused as a field in the LLM response model -> one definition everywhere.
```

---

## 🔗 LangChain / LangGraph Connection
```python
from typing import Literal
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

class Route(BaseModel):
    destination: Literal["classify", "refund", "human"]       # allowed next nodes

router = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Route)
decision = router.invoke("I want my money back for the wrong item")
# LangGraph: add_conditional_edges("router", lambda s: s["route"].destination, {...})
# The Literal guarantees the returned name matches a real node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No "other/unknown" option
✅ Correct: Include an escape value so the model does not force a wrong label.

```python
# Wrong: Category = {"electronics","footwear"}  -> a book is forced into one of them
# Right: add OTHER = "other" and route "other" to review
```

❌ Mistake 2: Huge enums (1,000+ values)
✅ Correct: Narrow first (retrieval or two-stage), then pick.

```python
# Wrong: enum with all 5,000 HS codes in the schema -> slow, costly, less accurate
# Right: RAG returns top 10 codes -> enum of those 10
```

---

## 🧠 Tricky Interview Question

**Q**: "Your enum has the values 'electronics' and 'electrical'. The model keeps confusing them. Is it a model problem?"

**Answer**: Usually a schema/prompt problem. Similar labels without definitions are ambiguous. Add short descriptions per value (in the field description or as a legend in the system prompt), include few-shot examples, merge labels that are not truly different, and add an "unsure" option. Check a confusion matrix on labelled data to see which pairs fail.

---

## ⚫ Interview Questions + Answers

Q1: How do you restrict a field to a few values?
A1: Use `Literal[...]` or an `Enum` in Pydantic; the JSON Schema gets an `enum`.

Q2: Why subclass `str` in `class Category(str, Enum)`?
A2: So members behave like strings and serialize to JSON without extra code.

Q3: What happens if the model outputs a value outside the enum in non-strict mode?
A3: Pydantic raises `ValidationError`; handle with retry or fallback.

Q4: How do you include per-value meaning?
A4: Put descriptions in the prompt or `Field(description=...)`, e.g. "electronics: powered devices; electrical: wiring and fittings".

Q5: How would you handle a label set that changes weekly?
A5: Build the Enum dynamically at request time from the DB (`create_model`), cache per version, include the version in logs, and add tests that run when labels change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Classification, routing, status, severity
- Values must match code or DB

❌ Avoid when:
- Open-ended text answers
- Thousands of possible values without prefiltering

---

## 📊 Visual Diagram
```
 Allowed: [electronics | footwear | food | other]
                │
 "Nike Air shoes" ─► LLM (constrained) ─► "footwear" ✔
                                           "Footwear goods" ✘ (impossible)
```

---

## 💰 Cost Impact
Enum values are input tokens (each value ~2-5 tokens). 100 values add ~300 tokens per request. Outputs get shorter because the model emits just one value.
Optimise: prefilter with embeddings/RAG to 5-20 candidates, use short codes, two-stage classification, and cache the schema prefix.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Enum | Fixed set of values | तय मानों का सेट |
| Literal | Inline fixed values | Inline fixed values |
| Escape hatch | "other/unknown" option | "अन्य/पता नहीं" विकल्प |
| Two-stage | Narrow then choose | पहले छाँटो फिर चुनो |
| Label drift | Labels changing meaning | Labels का बदलना |

---

## ⚡ 3-Line Summary
English: Enums force the model to choose from allowed values, giving consistent outputs. Always add an "other" option and keep the list short. Prefilter big label sets with retrieval.
Hindi: Enums model को allowed values में से चुनने पर मजबूर करते हैं, जिससे outputs consistent रहते हैं। हमेशा "other" option रखो और list छोटी रखो। बड़े label sets को retrieval से पहले छाँटो।

---

## ➡️ Next Topic
**095. Optional Fields** — handling missing information without forcing the model to make things up.
