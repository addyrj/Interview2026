---

# 256. JsonOutputParser
# हिंदी में: JsonOutputParser (JSON में output पढ़ने वाला Parser)

---

## 🔵 Simple Definition (English)
`JsonOutputParser` is a LangChain output parser that turns the LLM's text reply into a Python `dict`. It also gives the model **format instructions** ("reply as JSON like this") and can stream partial JSON while the model is still writing.

## 🔵 सरल परिभाषा (Hindi)
`JsonOutputParser` LangChain का output parser है जो LLM के text reply को Python `dict` में बदलता है। ये model को **format instructions** भी देता है ("इस तरह JSON में जवाब दो") और model के लिखते-लिखते partial JSON stream भी कर सकता है।

---

## 🔴 Problem it Solves
- LLMs reply in free text; code needs structured data.
- Models wrap JSON in prose or ```json fences, so `json.loads` crashes.
- Without a schema hint, key names change between calls.
- Streaming JSON normally cannot be parsed until it is complete.

## 🔴 यह क्यों बना? (Hindi)
- LLM free text में जवाब देता है; code को structured data चाहिए।
- Model JSON के आस-पास बातें या ```json fences लगा देता है, तो `json.loads` टूट जाता है।
- Schema hint के बिना हर call में key के नाम बदल जाते हैं।
- Streaming JSON पूरा होने तक आम तौर पर parse नहीं हो सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create parser = JsonOutputParser(pydantic_object=Schema)  (schema optional)
Step 2 → parser.get_format_instructions() returns a text hint describing the JSON shape
Step 3 → Put that hint into the prompt as {format_instructions}
Step 4 → LLM replies with text containing JSON
Step 5 → parser strips fences/extra text and parses it into a dict
Step 6 → Bad JSON raises OutputParserException
Step 7 → In a chain: prompt | llm | parser  (stream() yields growing partial dicts)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → parser = JsonOutputParser(pydantic_object=Schema) बनाओ (schema optional)
Step 2 → parser.get_format_instructions() JSON shape का text hint देता है
Step 3 → उस hint को prompt में {format_instructions} की जगह डालो
Step 4 → LLM JSON वाला text लौटाता है
Step 5 → parser fences/extra text हटाकर dict में parse करता है
Step 6 → गलत JSON पर OutputParserException आता है
Step 7 → Chain में: prompt | llm | parser (stream() बढ़ते हुए partial dict देता है)
```

---

## 🟡 Real World Example
**Tariff Classification System**: The LLM must return `{"hs_code": "8517.13", "description": "...", "confidence": 0.9}` so the backend can store the HS code in a database and show confidence in the UI. `JsonOutputParser` makes the reply a dict that code can use.
**Zomato AI**: parse "order summary" text into `{"items": [...], "total": 450}`.

## 🟡 Real Example Hindi mein
**Tariff System**: LLM को `{"hs_code": "8517.13", "description": "...", "confidence": 0.9}` लौटाना है ताकि backend HS code database में रखे और UI में confidence दिखाए। `JsonOutputParser` reply को dict बना देता है।
**Zomato AI**: "order summary" text को `{"items": [...], "total": 450}` में parse करना।

---

## 💻 Code Example — Basic
```python
# Basic: what the parser does, shown with a fake LLM reply (runs without langchain installed)
import json
import re
from typing import Any, Dict

def parse_json_reply(text: str) -> Dict[str, Any]:
    """Mimics JsonOutputParser: strip ```json fences, then json.loads."""
    cleaned = text.strip()                                   # remove outer whitespace
    match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)  # find fenced block
    if match:
        cleaned = match.group(1).strip()                     # keep only fence content
    return json.loads(cleaned)                               # may raise JSONDecodeError

if __name__ == "__main__":
    # Typical messy model reply
    reply = 'Sure! Here you go:\n```json\n{"hs_code": "8517.13", "confidence": 0.92}\n```'
    # The 'Sure!' prefix is outside the fence, so the fence search handles it
    data = parse_json_reply(reply)
    print(data["hs_code"], data["confidence"])               # 8517.13 0.92
    try:
        parse_json_reply("not json at all")
    except json.JSONDecodeError as exc:
        print("parse failed:", exc.msg)
    # Real LangChain equivalent:
    #   from langchain_core.output_parsers import JsonOutputParser
    #   parser = JsonOutputParser(); parser.parse(reply)
```

## 💻 Code Example — Advanced
```python
# Production: typed schema, format instructions, async, retry on parse failure
import asyncio
from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field  # pydantic v2

class HSResult(BaseModel):
    """Schema used only to generate format instructions (parser returns a dict)."""
    hs_code: str = Field(description="HS code like 8517.13")
    description: str = Field(description="Short product description")
    confidence: float = Field(description="0.0 to 1.0")

parser = JsonOutputParser(pydantic_object=HSResult)           # schema hint source
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a customs classifier. {format_instructions}"),
    ("human", "Classify: {product}"),
]).partial(format_instructions=parser.get_format_instructions())   # fill the hint once

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=200)
chain = prompt | llm | parser                                  # LCEL chain

async def classify(product: str, retries: int = 2) -> dict[str, Any]:
    last_error: Exception | None = None
    for _ in range(retries + 1):
        try:
            raw = await chain.ainvoke({"product": product})    # dict from parser
            return HSResult(**raw).model_dump()                # validate keys and types
        except (OutputParserException, ValueError) as exc:     # bad JSON or bad fields
            last_error = exc                                   # try again
    raise RuntimeError(f"Could not parse after {retries + 1} tries: {last_error}")

async def stream_partial(product: str) -> None:
    async for partial in chain.astream({"product": product}):  # growing dicts
        print(partial)                                         # {'hs_code': '85'} -> ...

if __name__ == "__main__":
    print(asyncio.run(classify("Bluetooth speaker")))          # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Return the dict through a response model so the API contract is validated.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class In(BaseModel):
    product: str = Field(min_length=2, max_length=300)

@app.post("/classify", response_model=HSResult)   # HSResult from the advanced example
async def classify_route(body: In) -> HSResult:
    try:
        return HSResult(**await classify(body.product))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))   # LLM kept returning bad JSON
```

---

## 🔗 LangChain / LangGraph Connection
`JsonOutputParser` is a `Runnable`, so it pipes at the end of any chain with `|`. In LangGraph, call `chain.ainvoke` inside a node and write the dict into the state. For stricter guarantees, prefer `llm.with_structured_output(HSResult)` (uses tool calling or JSON mode); keep `JsonOutputParser` for models without that feature or when you want streaming partial dicts.

```python
# Structured-output alternative (returns a validated HSResult object directly)
structured = llm.with_structured_output(HSResult)
result: HSResult = structured.invoke("Classify: Bluetooth speaker")
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to put format instructions in the prompt.
✅ Correct: Insert `parser.get_format_instructions()`.

```python
# Wrong: model invents its own keys
prompt = ChatPromptTemplate.from_template("Classify {product} as JSON")
# Right
prompt = ChatPromptTemplate.from_template(
    "Classify {product}.\n{format_instructions}"
).partial(format_instructions=parser.get_format_instructions())
```

❌ Mistake 2: Assuming the dict is validated (the parser does not check types).
✅ Correct: Validate with pydantic after parsing, or use `with_structured_output`.

❌ Mistake 3: Raw braces in the prompt text: `{"a": 1}` makes the template treat `a` as a variable.
✅ Correct: Escape as `{{"a": 1}}`.

---

## 🧠 Tricky Interview Question
**Q**: "The parser works in testing but in production about 2% of calls raise OutputParserException. How do you reduce that?"

**Answer**: Typical causes are truncated output (`max_tokens` too small, so JSON is cut off), the model adding prose, or odd characters. Fixes: raise `max_tokens`, set temperature 0, use JSON mode or `with_structured_output` (constrained by the API), add `OutputFixingParser` or a retry that sends the error back to the model, and log the raw output for failed cases. Truncation is the most common culprit; check `finish_reason == "length"`.

---

## ⚫ Interview Questions + Answers

Q1: What does JsonOutputParser return?
A1: A Python `dict` (or list) parsed from the model text, not a pydantic object.

Q2: What is `get_format_instructions()` for?
A2: It produces a prompt snippet describing the expected JSON, derived from the pydantic schema, so the model follows the shape.

Q3: JsonOutputParser vs PydanticOutputParser?
A3: JsonOutputParser returns a plain dict and supports streaming partial JSON. PydanticOutputParser validates and returns a model instance, but fails on invalid fields and does not stream partials.

Q4: JsonOutputParser vs `with_structured_output`?
A4: `with_structured_output` uses the provider's native tool calling or JSON schema mode, so output is more reliable. Parser relies on prompting and text parsing.

Q5: How would you make JSON extraction robust at scale?
A5: Use native structured output, validate with pydantic, set `max_tokens` with headroom, retry with the validation error fed back, fall back to a bigger model on repeated failure, and monitor parse-failure rate per prompt version.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a dict from model text
- You want to stream partial JSON to a UI
- The model has no native structured-output mode

❌ Avoid when:
- The provider supports strict structured output (use that)
- You need guaranteed types without extra validation
- Output is plain prose

---

## 📊 Visual Diagram
```
 prompt + {format_instructions}
          │
          ▼
       ┌─────┐   text: ```json {"hs_code":"8517.13"} ```
       │ LLM │ ─────────────────────────────┐
       └─────┘                              ▼
                                   ┌──────────────────┐
                                   │ JsonOutputParser │
                                   └────────┬─────────┘
                                            ▼
                              {"hs_code": "8517.13", ...}  (dict)
```

---

## 💰 Cost Impact
- Format instructions add ~100-250 input tokens per call (a big schema costs more).
- JSON keys and quotes make output longer than plain text; short key names save output tokens.
- Retries double the cost of failed calls.
- Optimise: short descriptions in schema, small `max_tokens` (with headroom), `partial()` the instructions once, and use native structured output to reduce retries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Output parser | Converts LLM text into data | LLM text को data बनाने वाला |
| Format instructions | Prompt hint about the output shape | Output के shape का hint |
| Partial JSON | Incomplete JSON while streaming | Stream के दौरान अधूरा JSON |
| OutputParserException | Error when parsing fails | Parse फ़ेल होने की error |
| Structured output | Provider-enforced schema output | Provider द्वारा तय schema वाला output |

---

## ⚡ 3-Line Summary
English: JsonOutputParser converts model text into a dict and supplies schema hints for the prompt. It can stream partial dicts, but it does not validate types. For reliability use pydantic validation or native structured output.
Hindi: JsonOutputParser model के text को dict में बदलता है और prompt के लिए schema hint देता है। ये partial dict stream कर सकता है पर types validate नहीं करता। भरोसे के लिए pydantic validation या native structured output इस्तेमाल करो।

---

## ➡️ Next Topic
**257. Memory in LangChain**: how chains remember earlier messages, and why the old memory classes were replaced.
