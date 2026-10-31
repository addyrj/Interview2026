---

# 086. Instructor Library
# हिंदी में: Instructor Library

---

## 🔵 Simple Definition (English)
Instructor is a small open-source Python library that wraps an LLM client (OpenAI, Anthropic, Gemini and others). You pass `response_model=YourPydanticClass` and it returns a validated object. If validation fails, it automatically re-asks the model with the error message, up to `max_retries` times.

## 🔵 सरल परिभाषा (Hindi)
Instructor एक छोटी open-source Python library है जो LLM client (OpenAI, Anthropic, Gemini आदि) को wrap करती है। आप `response_model=YourPydanticClass` देते हो और यह validated object लौटाती है। Validation fail हो तो error message के साथ model से अपने-आप दोबारा पूछती है, `max_retries` बार तक।

---

## 🔴 Problem it Solves
Native structured output differs per provider, and the retry-on-failure loop is something every team re-writes. Instructor gives one consistent API: same code works across providers, with automatic retry and Pydantic validation feedback to the model.

## 🔴 यह क्यों बना? (Hindi)
हर provider का native structured output अलग है, और failure पर retry loop हर team दोबारा लिखती है। Instructor एक consistent API देता है: वही code कई providers पर चलता है, automatic retry और Pydantic validation का feedback model को जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install instructor
Step 2 → client = instructor.from_openai(OpenAI())  (patches the client)
Step 3 → Call client.chat.completions.create(response_model=Model, max_retries=3, ...)
Step 4 → Instructor converts Model to a tool/schema and calls the LLM
Step 5 → Reply is validated with Pydantic
Step 6 → If invalid: error text is appended to messages and the LLM is called again
Step 7 → Returns a Model instance, or raises InstructorRetryException after retries
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pip install instructor
Step 2 → client = instructor.from_openai(OpenAI())  (client को patch करता है)
Step 3 → client.chat.completions.create(response_model=Model, max_retries=3, ...) call करो
Step 4 → Instructor Model को tool/schema में बदलकर LLM बुलाता है
Step 5 → Reply Pydantic से validate होती है
Step 6 → Invalid हो तो error text messages में जुड़कर LLM फिर बुलाया जाता है
Step 7 → Model instance लौटता है, या retries के बाद InstructorRetryException
```

---

## 🟡 Real World Example
**Tariff Classification System**: A validator says the HS code must exist in our tariff table. When the LLM returns "8518.99" which is not in the table, Instructor sends back "HS code 8518.99 not found, choose from the list" and the second attempt is correct, without us writing any loop.

**Amazon-style**: Extracting `brand`, `model`, `price` from messy seller titles with auto-correction on bad prices.

## 🟡 Real Example Hindi mein
**Tariff System**: एक validator कहता है कि HS code हमारे tariff table में होना चाहिए। LLM "8518.99" देता है जो table में नहीं, तो Instructor "HS code 8518.99 not found, list में से चुनो" वापस भेजता है और दूसरी कोशिश सही आती है — हमने कोई loop नहीं लिखा।

**Amazon-style**: Messy seller titles से `brand`, `model`, `price` निकालना, गलत price पर auto-correction के साथ।

---

## 💻 Code Example — Basic
```python
# Basic: the Instructor idea in pure Python — validate, then re-ask with the error.
# (The real library does exactly this loop for you.)
from typing import Callable                       # type hint for the fake LLM

VALID_CODES: set[str] = {"8518.30", "8517.13"}    # our tariff table

def fake_llm(messages: list[str], attempt: int) -> str:
    """Pretend LLM: wrong on attempt 0, right on attempt 1."""
    return "8518.99" if attempt == 0 else "8518.30"   # first answer is wrong

def validate(code: str) -> str:
    """Raise ValueError if the code is not in the table."""
    if code not in VALID_CODES:                   # business rule
        raise ValueError(f"HS code {code} not found, choose from {sorted(VALID_CODES)}")
    return code                                   # valid

def ask_with_retry(llm: Callable[[list[str], int], str], max_retries: int = 3) -> str:
    """Call LLM, validate, feed the error back on failure."""
    messages: list[str] = ["Classify: wireless earbuds"]   # conversation so far
    for attempt in range(max_retries):            # bounded loop = bounded cost
        raw = llm(messages, attempt)              # get answer
        try:
            return validate(raw)                  # success -> return
        except ValueError as exc:                 # validation failed
            print(f"attempt {attempt}: {exc}")    # log
            messages.append(f"Your answer {raw} was invalid: {exc}")   # feedback to LLM
    raise RuntimeError("gave up after retries")   # all attempts failed

print("Final:", ask_with_retry(fake_llm))         # prints retry log then 8518.30
```

## 💻 Code Example — Advanced
```python
# Production: Instructor + async OpenAI + validator + usage tracking.
# pip install instructor openai pydantic
import asyncio                                         # async runner
import instructor                                      # the library
from openai import AsyncOpenAI                         # async client
from pydantic import BaseModel, Field, field_validator # schema + rules
try:                                                   # import path differs by version
    from instructor.core.exceptions import InstructorRetryException   # newer versions
except ImportError:
    from instructor.exceptions import InstructorRetryException        # older versions

VALID_CODES: set[str] = {"8518.30", "8517.13", "8471.30"}   # demo table

client = instructor.from_openai(AsyncOpenAI())         # patched async client

class TariffResult(BaseModel):
    hs_code: str = Field(description="6-digit HS code, format 8518.30")
    duty_percent: float = Field(ge=0, le=100)

    @field_validator("hs_code")
    @classmethod
    def must_exist(cls, v: str) -> str:
        if v not in VALID_CODES:                       # error text goes back to the LLM
            raise ValueError(f"{v} not in tariff table: {sorted(VALID_CODES)}")
        return v

async def classify(product: str) -> TariffResult | None:
    """Return validated result or None if all retries failed."""
    try:
        result, raw = await client.chat.completions.create_with_completion(
            model="gpt-4o-mini",
            response_model=TariffResult,               # the magic parameter
            max_retries=3,                             # auto re-ask up to 3 times
            messages=[{"role": "user", "content": f"Classify for customs: {product}"}],
            temperature=0,
        )
        print("tokens:", raw.usage.total_tokens)       # includes retries' tokens
        return result
    except InstructorRetryException as exc:            # validation never passed
        print("Failed after retries:", exc)
        return None

if __name__ == "__main__":
    print(asyncio.run(classify("Wireless earbuds")))   # needs API key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/classify", response_model=TariffResult)
async def classify_route(product: str) -> TariffResult:
    result = await classify(product)                   # Instructor handles retries
    if result is None:
        raise HTTPException(status_code=422, detail="Unable to produce valid classification")
    return result
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangChain has with_structured_output() and RetryOutputParser / with_retry();
# Instructor is an alternative, not a requirement.
# Use Instructor inside a LangGraph node when you want validator-driven retries:
async def classify_node(state: dict) -> dict:
    result = await classify(state["product"])          # Instructor call
    return {"tariff": result}                          # write to graph state
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Huge `max_retries` (like 10)
✅ Correct: 2-3 retries; each retry resends the whole conversation and costs tokens.

```python
# Wrong: max_retries=10   -> a bad schema can burn 10x tokens
# Right: max_retries=2, then fallback to human review
```

❌ Mistake 2: Validators with vague messages
✅ Correct: Messages tell the LLM how to fix it.

```python
# Wrong: raise ValueError("invalid")
# Right: raise ValueError(f"{v} not in tariff table, choose from {codes}")
```

---

## 🧠 Tricky Interview Question

**Q**: "Instructor retried 3 times and your bill doubled for a batch job. Where did the cost come from and how do you cut it?"

**Answer**: Each retry resends the original prompt plus the failed answer plus the error, so input tokens grow every attempt (about 2-4x for 3 retries). Fixes: improve the prompt and descriptions so the first try passes, put valid options in the schema as an `Enum`/`Literal` so invalid values are impossible, lower `max_retries`, and monitor the retry rate.

---

## ⚫ Interview Questions + Answers

Q1: What is Instructor?
A1: A library that adds `response_model` and retry-with-validation on top of LLM clients.

Q2: What does `max_retries` do?
A2: On validation failure, it re-calls the model, adding the error text, up to that many times.

Q3: How is Instructor different from `parse()` of OpenAI?
A3: `parse()` is OpenAI-only and does not re-ask on semantic failures; Instructor is multi-provider and retries using validator messages.

Q4: Which modes can Instructor use under the hood?
A4: Tool calling (default for OpenAI), JSON mode, and native structured-output modes (`Mode.JSON_SCHEMA`/`TOOLS_STRICT`), chosen via `from_openai(client, mode=...)`.

Q5: How do you track total tokens with retries?
A5: Use `create_with_completion` and read `raw.usage`, which Instructor accumulates across attempts; also log via hooks or a proxy like LangSmith/Helicone.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need validator-driven self-correction
- You support several LLM providers
- You want streaming partial objects

❌ Avoid when:
- OpenAI strict `parse()` already meets your needs
- You cannot afford extra retry tokens
- You want fewer dependencies

---

## 📊 Visual Diagram
```
 messages + response_model
        │
        ▼
   ┌─────────┐    JSON     ┌───────────────┐
   │   LLM   │───────────► │ Pydantic check│
   └─────────┘             └──────┬────────┘
        ▲        invalid          │ valid
        └── add error text ◄──────┤
            (attempt < max)       ▼
                              return object
```

---

## 💰 Cost Impact
Happy path: same as a normal call plus schema tokens. Each retry adds the full previous prompt + bad answer + error (roughly doubles the input per attempt).
Optimise: use Literal/Enum to prevent invalid values, clear validator messages, `max_retries=2`, cheap model first then escalate, cache the prefix.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Instructor | Library for structured LLM output | Structured output library |
| response_model | Pydantic class to return | लौटने वाली Pydantic class |
| max_retries | Re-ask limit | दोबारा पूछने की सीमा |
| Self-correction | LLM fixes its answer from error | खुद सुधार |
| Mode | How schema is sent (tools/json) | Schema भेजने का तरीका |

---

## ⚡ 3-Line Summary
English: Instructor wraps LLM clients and returns Pydantic objects via `response_model`. It retries automatically with validator error messages. Keep retries low because each one costs tokens.
Hindi: Instructor LLM clients को wrap करके `response_model` से Pydantic objects देता है। यह validator के error messages के साथ अपने-आप retry करता है। Retries कम रखो क्योंकि हर retry में tokens लगते हैं।

---

## ➡️ Next Topic
**087. Structured Output in Claude** — Anthropic has no `response_format`; learn how Claude does it with tool use and prefill.
