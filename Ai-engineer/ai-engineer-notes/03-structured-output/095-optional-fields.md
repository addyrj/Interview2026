---

# 095. Optional Fields
# हिंदी में: Optional Fields

---

## 🔵 Simple Definition (English)
An optional field is one the model may leave empty (`null`) when the information is not in the input. In Pydantic you write `Optional[str]` (or `str | None`). In OpenAI strict mode, every field must be "required", so optional means **required but nullable**: the key is always present, and its value can be `null`.

## 🔵 सरल परिभाषा (Hindi)
Optional field वह है जिसे model खाली (`null`) छोड़ सकता है जब जानकारी input में न हो। Pydantic में `Optional[str]` (या `str | None`) लिखते हैं। OpenAI strict mode में हर field "required" होना चाहिए, इसलिए optional का मतलब है **required पर nullable**: key हमेशा मौजूद रहती है, और value `null` हो सकती है।

---

## 🔴 Problem it Solves
If every field is mandatory, the model will invent values to fill them: a missing invoice number becomes "INV-0001". Hallucinated data is worse than missing data. Optional fields give the model a safe, honest way to say "not provided".

## 🔴 यह क्यों बना? (Hindi)
अगर हर field mandatory है, तो model उन्हें भरने के लिए values गढ़ देगा: missing invoice number "INV-0001" बन जाएगा। Hallucinated data, missing data से बुरा है। Optional fields model को ईमानदारी से "नहीं दिया गया" कहने का सुरक्षित तरीका देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide which fields may truly be absent in the source
Step 2 → Declare them Optional[T] (no default for OpenAI strict mode)
Step 3 → Schema becomes {"anyOf": [{"type": "string"}, {"type": "null"}]}
Step 4 → Prompt: "Use null if the value is not stated. Never guess."
Step 5 → Model returns null for missing data
Step 6 → Code handles None explicitly (if x is None: ...)
Step 7 → Missing important data -> ask the user / mark needs_review
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → तय करो कि source में कौन से fields सच में गायब हो सकते हैं
Step 2 → उन्हें Optional[T] declare करो (OpenAI strict mode के लिए default मत दो)
Step 3 → Schema बनता है {"anyOf": [{"type": "string"}, {"type": "null"}]}
Step 4 → Prompt: "अगर value नहीं दी है तो null दो। अंदाज़ा मत लगाओ।"
Step 5 → Model missing data के लिए null देता है
Step 6 → Code None को साफ handle करता है (if x is None: ...)
Step 7 → ज़रूरी data गायब हो -> user से पूछो / needs_review mark करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Product text "Cotton T-shirt" has no `country_of_origin` and no `unit_value`. Those fields are `Optional`. The pipeline sees `None` and asks the user "Which country was it made in?" because origin changes the duty rate. Without optional fields the model might guess "China".

**Amazon-style**: Seller listing without a brand name returns `brand: null` instead of "Generic".

## 🟡 Real Example Hindi mein
**Tariff System**: Product text "Cotton T-shirt" में `country_of_origin` और `unit_value` नहीं है। ये fields `Optional` हैं। Pipeline `None` देखकर user से पूछती है "यह किस देश में बना?" क्योंकि origin से duty बदलती है। Optional के बिना model "China" का अंदाज़ा लगा देता।

**Amazon-style**: Brand name के बिना seller listing `brand: null` देती है, "Generic" नहीं।

---

## 💻 Code Example — Basic
```python
# Basic: Optional fields, null handling and the strict-mode schema shape.
# Needs: pip install pydantic
import json
from typing import Optional
from pydantic import BaseModel

class ProductInfo(BaseModel):
    name: str                                        # always present
    country_of_origin: Optional[str]                 # required key, nullable value (strict friendly)
    unit_value_usd: Optional[float]                  # may be unknown

print(json.dumps(ProductInfo.model_json_schema()["properties"]["country_of_origin"]))
# {"anyOf": [{"type": "string"}, {"type": "null"}], "title": ...}

replies = [
    '{"name": "Cotton T-shirt", "country_of_origin": null, "unit_value_usd": null}',
    '{"name": "Earbuds", "country_of_origin": "CN", "unit_value_usd": 20.5}',
]
for raw in replies:
    info = ProductInfo.model_validate_json(raw)      # null -> None
    missing = [f for f in ("country_of_origin", "unit_value_usd") if getattr(info, f) is None]
    if missing:
        print(f"{info.name}: ask user for {missing}")           # follow-up question
    else:
        print(f"{info.name}: ready, origin={info.country_of_origin}")
```

## 💻 Code Example — Advanced
```python
# Production: nullable fields, completeness scoring, follow-up questions, async.
import asyncio
from typing import Optional
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError

client = AsyncOpenAI()

class ProductInfo(BaseModel):
    name: str
    country_of_origin: Optional[str] = Field(description="ISO-2 country code, or null if not stated")
    material: Optional[str] = Field(description="Main material, or null if not stated")
    unit_value_usd: Optional[float] = Field(description="Price per unit, or null if not stated")

REQUIRED_FOR_DUTY = ("country_of_origin", "material")   # needed to compute duty

def missing_fields(info: ProductInfo) -> list[str]:
    """Which duty-critical fields are None?"""
    return [f for f in REQUIRED_FOR_DUTY if getattr(info, f) is None]

async def extract(text: str) -> Optional[ProductInfo]:
    try:
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "system",
                       "content": "Extract product info. If a value is not stated, use null. Never guess."},
                      {"role": "user", "content": text}],
            response_format=ProductInfo, temperature=0, max_tokens=200)
    except (OpenAIError, ValidationError) as exc:
        print("extract failed:", exc)
        return None
    msg = completion.choices[0].message
    return None if msg.refusal else msg.parsed

async def handle(text: str) -> dict:
    info = await extract(text)
    if info is None:
        return {"status": "error"}
    gaps = missing_fields(info)
    if gaps:                                             # do not guess, ask
        return {"status": "need_more_info", "ask": gaps, "partial": info.model_dump()}
    return {"status": "ok", "data": info.model_dump()}

if __name__ == "__main__":
    print(asyncio.run(handle("Cotton T-shirt, 20 pieces")))   # needs API key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/extract")
async def extract_route(text: str) -> dict:
    # Returns 200 with a status field; the client UI shows follow-up questions for None fields
    return await handle(text)
# Note: in FastAPI response models, Optional[str] = None fields can be omitted with
# response_model_exclude_none=True when you want smaller responses.
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
extractor = llm.with_structured_output(ProductInfo)       # Optional fields become nullable
info = extractor.invoke("Cotton T-shirt, 20 pieces")
# LangGraph: a conditional edge checks missing_fields(state["info"]);
# if gaps -> "ask_user" node (interrupt for human input) -> back to "extract".
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Making everything required with no way to say "unknown"
✅ Correct: Nullable fields plus "never guess" in the prompt.

```python
# Wrong: country_of_origin: str   -> model invents "China"
# Right: country_of_origin: Optional[str]  (+ prompt: use null if not stated)
```

❌ Mistake 2: Using defaults (`= None`) in OpenAI strict raw schemas
✅ Correct: Strict mode wants every key in `required`; use nullable type without relying on defaults.

```python
# Wrong (raw schema): "required": ["name"]  # country not in required -> strict error
# Right: "required": ["name","country"], country type ["string","null"]
```

---

## 🧠 Tricky Interview Question

**Q**: "You made `country_of_origin` Optional, yet the model still fills it with 'China' for every T-shirt. Why and how do you fix it?"

**Answer**: The model is biased toward completing fields; the prompt does not make null attractive. Fixes: explicit instruction "use null unless the text states it", describe the field ("only if explicitly mentioned"), add few-shot examples showing null, make the type `Literal[...,"unknown"]` if null is awkward, and evaluate on a set containing missing-value cases. Also verify claims by requiring an evidence quote field.

---

## ⚫ Interview Questions + Answers

Q1: How do you declare an optional field?
A1: `Optional[str]` or `str | None` in Pydantic.

Q2: Optional vs required in OpenAI strict mode?
A2: All keys must be required; optional is modeled as a nullable type (union with null).

Q3: Why prefer null over a default string like "N/A"?
A3: Null is unambiguous in code (`is None`), type-safe for numbers/dates and cannot be confused with real data.

Q4: How do you reduce hallucination for missing data?
A4: Explicit "do not guess" instruction, field descriptions, few-shot null examples, an `evidence` field quoting the source, and post-validation.

Q5: How do you design the follow-up question flow?
A5: After extraction, compute required-but-missing fields, generate (or template) a question per field, keep partial state (LangGraph checkpointer), resume extraction when the user answers and merge instead of overwriting.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Source text may omit information
- Wrong guesses are costly

❌ Avoid when:
- Field is truly always present (keep required to catch errors)

---

## 📊 Visual Diagram
```
 "Cotton T-shirt, 20 pieces"
          │
          ▼
 {name: "Cotton T-shirt",
  country_of_origin: null,   ◄── honest "not provided"
  material: "cotton",
  unit_value_usd: null}
          │
          ▼ missing = [country_of_origin]
  Ask user: "Which country was it made in?"
```

---

## 💰 Cost Impact
`anyOf` unions add a few schema tokens per field. The savings are indirect: fewer hallucinated values means fewer downstream corrections, support tickets and re-runs.
Optimise: only mark truly absent-able fields optional, keep descriptions short, store the follow-up state so you do not re-send the full document.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Optional | May be missing | हो भी सकता है, नहीं भी |
| Nullable | Value can be null | Value null हो सकती है |
| Required | Key must exist | Key ज़रूरी है |
| Hallucination | Invented data | गढ़ा हुआ data |
| Evidence field | Quote proving the value | सबूत वाला quote |

---

## ⚡ 3-Line Summary
English: Optional fields let the model say "unknown" instead of inventing values. In strict mode that means required-but-nullable. Handle None in code and ask the user for missing data.
Hindi: Optional fields model को values गढ़ने की जगह "पता नहीं" कहने देते हैं। Strict mode में इसका मतलब है required-but-nullable। Code में None handle करो और missing data के लिए user से पूछो।

---

## ➡️ Next Topic
**096. Streaming + Structured Output** — showing partial results to users while JSON is still being generated.
