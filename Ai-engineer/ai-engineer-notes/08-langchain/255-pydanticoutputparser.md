---

# 255. PydanticOutputParser
# हिंदी में: PydanticOutputParser (Parse + Validate एक साथ)

---

## 🔵 Simple Definition (English)
`PydanticOutputParser` converts the model's JSON text into an instance of **your pydantic model** and validates it (types, ranges, regex, custom rules). It also creates **format instructions** (the JSON schema in words) that you add to the prompt. If the output is invalid, it raises `OutputParserException`.

## 🔵 सरल परिभाषा (Hindi)
`PydanticOutputParser` model के JSON text को **आपके pydantic model** के instance में बदलता है और validate करता है (types, ranges, regex, custom rules)। यह **format instructions** (schema शब्दों में) भी बनाता है जो prompt में जोड़ी जाती हैं। Output गलत हो तो `OutputParserException` आता है।

---

## 🔴 Problem it Solves
`JsonOutputParser` gives a dict, but nobody checks that `heading` is a 4-digit string or that `confidence` is between 0 and 1. A bad value travels through the system and breaks a database insert or a customs declaration later. We want the same schema that validates our API to also validate the LLM output, with IDE autocompletion and type safety.

## 🔴 यह क्यों बना? (Hindi)
`JsonOutputParser` dict देता है, पर कोई नहीं जाँचता कि `heading` 4-digit string है या `confidence` 0 से 1 के बीच है। गलत value आगे जाकर database insert या customs declaration तोड़ सकती है। हम चाहते हैं कि जो schema हमारे API को validate करता है वही LLM output को भी validate करे — IDE autocomplete और type safety के साथ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define pydantic model (fields, types, descriptions, validators)
Step 2 → parser = PydanticOutputParser(pydantic_object=Model)
Step 3 → parser.get_format_instructions() -> JSON schema explained in text
Step 4 → Put the instructions into the prompt (usually via .partial())
Step 5 → LLM replies with JSON text (maybe inside code fences)
Step 6 → Parser extracts the JSON, runs Model.model_validate_json / validate
Step 7 → Success -> Model instance;  failure -> OutputParserException (with the raw output)
Step 8 → Optional: OutputFixingParser / RetryOutputParser asks an LLM to repair, or retry
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pydantic model बनाओ (fields, types, descriptions, validators)
Step 2 → parser = PydanticOutputParser(pydantic_object=Model)
Step 3 → parser.get_format_instructions() -> schema का text
Step 4 → Instructions को prompt में डालो (.partial() से)
Step 5 → LLM JSON text देता है (कभी code fences में)
Step 6 → Parser JSON निकालकर Model से validate करता है
Step 7 → सफल -> Model instance;  असफल -> OutputParserException
Step 8 → Optional: OutputFixingParser / RetryOutputParser से सुधार या retry
```

---

## 🟡 Real World Example
**Tariff Classification System**:
```
class TariffResult: heading (4 digits), subheading (6 digits, must start with heading),
                    confidence 0-1, duty_percent >= 0, evidence: list[str]
```
A custom validator checks that the subheading starts with the heading. If the model answers heading "8507" and subheading "850440", validation fails, so the wrong data never reaches the declaration form.

**Amazon AI**: Product-listing extractor: `title`, `brand`, `price: float`, `colors: list[str]` validated before saving to the catalogue.

## 🟡 Real Example Hindi mein
**Tariff System**: `TariffResult` में heading (4 digits), subheading (6 digits, heading से शुरू), confidence 0-1, duty_percent >= 0, evidence list है। Custom validator जाँचता है कि subheading, heading से शुरू होती है। Model heading "8507" और subheading "850440" दे तो validation फ़ेल होता है — गलत data declaration form तक नहीं पहुँचता।

**Amazon AI**: Product-listing extractor: `title`, `brand`, `price: float`, `colors: list[str]` catalogue में save होने से पहले validate होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: PydanticOutputParser with validation (offline, no API key)
# pip install langchain-core pydantic
from pydantic import BaseModel, Field, field_validator, model_validator  # pydantic v2
from langchain_core.exceptions import OutputParserException           # parse error
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # fake LLM
from langchain_core.output_parsers import PydanticOutputParser         # the parser
from langchain_core.prompts import ChatPromptTemplate                  # prompt


class TariffResult(BaseModel):                                         # target schema
    heading: str = Field(description="4-digit HS heading, e.g. 8507")  # description goes to the LLM
    subheading: str = Field(description="6-digit HS subheading")
    confidence: float = Field(ge=0, le=1, description="0 to 1")        # range validation
    evidence: list[str] = Field(default_factory=list)                  # optional list

    @field_validator("heading")                                        # check one field
    @classmethod
    def heading_is_4_digits(cls, v: str) -> str:
        if not (v.isdigit() and len(v) == 4):                          # simple rule
            raise ValueError("heading must be 4 digits")
        return v

    @model_validator(mode="after")                                     # check fields together
    def sub_matches_heading(self) -> "TariffResult":
        if not self.subheading.startswith(self.heading):               # business rule
            raise ValueError("subheading must start with heading")
        return self


parser = PydanticOutputParser(pydantic_object=TariffResult)           # create parser
print(parser.get_format_instructions()[:90], "...")                    # schema text for the prompt

prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the product.\n{format_instructions}"),        # instructions placeholder
    ("human", "{product}"),
]).partial(format_instructions=parser.get_format_instructions())      # fill instructions once

good = FakeListChatModel(responses=['{"heading": "8507", "subheading": "850760", "confidence": 0.93}'])
result = (prompt | good | parser).invoke({"product": "power bank"})   # -> TariffResult
print(result.heading, result.subheading, result.confidence)           # typed attribute access

bad = FakeListChatModel(responses=['{"heading": "8507", "subheading": "850440", "confidence": 0.9}'])
try:
    (prompt | bad | parser).invoke({"product": "power bank"})          # violates business rule
except OutputParserException as err:                                   # validation failed
    print("Rejected:", "subheading must start with heading" in str(err))  # True
```

## 💻 Code Example — Advanced
```python
# Production: parser + repair step + async + metrics + fallback
# pip install langchain-core langchain-classic pydantic
import logging                                                         # logging
from typing import Optional                                            # type hints
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.output_parsers import OutputFixingParser        # LLM-based repair of invalid output

logger = logging.getLogger("tariff.pydantic")                          # logger
# TariffResult from the basic example is reused here.


def build_chain(llm: BaseChatModel, cheap_llm: BaseChatModel):
    """Main chain + a repair parser that uses a cheap model."""
    base = PydanticOutputParser(pydantic_object=TariffResult)          # strict parser
    fixing = OutputFixingParser.from_llm(parser=base, llm=cheap_llm, max_retries=1)  # repair once
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Classify the product.\n{format_instructions}"),
        ("human", "{product}"),
    ]).partial(format_instructions=base.get_format_instructions())
    return prompt | llm | fixing                                       # repair happens only on failure


async def classify(chain, product: str) -> Optional[TariffResult]:
    """Return validated result or None (-> human review)."""
    if not product.strip():                                            # input validation
        raise ValueError("product is required")
    try:
        return await chain.ainvoke({"product": product})               # async call
    except OutputParserException:                                      # still invalid after repair
        logger.warning("invalid model output for %r", product)         # metric / alert hook
        return None                                                    # fallback path
    except Exception:                                                  # network / provider
        logger.exception("classification failed")
        raise                                                          # API layer handles 5xx
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, HTTPException                    # FastAPI
from pydantic import BaseModel, Field

app = FastAPI()                                                        # app


class Req(BaseModel):                                                  # request
    product: str = Field(min_length=2, max_length=300)


def get_chain():
    raise NotImplementedError                                          # build_chain(...) once at startup


@app.post("/classify", response_model=TariffResult)                    # the SAME model is the API contract
async def classify_endpoint(req: Req, chain=Depends(get_chain)) -> TariffResult:
    result = await classify(chain, req.product)
    if result is None:                                                 # invalid even after repair
        raise HTTPException(status_code=422, detail="could not produce a valid classification")
    return result
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LCEL: prompt | llm | parser. Modern alternative (usually more reliable):
structured_llm = llm.with_structured_output(TariffResult)   # provider enforces schema, returns TariffResult
result = (prompt_without_format_instructions | structured_llm).invoke({"product": "power bank"})

# LangGraph: store the model in state:  class State(TypedDict): result: TariffResult
# Conditional edge: if parsing failed -> route to "retry_with_more_context" or "human_review".
# Pydantic models also work as tool argument schemas for agents (args_schema).
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using pydantic v1 imports with LangChain
```python
# Wrong (old):
from langchain_core.pydantic_v1 import BaseModel

# Correct — current LangChain uses pydantic v2 directly:
from pydantic import BaseModel
```

❌ Mistake 2: Vague or missing field descriptions
```python
# Wrong — model guesses what "code" means:
class R(BaseModel):
    code: str

# Correct — descriptions are part of the schema the LLM sees:
class R(BaseModel):
    code: str = Field(description="4-digit HS heading, digits only")
```

❌ Mistake 3: Huge schemas with many optional fields
```python
# Wrong — 40 fields, long descriptions: more tokens, more errors
# Correct — ask only what you need; split into two calls if required.
```

---

## 🧠 Tricky Interview Question

**Q**: "The model returns valid JSON but your pydantic validation rejects 8% of answers because `confidence` is sometimes `\"high\"`. Should you loosen the schema?"

**Answer**: No — fix the contract, do not hide the problem. `confidence` as a model-reported number is poorly calibrated anyway. Better: (1) improve the field description with an example ("float 0.0-1.0, never text"), (2) use native structured output so the type is enforced, (3) or replace it with an enum (`low|medium|high`) if text is natural for the model, then map to numbers in code, (4) log rejected outputs to see patterns. Loosening to `Union[float, str]` pushes the error downstream.

---

## ⚫ Interview Questions + Answers

Q1: What does PydanticOutputParser return? (Easy)
A1: An instance of your pydantic model with validated fields, or it raises `OutputParserException`.

Q2: How does the model know the format? (Easy)
A2: You inject `parser.get_format_instructions()` (JSON schema + instructions) into the prompt.

Q3: Where do field descriptions go? (Medium)
A3: `Field(description=...)` is included in the JSON schema inside the format instructions, so it guides the LLM. Good descriptions improve accuracy and cost only a few tokens.

Q4: PydanticOutputParser vs `with_structured_output`? (Medium)
A4: The parser prompts for JSON and parses text; works with any model. `with_structured_output` uses tool/JSON-schema features of the provider, so output is constrained, with no format instructions needed. Prefer the latter when supported; keep the parser for portability or models without those features.

Q5: How do you handle repeated validation failures in production? (Hard)
A5: Track failure rate per prompt version, store raw outputs, add a cheap repair step (OutputFixingParser sends only the bad output + error), retry once with temperature 0, then route to human review. Fix root causes: schema too complex, truncated output (raise `max_tokens`), missing domain context (add retrieval), or wrong model tier. Add business validators so wrong-but-well-formed data is also caught.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need typed, validated output for APIs/databases
- The model lacks native structured output
- The same pydantic model is reused as FastAPI schema

❌ Avoid when:
- Free text answers
- Provider-native structured output is available and sufficient
- Very large nested schemas (split the task)

---

## 📊 Visual Diagram
```
 TariffResult (pydantic)
      │ get_format_instructions()
      ▼
 prompt ─────────► LLM ──► '{"heading":"8507","subheading":"850760","confidence":0.93}'
                                   │
                                   ▼
                       PydanticOutputParser
                       ├─ parse JSON
                       ├─ field validators (4 digits, 0..1)
                       └─ model validators (subheading startswith heading)
                                   │
                  ┌────────────────┴───────────────┐
                  ▼                                ▼
         TariffResult instance          OutputParserException
                                          └─► OutputFixingParser / retry / human
```

---

## 💰 Cost Impact
Format instructions add ~200-400 tokens to every request (schema text). At 100K calls/day: 30M tokens ≈ $4.50/day on gpt-4o-mini. A repair call costs bad output (~100 tokens) + instructions (~300) + error (~50) ≈ 450 input tokens — cheaper than re-running a 3,000-token RAG prompt.

Optimise: short field names and descriptions, native structured output (schema sent as tool definition, often shorter), `max_tokens` large enough to avoid truncated JSON, a cheap model for repair, and fewer fields.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pydantic model | Typed data class with validation | Validation वाली data class |
| Validator | Custom rule on field/model | Field/model पर नियम |
| Format instructions | Schema explained to the LLM | LLM को schema समझाना |
| `OutputFixingParser` | LLM repairs invalid output | LLM से गलत output ठीक करना |
| Structured output | Provider-enforced JSON schema | Provider से schema लागू |
| `response_model` | FastAPI output schema | FastAPI का output schema |

---

## ⚡ 3-Line Summary
English: PydanticOutputParser turns model JSON into a validated pydantic object and raises errors on bad data. Add format instructions to the prompt and field descriptions for accuracy. Prefer `with_structured_output` when available, and keep a repair or human-review fallback.
Hindi: PydanticOutputParser model के JSON को validated pydantic object में बदलता है और गलत data पर error देता है। सटीकता के लिए prompt में format instructions और field descriptions दो। जहाँ मिले `with_structured_output` बेहतर है, और repair या human-review fallback रखो।

---

## ➡️ Next Topic
**256. JsonOutputParser** — lightweight JSON parsing with streaming partial JSON, when you do not need a full schema.
