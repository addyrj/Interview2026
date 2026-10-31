---

# 083. Structured Output in OpenAI
# हिंदी में: OpenAI में Structured Output

---

## 🔵 Simple Definition (English)
Structured Output means asking the OpenAI model to reply in a fixed JSON shape (a schema) instead of free text. With `strict` mode the API guarantees the reply matches your JSON Schema — every required key is present and types are correct. Your code can then use the result like a normal Python object.

## 🔵 सरल परिभाषा (Hindi)
Structured Output का मतलब है कि model free text की जगह एक fixed JSON shape (schema) में जवाब दे। `strict` mode में API guarantee देती है कि reply आपके JSON Schema से match करेगा — सारी required keys होंगी और types सही होंगे। फिर आप result को normal Python object की तरह use कर सकते हैं।

---

## 🔴 Problem it Solves
Early LLM apps asked "reply in JSON" inside the prompt. The model sometimes added "Sure! Here is the JSON:", used single quotes, forgot a key or wrote `"duty": "about 5%"` instead of a number. `json.loads` crashed and production pipelines broke. We needed a contract between the LLM and our code, enforced by the API, not by hope.

## 🔴 यह क्यों बना? (Hindi)
पहले हम prompt में लिखते थे "JSON में जवाब दो"। Model कभी "Sure! Here is JSON:" लिख देता, single quotes लगा देता, कोई key भूल जाता या `"duty": "about 5%"` जैसा text दे देता। `json.loads` crash होता था और pipeline टूट जाती थी। हमें LLM और code के बीच एक contract चाहिए था जो API enforce करे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a schema (Pydantic model or raw JSON Schema)
Step 2 → Send it in `response_format` with strict=True
Step 3 → OpenAI compiles the schema into a grammar (first call is slightly slower)
Step 4 → During decoding, tokens that would break the schema are masked out
Step 5 → Model returns valid JSON text (or a `refusal` field if it declines)
Step 6 → SDK parses it back into your Pydantic object (message.parsed)
Step 7 → Your code uses typed fields — no string cleaning needed
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Schema define करो (Pydantic model या raw JSON Schema)
Step 2 → उसे `response_format` में strict=True के साथ भेजो
Step 3 → OpenAI schema को grammar में compile करता है (पहली call थोड़ी slow)
Step 4 → Decoding के समय schema तोड़ने वाले tokens block कर दिए जाते हैं
Step 5 → Model valid JSON देता है (या मना करे तो `refusal` field)
Step 6 → SDK उसे Pydantic object (message.parsed) में बदल देता है
Step 7 → आपका code typed fields use करता है — string cleaning की ज़रूरत नहीं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A user types "Bluetooth wireless earbuds with charging case". The model must return `hs_code`, `description`, `duty_percent` and `confidence`. Downstream code writes this to a database and calculates customs duty. A single wrong type (duty as text) would crash the billing step. Structured Output guarantees the shape.

**Zomato-style**: An AI that reads a food order message and returns `{"dish": "...", "quantity": 2, "spice_level": "medium"}` for the kitchen display.

## 🟡 Real Example Hindi mein
**Tariff System**: User लिखता है "Bluetooth wireless earbuds with charging case"। Model को `hs_code`, `description`, `duty_percent`, `confidence` return करना है। Downstream code इसे database में लिखता है और customs duty calculate करता है। अगर duty text आ गई तो billing crash होगी। Structured Output shape की guarantee देता है।

**Zomato-style**: Food order message पढ़कर `{"dish": "...", "quantity": 2, "spice_level": "medium"}` देना, जो kitchen display पर जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: build a strict JSON Schema by hand and "simulate" the API reply.
# This runs offline; the real call is shown in the comments.
import json                                   # standard JSON parser
from typing import Any                        # type hint for generic dicts

# The schema we send to OpenAI inside response_format
tariff_schema: dict[str, Any] = {             # a plain dict is a valid JSON Schema
    "type": "object",                         # top level must be an object
    "properties": {                           # list every allowed key
        "hs_code": {"type": "string"},        # HS code as text, e.g. "8518.30"
        "duty_percent": {"type": "number"},   # duty must be a number
        "confidence": {"type": "number"},     # 0.0 to 1.0
    },
    "required": ["hs_code", "duty_percent", "confidence"],  # strict mode: ALL keys required
    "additionalProperties": False,            # strict mode: no extra keys allowed
}

# The response_format payload exactly as OpenAI expects it
response_format: dict[str, Any] = {
    "type": "json_schema",                    # use schema based output
    "json_schema": {
        "name": "tariff_result",              # a name for the schema
        "strict": True,                       # enforce schema 100%
        "schema": tariff_schema,              # our schema from above
    },
}

# Real call (needs OPENAI_API_KEY) would be:
# resp = client.chat.completions.create(model="gpt-4o-mini",
#            messages=[...], response_format=response_format)
fake_reply = '{"hs_code": "8518.30", "duty_percent": 0.0, "confidence": 0.93}'  # simulated reply

def validate(data: dict[str, Any], schema: dict[str, Any]) -> None:
    """Tiny validator: check required keys and no extra keys."""
    missing = [k for k in schema["required"] if k not in data]      # keys the model forgot
    extra = [k for k in data if k not in schema["properties"]]      # keys we never asked for
    if missing or extra:                                            # any problem?
        raise ValueError(f"missing={missing} extra={extra}")        # fail loudly

try:
    data = json.loads(fake_reply)             # text -> dict
    validate(data, tariff_schema)             # check against schema
    print("HS code:", data["hs_code"])        # typed use, no guessing
    print("Duty:", data["duty_percent"], "%") # number, safe for maths
except (json.JSONDecodeError, ValueError) as exc:   # handle both failure types
    print("Bad output:", exc)                 # in production: log + retry
```

## 💻 Code Example — Advanced
```python
# Production: Pydantic + OpenAI parse() helper + refusal handling + async
import asyncio                                         # run async code
from typing import Optional                            # for optional values
from openai import AsyncOpenAI, OpenAIError            # async client + base error
from pydantic import BaseModel, Field                  # schema definition

client = AsyncOpenAI()                                 # reads OPENAI_API_KEY from env

class TariffResult(BaseModel):                         # our contract with the LLM
    hs_code: str = Field(description="HS code like 8518.30")   # description guides model
    description: str = Field(description="Short product description")
    duty_percent: float = Field(description="Import duty in percent")
    confidence: float = Field(description="Between 0 and 1")

async def classify(product: str) -> Optional[TariffResult]:
    """Return a TariffResult or None if the model refused."""
    try:
        completion = await client.beta.chat.completions.parse(   # parse() = create + validate
            model="gpt-4o-mini",                                  # supports Structured Outputs
            messages=[
                {"role": "system", "content": "You are a customs tariff classifier."},
                {"role": "user", "content": product},             # user product text
            ],
            response_format=TariffResult,                         # pass Pydantic class directly
            temperature=0,                                        # stable output
            max_tokens=300,                                       # cap output cost
        )
    except OpenAIError as exc:                                    # network, rate limit, 4xx
        print("OpenAI error:", exc)                               # log it
        return None                                               # caller decides fallback
    message = completion.choices[0].message                       # first choice
    if message.refusal:                                           # safety refusal is separate field
        print("Refused:", message.refusal)                        # do not treat as data
        return None
    usage = completion.usage                                      # token accounting
    if usage:
        print(f"tokens in={usage.prompt_tokens} out={usage.completion_tokens}")
    return message.parsed                                         # already a TariffResult

if __name__ == "__main__":
    result = asyncio.run(classify("Bluetooth wireless earbuds"))  # needs API key
    print(result)
```

---

## 🟠 FastAPI Integration
Use the same Pydantic model as FastAPI `response_model`. One class gives you LLM schema, validation and API docs.

```python
from fastapi import FastAPI, HTTPException      # web framework
from pydantic import BaseModel                  # request model

app = FastAPI()                                 # app instance

class ProductIn(BaseModel):                     # request body
    product: str

@app.post("/classify", response_model=TariffResult)   # TariffResult from above
async def classify_route(body: ProductIn) -> TariffResult:
    result = await classify(body.product)       # call LLM helper
    if result is None:                          # refusal or API failure
        raise HTTPException(status_code=502, detail="LLM could not classify")
    return result                               # FastAPI serialises it to JSON
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangChain wraps the same feature in with_structured_output()
from langchain_openai import ChatOpenAI          # chat model wrapper

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)          # base model
structured_llm = llm.with_structured_output(TariffResult)     # uses OpenAI structured output
result = structured_llm.invoke("Bluetooth wireless earbuds")  # returns TariffResult
# In LangGraph, a node returns {"tariff": result} so later nodes read typed state.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Asking for JSON only in the prompt
✅ Correct: Use `response_format` with a schema.

```python
# Wrong — model may add text around the JSON:
# messages=[{"role": "user", "content": "Return JSON with hs_code"}]
# Right — API enforces the shape:
# response_format=TariffResult
```

❌ Mistake 2: Using unsupported schema features in strict mode (optional keys, missing `additionalProperties: false`)
✅ Correct: Make every field required; model "optional" as `type: ["string", "null"]`.

```python
# Wrong: field with default and not required -> rejected in strict mode (raw schema)
# Right: hs_code: Optional[str]  (Pydantic helper turns this into required + nullable)
```

---

## 🧠 Tricky Interview Question

**Q**: "You turned on strict Structured Output, so the JSON is always valid. Does that mean the HS code is always correct?"

**Answer**: No. Structured Output guarantees **syntax and shape**, not **truth**. The model can return a perfectly formed `{"hs_code": "9999.99"}` that does not exist. You still need semantic validation (lookup in the real tariff table), confidence thresholds and human review for low confidence. Also check `finish_reason` — if `length`, the JSON may be cut off, and check `refusal`.

---

## ⚫ Interview Questions + Answers

Q1: What is Structured Output?
A1: A feature where the model's reply is forced to match a JSON Schema you give, so you get predictable, parseable data.

Q2: What does `strict: true` do?
A2: It makes the API guarantee the output follows the schema exactly (all required keys, correct types, no extra keys), using constrained decoding.

Q3: How is Structured Output different from JSON mode?
A3: JSON mode (`{"type":"json_object"}`) only guarantees the text is valid JSON — any keys, any types. Structured Output guarantees it matches your specific schema.

Q4: How do you handle a model refusal?
A4: With `parse()`, check `message.refusal` before `message.parsed`. A refusal is not schema data; log it, return a clean error or fallback.

Q5: Your schema is huge and the first request is slow. Why and how to fix?
A5: OpenAI compiles the schema to a grammar on first use and caches it. Large or deeply nested schemas increase that latency and prompt tokens. Fix: simplify the schema, flatten nesting, keep descriptions short, reuse the same schema so cache hits, and keep it under the documented limits for properties and depth.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output feeds code, databases or other APIs
- You need classification, extraction or routing
- You want typed objects and fewer retries

❌ Avoid when:
- You want a creative free-text answer (essay, chat reply)
- The model does not support it (older models) — use tool calling or Instructor
- The schema needs unsupported JSON Schema features

---

## 📊 Visual Diagram
```
 Pydantic class ──► JSON Schema ──► response_format (strict)
                                          │
 User text ───────────────────────────────▼
                                   ┌──────────────┐
                                   │  OpenAI LLM  │
                                   │ constrained  │
                                   │  decoding    │
                                   └──────┬───────┘
                                          ▼
                              {"hs_code": "...", ...}
                                          ▼
                              message.parsed (Pydantic)
```

---

## 💰 Cost Impact
The schema is sent as part of the input, so it counts as input tokens (a 10-field schema is roughly 150-300 tokens). Output is usually shorter than chatty free text because there is no "Sure, here is..." filler. Fewer parse failures means fewer retries, which saves real money.
Optimise: short field names and descriptions, `max_tokens`, `gpt-4o-mini`, reuse one schema (cache), and enable prompt caching by keeping the system prompt identical.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structured Output | Reply forced into a schema | Schema में बंधा जवाब |
| JSON Schema | Language to describe JSON shape | JSON की shape बताने की भाषा |
| strict | Exact schema guarantee | Schema की पक्की guarantee |
| Constrained decoding | Block tokens that break schema | गलत tokens रोकना |
| Refusal | Model declined to answer | Model का मना करना |
| parse() | SDK helper returning Pydantic object | Pydantic object देने वाला helper |

---

## ⚡ 3-Line Summary
English: Structured Output makes OpenAI return JSON that matches your schema, enforced by the API. Use Pydantic with `parse()` and check `refusal`. It guarantees shape, not factual correctness.
Hindi: Structured Output में OpenAI आपके schema जैसा JSON देता है, API इसे enforce करती है। Pydantic और `parse()` use करो और `refusal` check करो। यह shape की guarantee है, facts की नहीं।

---

## ➡️ Next Topic
**084. response_format Parameter** — the exact options (`text`, `json_object`, `json_schema`) and when to pick each.
