---

# 063. JSON Output Prompting
# हिंदी में: JSON Output Prompting — LLM से JSON में जवाब लेना

---

## 🔵 Simple Definition (English)
JSON Output Prompting means writing the prompt so the LLM replies with valid JSON that follows a fixed shape (keys and types). Your code can then parse the reply with `json.loads` instead of reading free text. It is the simplest form of structured output and works with any model.

## 🔵 सरल परिभाषा (Hindi)
JSON Output Prompting में हम prompt ऐसे लिखते हैं कि LLM एक fixed shape (keys और types) वाला valid JSON लौटाए। फिर हमारा code `json.loads` से सीधे parse कर सकता है, free text पढ़ने की ज़रूरत नहीं। यह structured output का सबसे आसान तरीका है और हर model के साथ चलता है।

---

## 🔴 Problem it Solves
Free-text answers are hard to use in software. "The HS code is probably 8517.13, I think" cannot be stored in a database column. Regex on free text breaks when the model changes wording. Downstream services (billing, UI, workflow) need predictable fields.

JSON prompting gives a contract: the model fills `hs_code`, `confidence`, `reason`, and code reads them directly.

## 🔴 यह क्यों बना? (Hindi)
Free text को software में use करना मुश्किल है। "HS code शायद 8517.13 है" को database column में नहीं रख सकते। Model के शब्द बदलते ही regex टूट जाता है। Billing, UI और workflow को predictable fields चाहिए। JSON prompting एक contract देता है: model `hs_code`, `confidence`, `reason` भरता है और code सीधे पढ़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide the schema: keys, types, allowed values
Step 2 → Put the schema + 1-2 examples in the prompt
Step 3 → Say clearly: "Return ONLY valid JSON, no extra text"
Step 4 → Call the model (low temperature, e.g. 0)
Step 5 → Strip code fences if the model added them
Step 6 → json.loads the text
Step 7 → Validate with Pydantic (keys, types, ranges)
Step 8 → If invalid: retry once with the error message
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Schema तय करो: keys, types, allowed values
Step 2 → Prompt में schema + 1-2 examples डालो
Step 3 → साफ़ लिखो: "सिर्फ valid JSON दो, extra text नहीं"
Step 4 → Model call करो (temperature 0 के आसपास)
Step 5 → अगर model ने code fence लगाया तो हटाओ
Step 6 → json.loads से parse करो
Step 7 → Pydantic से validate करो
Step 8 → Invalid हो तो error message के साथ एक बार retry करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A user types "wireless bluetooth earbuds". The prompt asks for JSON: `{"hs_code": "8518.30", "description": "...", "confidence": 0.0-1.0}`. The API layer parses it, saves `hs_code` to the shipment record, and routes low-confidence items (< 0.7) to a human reviewer. Without JSON, the team would need fragile text parsing.

**Zomato-style**: An order-support bot returns `{"intent": "refund", "order_id": "Z123", "urgency": "high"}` so the ticket system can route it automatically.

## 🟡 Real Example Hindi mein
**Tariff System**: User लिखता है "wireless bluetooth earbuds"। Prompt JSON माँगता है: `{"hs_code": "8518.30", "description": "...", "confidence": 0.0-1.0}`। API layer इसे parse करके `hs_code` shipment record में save करती है, और कम confidence (< 0.7) वाले items human reviewer को भेजती है।

**Zomato-style**: Order-support bot `{"intent": "refund", "order_id": "Z123", "urgency": "high"}` लौटाता है ताकि ticket system अपने आप route कर सके।

---

## 💻 Code Example — Basic
```python
# Basic JSON prompting with a fake LLM (runs offline, no API key needed)
import json  # standard library JSON parser

# The prompt: schema + rule + example, all in plain text
PROMPT = """You are a tariff classifier.
Return ONLY valid JSON with exactly these keys:
{"hs_code": string, "description": string, "confidence": number between 0 and 1}
No markdown, no explanation.

Product: wireless bluetooth earbuds"""

def fake_llm(prompt: str) -> str:
    # Pretend LLM: returns JSON wrapped in a code fence (a very common real behaviour)
    return '```json\n{"hs_code": "8518.30", "description": "Headphones and earphones", "confidence": 0.93}\n```'

def extract_json(text: str) -> str:
    # Remove leading/trailing whitespace
    text = text.strip()
    # If the model wrapped the answer in a fence, drop the fence lines
    if text.startswith("```"):
        lines = text.splitlines()          # split into lines
        text = "\n".join(lines[1:-1])      # drop first and last line (the fences)
    return text                            # return the clean JSON string

raw = fake_llm(PROMPT)                     # call the (fake) model
clean = extract_json(raw)                  # clean the text
data = json.loads(clean)                   # parse into a Python dict
print(data["hs_code"])                     # 8518.30
print(data["confidence"] >= 0.7)           # True -> auto-approve
```

## 💻 Code Example — Advanced
```python
# Production style: Pydantic validation + retry with error feedback + async
from __future__ import annotations

import asyncio                                   # for the async version
import json                                      # JSON parsing
import re                                        # to find a JSON object inside text
from typing import Awaitable, Callable           # type hints for the LLM callable

from pydantic import BaseModel, Field, ValidationError  # pydantic v2

class TariffResult(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")      # format like 8518.30
    description: str = Field(min_length=3)               # non-empty text
    confidence: float = Field(ge=0.0, le=1.0)            # probability range

# An LLM is any async function: list of messages -> reply text
LLM = Callable[[list[dict[str, str]]], Awaitable[str]]

JSON_RE = re.compile(r"\{.*\}", re.DOTALL)               # greedy: first { to last }

def parse_reply(text: str) -> TariffResult:
    """Find the JSON object in text and validate it."""
    match = JSON_RE.search(text)                         # look for { ... }
    if match is None:                                    # no JSON at all
        raise ValueError("no JSON object found in reply")
    payload = json.loads(match.group(0))                 # may raise JSONDecodeError
    return TariffResult.model_validate(payload)          # may raise ValidationError

async def classify(llm: LLM, product: str, max_retries: int = 2) -> TariffResult:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": "Reply ONLY with JSON: hs_code (NNNN.NN), description, confidence (0-1)."},
        {"role": "user", "content": f"Product: {product}"},
    ]
    last_error = ""                                      # remember last failure
    for attempt in range(max_retries + 1):               # first try + retries
        reply = await llm(messages)                      # call the model
        try:
            return parse_reply(reply)                    # success path
        except (ValueError, ValidationError) as exc:     # JSONDecodeError is a ValueError
            last_error = str(exc)                        # save the error text
            # Feed the error back so the model can fix its own output
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": f"Invalid JSON: {last_error[:300]}. Return corrected JSON only."})
    raise RuntimeError(f"model failed to return valid JSON: {last_error}")

async def _demo() -> None:
    calls = {"n": 0}                                     # count calls to simulate a bad first reply
    async def flaky_llm(messages: list[dict[str, str]]) -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            return "Sure! The code is 8518.30"           # bad: no JSON
        return '{"hs_code": "8518.30", "description": "Earphones", "confidence": 0.9}'
    result = await classify(flaky_llm, "earbuds")        # retry makes it succeed
    print(result.model_dump())

if __name__ == "__main__":
    asyncio.run(_demo())                                 # run the async demo
```
Token usage: the schema + rule adds ~60-100 input tokens per call; a JSON reply is ~40-60 output tokens. Each retry roughly doubles the cost of that request.

---

## 🟠 FastAPI Integration
FastAPI already speaks JSON and Pydantic. Use the same Pydantic model as `response_model`, so the API contract and the LLM contract are one class.

```python
# FastAPI route that classifies a product and returns validated JSON
from fastapi import FastAPI, HTTPException        # web framework + HTTP errors
from pydantic import BaseModel                    # request model
from openai import AsyncOpenAI                    # openai>=1 async client

app = FastAPI()                                   # create the app
client = AsyncOpenAI()                            # reads OPENAI_API_KEY from env

class Query(BaseModel):
    product: str                                  # request body field

async def openai_llm(messages: list[dict[str, str]]) -> str:
    resp = await client.chat.completions.create(  # call chat completions
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,                            # deterministic output
        max_tokens=200,                           # cap output tokens
    )
    return resp.choices[0].message.content or ""  # content can be None

@app.post("/classify", response_model=TariffResult)   # TariffResult from the advanced block
async def classify_route(q: Query) -> TariffResult:
    try:
        return await classify(openai_llm, q.product)  # validated object
    except RuntimeError as exc:                       # model never produced valid JSON
        raise HTTPException(status_code=502, detail=str(exc)) from exc
```

---

## 🔗 LangChain / LangGraph Connection
LangChain gives `JsonOutputParser` and `PydanticOutputParser` which add format instructions to the prompt and parse the reply. In LCEL: `prompt | llm | parser`. In LangGraph, a node can call this chain and store the parsed dict in the graph state.

```python
from langchain_core.prompts import ChatPromptTemplate        # prompt template
from langchain_core.output_parsers import PydanticOutputParser  # parser
from langchain_openai import ChatOpenAI                      # chat model

parser = PydanticOutputParser(pydantic_object=TariffResult)  # knows the schema
prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the product.\n{format_instructions}"),  # parser adds schema text
    ("user", "{product}"),
]).partial(format_instructions=parser.get_format_instructions())
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | parser  # LCEL chain
# result = await chain.ainvoke({"product": "earbuds"})       # returns TariffResult
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting the raw reply
✅ Correct: Parse and validate every time.
```python
# Wrong: crashes if the model adds "Here is the JSON:" or a code fence
data = json.loads(reply)

# Right: extract, parse, validate, and retry on failure
result = parse_reply(reply)
```

❌ Mistake 2: Describing the schema vaguely
✅ Correct: Give exact keys, types, allowed values, and one example.
```python
# Wrong
prompt = "Give me the tariff info as JSON"

# Right
prompt = 'Return JSON: {"hs_code": "NNNN.NN", "confidence": 0.0-1.0}. Example: {"hs_code": "8518.30", "confidence": 0.9}'
```

❌ Mistake 3: High temperature for structured output
✅ Correct: Use temperature 0 to 0.2 so format stays stable.

---

## 🧠 Tricky Interview Question
**Q**: "Your JSON prompt works 98% of the time. At 1M requests/day, 2% failures are 20,000 broken requests. What do you do?"

**Answer**: 98% is not production-ready. Layer defences: (1) use the provider's JSON mode or structured outputs (schema enforced by decoding, ~100%), (2) validate with Pydantic, (3) retry once with the validation error in the prompt, (4) fall back to a safe default or human queue, (5) log failures and add them to the test set. Prompting alone gives probability; constrained decoding gives a guarantee.

---

## ⚫ Interview Questions + Answers

Q1: Why ask an LLM for JSON?
A1: So code can parse the reply directly. Fixed keys and types remove fragile text parsing and let the answer flow into databases, APIs and workflows.

Q2: Why set temperature low for JSON output?
A2: High temperature increases randomness, which can break syntax or change key names. Temperature 0 to 0.2 keeps the format stable.

Q3: Models often wrap JSON in markdown fences. How do you handle it?
A3: First, tell the model "no markdown". Second, in code strip fences or extract the first `{...}` with a regex. Third, prefer JSON mode / structured outputs which return pure JSON.

Q4: What is the difference between JSON prompting and JSON mode?
A4: JSON prompting is just an instruction; the model may still fail. JSON mode is an API setting that guarantees syntactically valid JSON, but not your schema. Structured outputs (schema-constrained) guarantee the schema too.

Q5 (Hard): How do you make a JSON pipeline robust across multiple model providers?
A5: Define one Pydantic schema as the source of truth. Per provider, use the strongest native feature (OpenAI structured outputs, Anthropic tool use with an input schema, etc.), and keep a shared fallback: extract, parse, validate, retry with the error. Add an eval set of tricky inputs and track the parse-success rate per model, so a model upgrade cannot silently break the format.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output feeds code (database, API, UI, workflow)
- You need classification, extraction or routing
- You work with a model that has no native structured output

❌ Avoid when:
- The answer is for a human to read (chat reply, essay)
- Native structured outputs are available and you need guarantees (use those)
- The schema is huge and deeply nested (accuracy drops; split into steps)

---

## 📊 Visual Diagram
```
 Prompt (schema + rules + example)
              |
              v
        +-----------+
        |    LLM    |  temperature = 0
        +-----------+
              |
        raw text reply
              |
              v
   strip fences / extract {...}
              |
              v
        json.loads  ---- error ----+
              |                    |
              v                    |
      Pydantic validate -- error --+--> retry with error message
              |
              v
        typed Python object --> DB / API / UI
```

---

## 💰 Cost Impact
- Schema and examples add input tokens on every call (about 60-150 tokens).
- JSON syntax (quotes, braces, key names) costs output tokens. Use short key names (`hs` vs `harmonized_system_code`) when volume is high.
- Each retry pays for input + output again.

Optimisation: keep schema compact, cap `max_tokens`, use temperature 0, use a cheap model (gpt-4o-mini) for extraction, and use prompt caching for the fixed schema prefix.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSON | Text format of keys and values | Keys-values वाला text format |
| Schema | Expected keys and types | अपेक्षित keys और types का ढाँचा |
| Parse | Convert text to objects | Text को object में बदलना |
| Validation | Check data fits the schema | Data schema से मेल खाता है या नहीं जाँचना |
| Code fence | Markdown ``` wrapper | Markdown का ``` लपेटा |
| Retry | Call again after failure | Fail होने पर दोबारा call |

---

## ⚡ 3-Line Summary
English: JSON output prompting makes the model reply in a fixed machine-readable shape. Always extract, parse and validate, and retry with the error. For guarantees, use native JSON mode or structured outputs.
Hindi: JSON output prompting से model fixed machine-readable shape में जवाब देता है। हमेशा extract, parse और validate करो, और error के साथ retry करो। Guarantee चाहिए तो native JSON mode या structured outputs use करो।

---

## ➡️ Next Topic
**064. Markdown Output Prompting** — when the answer is for humans (reports, chat UI), format it with headings, lists and tables instead of JSON.
