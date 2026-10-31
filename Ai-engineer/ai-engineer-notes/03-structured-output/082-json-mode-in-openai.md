---

# 082. JSON Mode in OpenAI
# हिंदी में: OpenAI में JSON Mode

---

## 🔵 Simple Definition (English)
JSON mode is an OpenAI API setting, `response_format={"type": "json_object"}`, that forces the model's reply to be syntactically valid JSON. It does NOT enforce your keys or types; for that you need Structured Outputs with a JSON Schema (`response_format={"type": "json_schema", ...}`). The prompt must also tell the model to produce JSON (the word "JSON" must appear in the messages), or the API returns an error.

## 🔵 सरल परिभाषा (Hindi)
JSON mode OpenAI API की एक setting है, `response_format={"type": "json_object"}`, जो model के reply को syntactically valid JSON बनाने पर मजबूर करती है। यह आपके keys या types लागू नहीं करती; उसके लिए JSON Schema वाला Structured Outputs चाहिए (`response_format={"type": "json_schema", ...}`)। Prompt में model को JSON देने को कहना भी ज़रूरी है (messages में "JSON" शब्द होना चाहिए), वरना API error देता है।

---

## 🔴 Problem it Solves
With prompt-only JSON (topic 063), the model sometimes adds text, a code fence or a trailing comma, and `json.loads` fails. JSON mode removes the syntax problem: the reply always parses (unless cut off by the token limit). It was the first step toward reliable structured data; Structured Outputs later added schema adherence.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ prompt वाले JSON (topic 063) में model कभी text, code fence या अतिरिक्त comma जोड़ देता है और `json.loads` फेल होता है। JSON mode syntax की समस्या हटाता है: reply हमेशा parse होता है (जब तक token limit से कट न जाए)। यह भरोसेमंद structured data की तरफ पहला कदम था; बाद में Structured Outputs ने schema का पालन जोड़ा।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Set response_format={"type": "json_object"} in the request
Step 2 → Include instructions in system/user message that mention JSON and describe the keys
Step 3 → Model decodes with a JSON-syntax constraint
Step 4 → Reply is valid JSON text (an object)
Step 5 → Check finish_reason: "length" means the JSON may be cut off and invalid
Step 6 → json.loads, then validate keys/types with Pydantic (JSON mode does not do this)
Step 7 → On failure: retry with the validation error, or fall back

JSON mode  = valid JSON syntax
Structured Outputs (json_schema, strict) = valid JSON + matches your schema
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request में response_format={"type": "json_object"} सेट करो
Step 2 → System/user message में JSON का ज़िक्र करो और keys बताओ
Step 3 → Model JSON-syntax constraint के साथ decode करता है
Step 4 → Reply valid JSON text (एक object) होता है
Step 5 → finish_reason देखो: "length" का मतलब JSON कट सकता है और invalid हो सकता है
Step 6 → json.loads, फिर Pydantic से keys/types validate करो (JSON mode यह नहीं करता)
Step 7 → फेल होने पर: validation error के साथ retry या fallback

JSON mode  = valid JSON syntax
Structured Outputs (json_schema, strict) = valid JSON + आपके schema से मेल
```

---

## 🟡 Real World Example
**Tariff Classification System**: A quick extraction endpoint pulls `{"product": ..., "material": ..., "country_of_origin": ...}` from messy invoice lines. JSON mode guarantees the reply parses. Because keys are not enforced, the code uses Pydantic with defaults to handle a missing `material`. For the final HS classification (where a wrong enum value is costly) the team uses strict Structured Outputs instead.

**Zomato-style**: Extract `{"dish": ..., "quantity": ...}` from a free-text order message.

## 🟡 Real Example Hindi mein
**Tariff System**: एक quick extraction endpoint गंदी invoice lines से `{"product": ..., "material": ..., "country_of_origin": ...}` निकालता है। JSON mode गारंटी देता है कि reply parse होगा। Keys लागू नहीं होते, इसलिए code Pydantic defaults से missing `material` संभालता है। अंतिम HS classification के लिए (जहाँ गलत enum value महँगी है) team strict Structured Outputs इस्तेमाल करती है।

**Zomato-style**: Free-text order message से `{"dish": ..., "quantity": ...}` निकालना।

---

## 💻 Code Example — Basic
```python
# Basic: JSON mode request + parse (needs: pip install openai>=1 and OPENAI_API_KEY)
# A fake client is used when no key is set so the script still runs.
import json   # parse the reply
import os     # read the API key from the environment

def fake_reply(messages: list[dict[str, str]]) -> str:
    return '{"product": "wireless earbuds", "material": "plastic", "country_of_origin": "CN"}'

def extract(text: str) -> dict:
    messages = [
        # The word JSON must appear in the messages when JSON mode is on
        {"role": "system", "content": "Extract fields as JSON with keys: product, material, country_of_origin."},
        {"role": "user", "content": text},
    ]
    if os.getenv("OPENAI_API_KEY"):                              # real call
        from openai import OpenAI                                # sync client for the basic example
        client = OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"},             # JSON mode
            temperature=0,
            max_tokens=200,
        )
        choice = resp.choices[0]
        if choice.finish_reason == "length":                     # output was cut off
            raise ValueError("truncated JSON")
        raw = choice.message.content or "{}"
    else:
        raw = fake_reply(messages)                               # offline stand-in
    return json.loads(raw)                                       # valid JSON, but keys not guaranteed

print(extract("2000 pcs wireless earbuds, plastic, made in China"))
```

## 💻 Code Example — Advanced
```python
# Production: JSON mode with Pydantic validation, truncation check, repair retry and metrics (async)
from __future__ import annotations

import asyncio                                    # async runner
import json                                       # parse
from typing import Awaitable, Callable            # type hints

from pydantic import BaseModel, ValidationError   # pydantic v2

class Extracted(BaseModel):
    product: str                                  # required
    material: str | None = None                   # optional (JSON mode may omit it)
    country_of_origin: str | None = None          # optional

# call(messages) -> (text, finish_reason, total_tokens). Injected for testability.
Call = Callable[[list[dict[str, str]]], Awaitable[tuple[str, str, int]]]

async def extract_json_mode(call: Call, text: str, retries: int = 2) -> tuple[Extracted, int]:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": "Return a JSON object with keys product (string), "
                                      "material (string or null), country_of_origin (ISO code or null)."},
        {"role": "user", "content": text},
    ]
    tokens_used = 0                                              # total tokens across attempts
    last_error = ""
    for _ in range(retries + 1):
        try:
            raw, finish, tokens = await call(messages)           # API call
        except Exception as exc:                                 # network / rate limit
            raise RuntimeError(f"OpenAI call failed: {exc}") from exc
        tokens_used += tokens
        if finish == "length":                                   # truncated: retry with room, don't parse
            last_error = "output truncated"
            continue
        try:
            return Extracted.model_validate(json.loads(raw)), tokens_used   # success
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = str(exc)[:200]                          # schema mismatch (JSON mode allows this)
            messages += [{"role": "assistant", "content": raw},
                         {"role": "user", "content": f"Fix this JSON error: {last_error}. Return JSON only."}]
    raise RuntimeError(f"could not get valid JSON: {last_error}")

async def _demo() -> None:
    state = {"n": 0}
    async def call(messages: list[dict[str, str]]) -> tuple[str, str, int]:
        state["n"] += 1
        if state["n"] == 1:
            return '{"name": "earbuds"}', "stop", 80              # valid JSON but wrong key (typical JSON mode gap)
        return '{"product": "earbuds", "material": null, "country_of_origin": "CN"}', "stop", 90
    print(await extract_json_mode(call, "earbuds from China"))

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: JSON mode adds no extra input tokens by itself, but your instructions describing keys do (~40-80 tokens). Retries after schema mismatches double the cost, which is a reason to move critical paths to strict Structured Outputs.

---

## 🟠 FastAPI Integration
Use `AsyncOpenAI` created once; return a Pydantic `response_model`; translate failures into proper HTTP codes.

```python
from fastapi import FastAPI, HTTPException        # framework
from openai import AsyncOpenAI                    # openai>=1
from pydantic import BaseModel                    # models

app = FastAPI()                                   # app
client = AsyncOpenAI()                            # client

class In(BaseModel):
    text: str                                     # invoice line text

async def openai_call(messages: list[dict[str, str]]) -> tuple[str, str, int]:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, temperature=0, max_tokens=250,
        response_format={"type": "json_object"})         # JSON mode
    c = r.choices[0]
    return c.message.content or "{}", c.finish_reason, (r.usage.total_tokens if r.usage else 0)

@app.post("/extract", response_model=Extracted)          # Extracted from the advanced block
async def extract_route(body: In) -> Extracted:
    try:
        item, _tokens = await extract_json_mode(openai_call, body.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return item
```

---

## 🔗 LangChain / LangGraph Connection
`ChatOpenAI(...).bind(response_format={"type": "json_object"})` enables JSON mode; pair it with `JsonOutputParser` or `PydanticOutputParser`. `with_structured_output(Model, method="json_mode")` also exists; for strict schema enforcement use `method="json_schema"` (the default in recent versions for supported OpenAI models; check your installed version).

```python
from langchain_core.output_parsers import JsonOutputParser        # parser
from langchain_core.prompts import ChatPromptTemplate             # prompt
from langchain_openai import ChatOpenAI                           # model

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind(response_format={"type": "json_object"})
prompt = ChatPromptTemplate.from_messages([
    ("system", "Return JSON with keys product, material, country_of_origin."),   # mentions JSON
    ("user", "{text}")])
chain = prompt | llm | JsonOutputParser()
# data = await chain.ainvoke({"text": "2000 pcs wireless earbuds from China"})   # returns dict
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Enabling JSON mode without mentioning JSON in the prompt
✅ Correct: Include "JSON" and describe the keys.
```python
# Wrong: API error (messages must contain the word "JSON")
messages = [{"role": "user", "content": "Extract product details"}]

# Right
messages = [{"role": "system", "content": "Return JSON with keys product, material."},
            {"role": "user", "content": text}]
```

❌ Mistake 2: Assuming JSON mode enforces your schema
✅ Correct: Validate with Pydantic or use Structured Outputs (json_schema, strict).
```python
# Wrong
data = json.loads(reply)
price = data["price"]            # KeyError if the model chose another key name

# Right
item = Extracted.model_validate_json(reply)
```

❌ Mistake 3: Ignoring `finish_reason == "length"`. Truncated output is invalid JSON; raise `max_tokens` or shorten the output.

---

## 🧠 Tricky Interview Question
**Q**: "JSON mode is on, yet `json.loads` still fails in about 0.5% of requests. How is that possible?"

**Answer**: The most common cause is truncation: when the output hits `max_tokens` (finish_reason `length`) the JSON is cut mid-object. Other causes: a refusal or content filter result (finish_reason `content_filter`), whitespace-only streams in edge cases (the model emitting endless whitespace if not told to produce JSON), or parsing a streamed partial response. Fixes: check `finish_reason` before parsing, set a larger `max_tokens`, always instruct the model to produce JSON, handle refusals, and retry with validation feedback or switch to strict Structured Outputs.

---

## ⚫ Interview Questions + Answers

Q1: What does JSON mode guarantee?
A1: That the reply is valid JSON syntax (a JSON object), assuming it was not truncated.

Q2: What does it not guarantee?
A2: It does not guarantee your keys, types or enum values, nor that the content is correct.

Q3: What is a requirement when using JSON mode?
A3: The conversation must instruct the model to produce JSON (the word "JSON" must appear in the messages), otherwise the API returns an error.

Q4: JSON mode vs Structured Outputs?
A4: JSON mode: valid JSON only. Structured Outputs (`json_schema` with `strict: true`, or `client.beta.chat.completions.parse` with a Pydantic class): valid JSON that matches your schema. Prefer Structured Outputs on models that support them.

Q5 (Hard): Design a migration from prompt-only JSON to strict Structured Outputs for a high-volume service.
A5: Measure baseline parse-failure, schema-failure and retry rates and cost. Define Pydantic models; shadow-run the new path on a sample, compare field-level accuracy against the old path and human labels; check schema support limits (required fields, nesting, enums); roll out via canary with alerts on refusals and truncations; keep a fallback to JSON mode plus validation if the new path errors; update tests, and track token cost since schemas add input tokens while removing retries.

---

## 🔷 When to Use + When Not to Use
✅ Use JSON mode when:
- You need valid JSON quickly and keys are flexible or validated by you
- The model or API version does not support strict schemas
- Simple extraction or prototypes

❌ Avoid when:
- You need exact keys/enums (use Structured Outputs)
- The reply is for humans
- Outputs may be long and truncated without handling

---

## 📊 Visual Diagram
```
 Prompt only        JSON mode                   Structured Outputs (strict)
 -----------        ---------                   ---------------------------
 may add text       valid JSON syntax           valid JSON
 may break JSON     keys/types NOT enforced     keys/types/enums enforced
       |                  |                              |
   regex+retry       json.loads + Pydantic          parse directly (+ semantic checks)

 Always check: finish_reason == "length" ?  -> truncated, do not trust the JSON
```

---

## 💰 Cost Impact
- JSON mode adds no surcharge; you pay normal input and output tokens.
- Instructions describing the keys add ~40-80 input tokens per request; cache them via the static prefix.
- Schema mismatches cause retries (extra tokens). Track the retry rate: if above about 1-2% on a critical path, strict Structured Outputs are usually cheaper overall.
- Use short key names and `max_tokens` close to the expected size to avoid wasted output.

Optimisation: gpt-4o-mini for extraction, temperature 0, a compact prompt, response caching for repeated inputs, and validation with one targeted repair retry.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JSON mode | Forces valid JSON syntax | Valid JSON syntax की बाध्यता |
| response_format | API field to choose output mode | Output mode चुनने वाला API field |
| finish_reason | Why generation stopped | Generation क्यों रुका |
| Truncation | Output cut by token limit | Token limit से output का कटना |
| Strict schema | Enforced keys and types | लागू किए गए keys और types |
| Repair retry | Retry with error feedback | Error बताकर दोबारा कोशिश |

---

## ⚡ 3-Line Summary
English: OpenAI JSON mode (`response_format={"type": "json_object"}`) guarantees valid JSON syntax but not your keys or types. Mention JSON in the prompt, check `finish_reason` for truncation, and validate with Pydantic. Use strict Structured Outputs when the schema must be exact.
Hindi: OpenAI JSON mode (`response_format={"type": "json_object"}`) valid JSON syntax की गारंटी देता है, आपके keys या types की नहीं। Prompt में JSON का ज़िक्र करो, truncation के लिए `finish_reason` देखो और Pydantic से validate करो। Schema सटीक चाहिए तो strict Structured Outputs इस्तेमाल करो।

---

## ➡️ Next Topic
**083. Structured Outputs with JSON Schema (strict)** — enforcing exact schemas with `json_schema` and Pydantic parsing, plus its limits.
