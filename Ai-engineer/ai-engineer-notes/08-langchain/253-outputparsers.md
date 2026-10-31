---

# 253. OutputParsers
# हिंदी में: OutputParsers (Model के जवाब को Data में बदलना)

---

## 🔵 Simple Definition (English)
An **OutputParser** takes the model's raw reply (an `AIMessage` or a string) and converts it into a useful Python value: a `str`, a `list`, a `dict`, or a validated pydantic object. It is a Runnable, so it is the last step of a chain: `prompt | llm | parser`. Many parsers can also generate **format instructions** to tell the model what format to produce.

## 🔵 सरल परिभाषा (Hindi)
**OutputParser** model के raw जवाब (`AIMessage` या string) को काम की Python value में बदलता है: `str`, `list`, `dict` या validated pydantic object। यह Runnable है, इसलिए chain का आख़िरी step होता है: `prompt | llm | parser`। कई parsers **format instructions** भी बनाते हैं जो model को बताती हैं कि किस format में जवाब देना है।

---

## 🔴 Problem it Solves
LLMs return free text: `"Sure! The HS code is **8507**."`. Your code needs `{"heading": "8507"}`. Doing `json.loads(reply)` fails when the model adds words or markdown fences. Regex hacks are fragile and each developer invents a new one. You need one consistent step that (1) tells the model the format, (2) parses, (3) validates, (4) raises a clear error if the output is wrong.

## 🔴 यह क्यों बना? (Hindi)
LLM free text देता है: `"Sure! The HS code is **8507**."`। आपके code को `{"heading": "8507"}` चाहिए। जब model extra शब्द या markdown fences जोड़ता है तो `json.loads(reply)` फ़ेल हो जाता है। Regex fragile हैं। चाहिए एक consistent step जो (1) model को format बताए, (2) parse करे, (3) validate करे, (4) गलत output पर साफ़ error दे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Choose parser: StrOutputParser / JsonOutputParser / PydanticOutputParser / ...
Step 2 → (Optional) parser.get_format_instructions() -> text to add into the prompt
Step 3 → Chain runs:  prompt | llm   -> AIMessage
Step 4 → parser.invoke(AIMessage) -> reads .content
Step 5 → Parser cleans/extracts (e.g. strips json code fences) and converts the text
Step 6 → Validation (pydantic) -> returns typed object, or raises OutputParserException
Step 7 → Optional recovery: retry / OutputFixingParser / with_structured_output
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Parser चुनो: StrOutputParser / JsonOutputParser / PydanticOutputParser / ...
Step 2 → (Optional) parser.get_format_instructions() -> prompt में जोड़ने वाला text
Step 3 → Chain चलती है:  prompt | llm   -> AIMessage
Step 4 → parser.invoke(AIMessage) -> .content पढ़ता है
Step 5 → Parser text साफ़ करता है (जैसे json code fences हटाना) और convert करता है
Step 6 → Validation (pydantic) -> typed object या OutputParserException
Step 7 → Recovery: retry / OutputFixingParser / with_structured_output
```

---

## 🟡 Real World Example
**Tariff Classification System**: The API must return `{"heading": "8507", "confidence": 0.92}`. The prompt includes the parser's format instructions; `PydanticOutputParser(TariffResult)` validates that `heading` is 4 digits and `confidence` is between 0 and 1. Invalid output raises an exception, which triggers one retry, then a fallback to "needs human review".

**Zomato AI**: Menu extraction from a photo caption — `CommaSeparatedListOutputParser` converts "paneer, naan, dal" into `["paneer", "naan", "dal"]` for the cart.

## 🟡 Real Example Hindi mein
**Tariff System**: API को `{"heading": "8507", "confidence": 0.92}` लौटाना है। Prompt में parser की format instructions हैं; `PydanticOutputParser(TariffResult)` जाँचता है कि `heading` 4 digits है और `confidence` 0 से 1 के बीच। Invalid output पर exception आता है → एक retry → फिर "human review चाहिए"।

**Zomato AI**: Menu extraction — `CommaSeparatedListOutputParser` "paneer, naan, dal" को `["paneer", "naan", "dal"]` में बदलता है।

---

## 💻 Code Example — Basic
```python
# Basic: three common parsers with a fake LLM (offline, no API key)
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # scripted LLM
from langchain_core.output_parsers import (
    CommaSeparatedListOutputParser,                                    # "a, b, c" -> ["a","b","c"]
    JsonOutputParser,                                                  # JSON text -> dict
    StrOutputParser,                                                   # AIMessage -> str
)
from langchain_core.exceptions import OutputParserException           # parse failure error
from langchain_core.prompts import ChatPromptTemplate                  # prompt

prompt = ChatPromptTemplate.from_messages([("human", "{q}")])          # trivial prompt

# 1) StrOutputParser: message -> plain string
llm = FakeListChatModel(responses=["Heading 8507"])                    # fake reply
print((prompt | llm | StrOutputParser()).invoke({"q": "x"}))           # 'Heading 8507'

# 2) List parser
llm = FakeListChatModel(responses=["8507, 8504, 0901"])
parser = CommaSeparatedListOutputParser()                              # splits by comma
print((prompt | llm | parser).invoke({"q": "x"}))                      # ['8507', '8504', '0901']
print(parser.get_format_instructions())                                # text you can put in a prompt

# 3) JSON parser: also handles json code fences around the object
fence = "`" * 3                                                       # three backticks (written this way to keep this note's code block intact)
llm = FakeListChatModel(responses=[fence + 'json\n{"heading": "8507", "confidence": 0.9}\n' + fence])
print((prompt | llm | JsonOutputParser()).invoke({"q": "x"}))          # {'heading': '8507', 'confidence': 0.9}

# 4) Error case: model ignored the format
llm = FakeListChatModel(responses=["Sorry, I think it is battery related"])
try:
    (prompt | llm | JsonOutputParser()).invoke({"q": "x"})             # not JSON
except OutputParserException as err:                                   # raised by LangChain
    print("Parse failed:", str(err)[:60])                              # handle it, do not crash
```

## 💻 Code Example — Advanced
```python
# Production: parser + retry on parse failure + structured-output alternative + async
# pip install langchain-core pydantic
import asyncio                                                         # async
import logging                                                         # logs
from typing import Optional                                            # type hints
from pydantic import BaseModel, Field                                  # pydantic v2 models
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger("tariff.parse")                             # logger


class TariffResult(BaseModel):                                         # target schema
    heading: str = Field(pattern=r"^\d{4}$", description="4-digit HS heading")
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(max_length=300)


parser = PydanticOutputParser(pydantic_object=TariffResult)            # parse + validate

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Classify the product. {format_instructions}"),         # instructions from the parser
    ("human", "{product}"),
]).partial(format_instructions=parser.get_format_instructions())       # fill once


async def classify(llm: BaseChatModel, product: str, retries: int = 1) -> Optional[TariffResult]:
    """Return a validated result, or None if the model keeps producing invalid output."""
    chain = PROMPT | llm | parser                                      # prompt -> model -> typed object
    for attempt in range(retries + 1):                                 # first try + retries
        try:
            return await chain.ainvoke({"product": product})           # success path
        except OutputParserException as exc:                           # bad JSON or failed validation
            logger.warning("parse failed (attempt %d): %s", attempt + 1, exc)
    return None                                                        # caller routes to human review


# Often better on modern models: native structured output (uses tool calling / JSON schema)
def structured_chain(llm: BaseChatModel):                              # returns a Runnable producing TariffResult
    return PROMPT.partial(format_instructions="") | llm.with_structured_output(TariffResult)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, HTTPException                    # FastAPI
from pydantic import BaseModel, Field

app = FastAPI()                                                        # app


class Req(BaseModel):                                                  # input
    product: str = Field(min_length=2, max_length=300)


def get_llm():
    raise NotImplementedError                                          # shared model


@app.post("/classify", response_model=TariffResult)                    # FastAPI validates output again
async def classify_endpoint(req: Req, llm=Depends(get_llm)) -> TariffResult:
    result = await classify(llm, req.product)                          # from the advanced block
    if result is None:                                                 # parser kept failing
        raise HTTPException(status_code=502, detail="model returned invalid output")
    return result                                                      # typed object -> JSON automatically
```
The same pydantic model serves three jobs: parser schema, prompt instructions, and FastAPI `response_model`.

---

## 🔗 LangChain / LangGraph Connection
```python
# LCEL: parser is the final step; with streaming, StrOutputParser streams text pieces.
chain = prompt | llm | StrOutputParser()
for piece in chain.stream({"q": "..."}):
    print(piece, end="")

# JsonOutputParser also streams partial JSON dicts as they build up.
# LangGraph: a node returns {"result": parser output}; a conditional edge can check if parsing
# failed and loop back to retry ("reflection" loop).
# Modern alternative: llm.with_structured_output(Schema) -- provider enforces the schema.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `json.loads` directly on model output
```python
# Wrong — crashes on markdown code fences or extra words:
data = json.loads(llm.invoke(prompt).content)

# Correct — parser handles fences and gives a clear error type:
data = (prompt | llm | JsonOutputParser()).invoke(inputs)
```

❌ Mistake 2: Forgetting format instructions in the prompt
```python
# Wrong — model does not know the schema, parsing fails often:
prompt | llm | PydanticOutputParser(pydantic_object=TariffResult)

# Correct — inject get_format_instructions() (or use with_structured_output):
prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser
```

❌ Mistake 3: Swallowing OutputParserException silently
```python
# Wrong:
try: result = chain.invoke(x)
except Exception: result = {}        # hides failures, bad data downstream

# Correct — catch OutputParserException, log it, retry, then route to human review.
```

---

## 🧠 Tricky Interview Question

**Q**: "In production 3% of requests fail with OutputParserException. Retrying makes cost go up. What is a better strategy than blind retry?"

**Answer**: First look at WHY: log failing raw outputs. Common root causes are truncated output (`max_tokens` too low), missing format instructions, long/noisy inputs, or a weak model. Fixes in order of cost: (1) use native structured output (`with_structured_output`) so the provider enforces the schema, (2) raise `max_tokens` and simplify the schema, (3) use `OutputFixingParser`/a cheap repair call that sends only the bad output plus the error, not the whole prompt, (4) retry once with temperature 0, (5) fall back to human review. Blind retry resends the entire prompt and doubles cost for the same failure.

---

## ⚫ Interview Questions + Answers

Q1: What is an OutputParser? (Easy)
A1: A Runnable that converts model output into a structured Python value (str, list, dict, pydantic object), usually the last step in an LCEL chain.

Q2: What does `StrOutputParser` do? (Easy)
A2: Extracts the text content of an `AIMessage` and returns a plain string, so downstream code does not deal with message objects.

Q3: What are format instructions? (Medium)
A3: Text generated by `parser.get_format_instructions()` that describes the expected output (schema, JSON structure). You add it to the prompt so the model knows what to produce.

Q4: Parser vs `with_structured_output`? (Medium)
A4: Parsers work with any model by prompting and parsing text. `with_structured_output` uses the provider's tool-calling or JSON-schema mode so the model is constrained and the result is already a pydantic object — usually more reliable and less prompt text. Use parsers for models without such support or for streaming partial JSON.

Q5: How do you handle parsing failures at scale? (Hard)
A5: Monitor parse failure rate; store failing raw outputs; use native structured output; set sufficient `max_tokens`; add repair step (OutputFixingParser) sending only the bad text; retry with limits and backoff; use pydantic validators for business rules (e.g. heading exists in DB); fall back to human review; add alerts if the rate rises after a prompt or model change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Downstream code needs str / list / dict / typed object
- You need validation of LLM output
- You want consistent error handling

❌ Avoid when:
- Free-text answer shown straight to the user (StrOutputParser is enough)
- Provider supports native structured output and you do not need streaming JSON (prefer `with_structured_output`)

---

## 📊 Visual Diagram
```
 prompt (+ format instructions)
            │
            ▼
        ChatModel ──► AIMessage("<fence>json {...} <fence>")
                              │
                              ▼
                      ┌───────────────┐
                      │ OutputParser  │  strip fences, parse, validate
                      └──────┬────────┘
              ┌──────────────┼───────────────┐
              ▼              ▼               ▼
          str / list       dict        pydantic object
                                   (or OutputParserException)
```

---

## 💰 Cost Impact
Format instructions add input tokens on every call (a 3-field schema ≈ 150-250 tokens). At 100K calls/day that is ~20M tokens ≈ $3/day on gpt-4o-mini. Failures add cost: a retry resends the whole prompt, so a 3% failure rate with 1 retry costs about +3% overall.

Optimise: use `with_structured_output` (schema travels as a tool definition, often shorter and more reliable), keep schemas small, short field descriptions, `temperature=0`, and repair only the bad output instead of re-running the full prompt.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OutputParser | Converts reply to Python data | जवाब को data में बदलने वाला |
| Format instructions | Text describing expected format | Format बताने वाला text |
| `OutputParserException` | Parse/validation failure | Parse fail होने का error |
| Structured output | Provider-enforced schema | Provider द्वारा तय schema |
| Validation | Check types and rules | Types और नियम जाँचना |
| Fixing parser | Uses LLM to repair output | गलत output ठीक करना |

---

## ⚡ 3-Line Summary
English: OutputParsers turn raw LLM text into typed data and raise clear errors when the format is wrong. Add format instructions or use `with_structured_output` for reliability. Handle failures with limited retries and a human-review fallback.
Hindi: OutputParsers LLM के raw text को typed data में बदलते हैं और format गलत होने पर साफ़ error देते हैं। भरोसे के लिए format instructions या `with_structured_output` इस्तेमाल करो। Failures को सीमित retries और human-review fallback से संभालो।

---

## ➡️ Next Topic
**254. StrOutputParser** — the simplest and most-used parser: AIMessage to plain string, including streaming.
