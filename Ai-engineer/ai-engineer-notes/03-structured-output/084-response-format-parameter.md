---

# 084. response_format Parameter
# हिंदी में: response_format Parameter

---

## 🔵 Simple Definition (English)
`response_format` is a parameter of the OpenAI Chat Completions API that controls the shape of the reply. It has three modes: `{"type": "text"}` (default, free text), `{"type": "json_object"}` (any valid JSON) and `{"type": "json_schema", ...}` (JSON that matches your schema).

## 🔵 सरल परिभाषा (Hindi)
`response_format` OpenAI Chat Completions API का parameter है जो reply की shape control करता है। इसके तीन modes हैं: `text` (default, free text), `json_object` (कोई भी valid JSON) और `json_schema` (आपके schema से match करने वाला JSON)।

---

## 🔴 Problem it Solves
Without it, the only lever was the prompt. Prompts are suggestions, not rules. Developers needed a switch at the API level: "this reply must be JSON" or "this reply must follow this exact schema". Different tasks need different strength of guarantee, so there are three levels.

## 🔴 यह क्यों बना? (Hindi)
इसके बिना सिर्फ prompt का सहारा था। Prompt सुझाव होता है, rule नहीं। Developers को API level पर switch चाहिए था: "reply JSON ही हो" या "reply इसी schema में हो"। अलग tasks को अलग strength की guarantee चाहिए, इसलिए तीन levels हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a mode: text | json_object | json_schema
Step 2 → text: no constraint, model writes anything
Step 3 → json_object: output must parse as JSON, but keys are free.
         You MUST also say the word "JSON" in the prompt, or the API errors
Step 4 → json_schema: send {"name", "strict", "schema"}
Step 5 → API validates the schema first (400 error if unsupported)
Step 6 → Decoding is constrained, reply returned in message.content
Step 7 → You json.loads() it (or use parse() for Pydantic)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Mode चुनो: text | json_object | json_schema
Step 2 → text: कोई constraint नहीं, model कुछ भी लिखे
Step 3 → json_object: output valid JSON होगा, पर keys free हैं।
         Prompt में "JSON" शब्द लिखना ज़रूरी है वरना API error देती है
Step 4 → json_schema: {"name", "strict", "schema"} भेजो
Step 5 → API पहले schema validate करती है (unsupported हो तो 400 error)
Step 6 → Decoding constrained होती है, reply message.content में आता है
Step 7 → आप json.loads() करो (या Pydantic के लिए parse())
```

---

## 🟡 Real World Example
**Tariff Classification System**: Three endpoints in one app.
- `/explain` uses `text` — a human-readable explanation of why a code was chosen.
- `/quick-tags` uses `json_object` — loose keyword tags for a prototype.
- `/classify` uses `json_schema` strict — the billing-safe result.

**Amazon-style**: Product title cleaning returns a strict schema; "write a product description" stays `text`.

## 🟡 Real Example Hindi mein
**Tariff System**: एक app में तीन endpoints।
- `/explain` में `text` — code क्यों चुना, इसकी human-readable explanation।
- `/quick-tags` में `json_object` — prototype के लिए ढीले keyword tags।
- `/classify` में `json_schema` strict — billing के लिए safe result।

**Amazon-style**: Product title cleaning strict schema में; "product description लिखो" `text` में।

---

## 💻 Code Example — Basic
```python
# Basic: build the three response_format payloads and pick one by task.
# Pure Python, runs offline.
from typing import Any                          # type hint

def build_response_format(mode: str) -> dict[str, Any]:
    """Return the response_format dict for a given mode."""
    if mode == "text":                          # default behaviour
        return {"type": "text"}                 # free text
    if mode == "json_object":                   # any valid JSON
        return {"type": "json_object"}          # remember: prompt must say "JSON"
    if mode == "json_schema":                   # strict schema
        schema: dict[str, Any] = {              # minimal schema
            "type": "object",
            "properties": {"hs_code": {"type": "string"}},   # one field
            "required": ["hs_code"],                         # strict: all required
            "additionalProperties": False,                   # strict: no extras
        }
        return {
            "type": "json_schema",
            "json_schema": {"name": "hs", "strict": True, "schema": schema},
        }
    raise ValueError(f"unknown mode: {mode}")   # guard against typos

for m in ("text", "json_object", "json_schema"):  # show all three
    print(m, "->", build_response_format(m))      # print the payload

# Usage with the SDK (needs API key):
# client.chat.completions.create(model="gpt-4o-mini", messages=msgs,
#                                response_format=build_response_format("json_schema"))
try:
    build_response_format("xml")                # invalid mode
except ValueError as exc:                       # error handling demo
    print("Caught:", exc)
```

## 💻 Code Example — Advanced
```python
# Production: one helper that picks the mode, validates reply, async + errors.
import asyncio                                   # async runner
import json                                      # parse reply
from typing import Any, Literal                  # type hints
from openai import AsyncOpenAI, BadRequestError, OpenAIError   # SDK + errors

client = AsyncOpenAI()                           # key from OPENAI_API_KEY
Mode = Literal["text", "json_object", "json_schema"]            # allowed modes

HS_SCHEMA: dict[str, Any] = {                    # strict schema for tariff
    "type": "object",
    "properties": {
        "hs_code": {"type": "string"},
        "duty_percent": {"type": "number"},
    },
    "required": ["hs_code", "duty_percent"],
    "additionalProperties": False,
}

def make_format(mode: Mode) -> dict[str, Any]:
    """Create response_format for the chosen mode."""
    if mode == "json_schema":
        return {"type": "json_schema",
                "json_schema": {"name": "tariff", "strict": True, "schema": HS_SCHEMA}}
    return {"type": mode}                        # text or json_object

async def ask(product: str, mode: Mode = "json_schema") -> dict[str, Any] | str:
    """Call the model with the chosen response_format."""
    system = "You classify products. Reply in JSON."   # 'JSON' word needed for json_object
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": product}],
            response_format=make_format(mode),   # <-- the parameter
            max_tokens=200,                      # bound the cost
        )
    except BadRequestError as exc:               # bad schema or missing 'JSON' word
        raise ValueError(f"Invalid request: {exc}") from exc
    except OpenAIError as exc:                   # all other API errors
        raise RuntimeError(f"API failure: {exc}") from exc
    choice = resp.choices[0]                     # first answer
    if choice.finish_reason == "length":         # output was cut -> JSON broken
        raise RuntimeError("Truncated output, raise max_tokens")
    content = choice.message.content or ""       # may be None on refusal
    return content if mode == "text" else json.loads(content)   # parse JSON modes

if __name__ == "__main__":
    print(asyncio.run(ask("Bluetooth earbuds")))  # needs API key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Query, HTTPException    # web framework

app = FastAPI()

@app.get("/classify")
async def classify(product: str, mode: Mode = Query("json_schema")) -> dict:
    """Let the caller choose the response mode (handy for A/B tests)."""
    try:
        data = await ask(product, mode)              # helper from above
    except (ValueError, RuntimeError) as exc:        # our own errors
        raise HTTPException(status_code=502, detail=str(exc))
    return {"mode": mode, "data": data}              # always JSON for the client
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI

# model_kwargs forwards raw parameters to the API (json_object mode):
llm = ChatOpenAI(model="gpt-4o-mini",
                 model_kwargs={"response_format": {"type": "json_object"}})
msg = llm.invoke("Reply in JSON: HS code of earbuds")   # AIMessage with JSON text
# Prefer llm.with_structured_output(Model) for json_schema mode (see topic 085).
# LangGraph nodes can use different modes: classify node = schema, explain node = text.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `json_object` without the word "JSON" in any message
✅ Correct: Mention JSON in system or user message.

```python
# Wrong -> 400 error: "'messages' must contain the word 'json'"
# messages=[{"role": "user", "content": "HS code of earbuds"}]
# Right:
# messages=[{"role": "user", "content": "Give the HS code of earbuds as JSON"}]
```

❌ Mistake 2: Thinking `json_object` enforces your keys
✅ Correct: Use `json_schema` when keys and types matter.

```python
# Wrong: json_object, then data["duty_percent"] -> KeyError sometimes
# Right: json_schema strict with duty_percent required
```

---

## 🧠 Tricky Interview Question

**Q**: "Your JSON-mode call randomly returns a half-finished JSON string and `json.loads` fails. The schema mode is on. What happened?"

**Answer**: `finish_reason == "length"` — the reply hit `max_tokens` before the JSON closed. Constrained decoding keeps tokens valid but cannot finish a document the budget cuts off. Check `finish_reason`, raise `max_tokens`, shorten output fields, and retry. Also with `json_object` alone the model might emit endless whitespace if prompt lacks instruction.

---

## ⚫ Interview Questions + Answers

Q1: Name the three `response_format` types.
A1: `text`, `json_object`, `json_schema`.

Q2: Which mode guarantees my exact keys?
A2: Only `json_schema` with `strict: true`.

Q3: Why does `json_object` need the word JSON in the prompt?
A3: It is an API safeguard so the model is clearly told to produce JSON; otherwise it may generate whitespace forever. The API returns an error if missing.

Q4: Which models support `json_schema`?
A4: GPT-4o family (gpt-4o-2024-08-06 and later, gpt-4o-mini) and newer models. Older gpt-3.5/gpt-4 models support only `json_object` at best. Always check the current docs.

Q5: How would you migrate a prototype using `json_object` to `json_schema` safely?
A5: Define a Pydantic model from the keys you already use, shadow-run both modes on logged traffic, compare parse failures, make nullable fields explicit, deploy behind a flag, and keep `json.loads` plus validation as a second safety net.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `text`: explanations, chat, summaries for humans
- `json_object`: quick prototypes, older models
- `json_schema`: production pipelines, billing, databases

❌ Avoid when:
- `json_schema` for tiny throwaway scripts where a plain prompt is fine
- `json_object` when downstream code needs fixed keys

---

## 📊 Visual Diagram
```
response_format
 ├── {"type":"text"}        -> "Probably 8518.30 because ..."   (free)
 ├── {"type":"json_object"} -> {"anything": "valid JSON"}       (loose)
 └── {"type":"json_schema"} -> {"hs_code":"8518.30","duty_percent":0}
                               ▲ exact keys + types (strict)
 Strength of guarantee:  low ─────────────────────► high
```

---

## 💰 Cost Impact
`text` has no overhead. `json_object` adds nothing except the prompt sentence. `json_schema` adds the schema to input tokens (about 100-300 tokens) but removes filler words in output and reduces retries.
Optimise: use short key names, drop long descriptions the model does not need, set `max_tokens`, use `gpt-4o-mini`, and cache the system prompt.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| response_format | API parameter for reply shape | Reply की shape का parameter |
| json_object | Valid JSON, free keys | कोई भी valid JSON |
| json_schema | JSON matching a schema | Schema वाला JSON |
| finish_reason | Why generation stopped | Generation क्यों रुका |
| strict | Exact schema enforcement | सख्त schema पालन |

---

## ⚡ 3-Line Summary
English: `response_format` has three modes: text, json_object and json_schema. Only json_schema with strict guarantees your keys and types. Always check `finish_reason` for truncation.
Hindi: `response_format` के तीन modes हैं: text, json_object और json_schema। सिर्फ strict json_schema आपकी keys और types की guarantee देता है। Truncation के लिए हमेशा `finish_reason` check करो।

---

## ➡️ Next Topic
**085. Pydantic + OpenAI Integration** — using Pydantic classes directly so schema, validation and typing come from one place.
