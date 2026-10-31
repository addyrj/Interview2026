---

# 098. Schema Design Best Practices
# हिंदी में: Schema Design की Best Practices

---

## 🔵 Simple Definition (English)
Schema design is choosing field names, types, descriptions, order and structure so that an LLM fills the schema accurately and cheaply. The schema is part of the prompt: the model reads names and descriptions as instructions. A good schema is small, clear, ordered to allow reasoning first, and easy to validate.

## 🔵 सरल परिभाषा (Hindi)
Schema design का मतलब है field names, types, descriptions, order और structure ऐसे चुनना कि LLM schema को सही और सस्ते में भरे। Schema prompt का हिस्सा है: model names और descriptions को instructions की तरह पढ़ता है। अच्छा schema छोटा, साफ, reasoning-पहले क्रम में और validate करने में आसान होता है।

---

## 🔴 Problem it Solves
Bad schemas cause bad outputs even with a great model: vague names (`data`, `info`), wrong order (answer before reasoning), too many fields, ambiguous types (`duty: str`). Teams often blame the model when the schema is the problem.

## 🔴 यह क्यों बना? (Hindi)
Bad schemas अच्छे model के साथ भी bad outputs देते हैं: अस्पष्ट names (`data`, `info`), गलत order (reasoning से पहले answer), बहुत सारे fields, अस्पष्ट types (`duty: str`)। Teams अक्सर model को दोष देती हैं जबकि समस्या schema में होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start from the consumer: what does downstream code need? (only those fields)
Step 2 → Name fields clearly: hs_code, duty_percent (unit in name), not "d1" or "value"
Step 3 → Use precise types: float for numbers, Enum/Literal for categories, bool for flags
Step 4 → Describe each non-obvious field: format, unit, "null if not stated"
Step 5 → Order fields for reasoning: evidence/reasoning BEFORE the final answer
Step 6 → Keep it small and shallow; split big tasks into multiple calls
Step 7 → Test on real examples, measure accuracy, iterate; version the schema
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Consumer से शुरू करो: downstream code को क्या चाहिए? (सिर्फ वही fields)
Step 2 → Fields के नाम साफ रखो: hs_code, duty_percent (unit नाम में), "d1" या "value" नहीं
Step 3 → सटीक types: numbers के लिए float, categories के लिए Enum/Literal, flags के लिए bool
Step 4 → हर non-obvious field का description: format, unit, "नहीं दिया तो null"
Step 5 → Reasoning के हिसाब से order: अंतिम answer से पहले evidence/reasoning
Step 6 → छोटा और shallow रखो; बड़े task को कई calls में बाँटो
Step 7 → असली examples पर test करो, accuracy नापो, सुधारो; schema को version करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Version 1 had `{"result": str}`: unusable. Version 2: `{hs_code, duty_percent, confidence}`. Version 3 puts `reasoning` first (a short evidence sentence), then `hs_code`: accuracy rose because the model "thinks" before committing. Version 4 adds `candidate_chapter: Literal[...]` from RAG. Each change was tested on 200 labelled products.

**Amazon-style**: Fields like `price_usd: float` (not `price: str`) prevent "$1,299.00" parsing bugs.

## 🟡 Real Example Hindi mein
**Tariff System**: Version 1 में `{"result": str}` था: बेकार। Version 2: `{hs_code, duty_percent, confidence}`। Version 3 में `reasoning` पहले (छोटा evidence वाक्य), फिर `hs_code`: accuracy बढ़ी क्योंकि model commit करने से पहले "सोचता" है। Version 4 में RAG से `candidate_chapter: Literal[...]` जोड़ा। हर बदलाव 200 labelled products पर test हुआ।

**Amazon-style**: `price_usd: float` (न कि `price: str`) जैसे fields "$1,299.00" parsing bugs रोकते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: a bad schema vs a good schema, and a tiny "schema linter". Needs: pip install pydantic
from typing import Literal, Optional
from pydantic import BaseModel, Field

class BadSchema(BaseModel):                              # vague names, loose types
    data: str
    value: str
    flag: str

class GoodSchema(BaseModel):                             # clear, typed, ordered
    reasoning: str = Field(description="One sentence citing words from the input that justify the code")
    hs_code: str = Field(description="6-digit HS code formatted 8518.30")
    duty_percent: float = Field(description="Import duty as a percent number, e.g. 5.0 for 5%")
    confidence: float = Field(description="0.0 to 1.0, lower if the input is vague")
    origin_country: Optional[Literal["CN", "IN", "US", "OTHER"]] = Field(
        description="Country of origin if stated, otherwise null")

VAGUE_NAMES = {"data", "value", "info", "result", "flag", "x", "temp"}   # names to avoid

def lint(model: type[BaseModel]) -> list[str]:
    """Return warnings about common schema smells."""
    warnings: list[str] = []
    fields = model.model_fields                           # name -> FieldInfo
    if len(fields) > 15:
        warnings.append("more than 15 fields: split the task")
    for name, info in fields.items():
        if name in VAGUE_NAMES:
            warnings.append(f"{name}: vague name")
        if info.description is None:
            warnings.append(f"{name}: no description")
        if info.annotation is str and name not in {"reasoning"} and info.description is None:
            warnings.append(f"{name}: free string, can it be Enum/float?")
    names = list(fields)
    if "reasoning" in names and names.index("reasoning") != 0:
        warnings.append("reasoning should come first")
    return warnings

print("Bad :", lint(BadSchema))
print("Good:", lint(GoodSchema))                          # []
```

## 💻 Code Example — Advanced
```python
# Production: versioned schemas, A/B evaluation harness (offline-capable), async.
import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, Literal
from pydantic import BaseModel, Field

class TariffV2(BaseModel):                                # no reasoning field
    hs_code: str
    confidence: float

class TariffV3(BaseModel):                                # reasoning first
    reasoning: str = Field(description="One sentence of evidence from the input")
    hs_code: str
    confidence: float

SCHEMAS: dict[str, type[BaseModel]] = {"v2": TariffV2, "v3": TariffV3}   # registry by version

@dataclass
class Example:
    text: str
    expected_hs: str

Classifier = Callable[[str, type[BaseModel]], Awaitable[str]]            # returns predicted hs_code

async def evaluate(version: str, classify: Classifier, data: list[Example]) -> float:
    """Accuracy of one schema version over a labelled set (run concurrently)."""
    schema = SCHEMAS[version]
    preds = await asyncio.gather(*(classify(ex.text, schema) for ex in data))   # parallel calls
    correct = sum(p == ex.expected_hs for p, ex in zip(preds, data))
    return correct / len(data)

async def fake_classify(text: str, schema: type[BaseModel]) -> str:
    """Offline stand-in: pretend the reasoning schema fixes one ambiguous case."""
    await asyncio.sleep(0)
    if "earbuds" in text:
        return "8518.30"
    return "8517.13" if "reasoning" in schema.model_fields else "0000.00"

async def main() -> None:
    data = [Example("wireless earbuds", "8518.30"), Example("smartphone", "8517.13")]
    for v in SCHEMAS:
        print(v, "accuracy:", await evaluate(v, fake_classify, data))        # v2 0.5, v3 1.0

if __name__ == "__main__":
    asyncio.run(main())                                   # runs offline
# In production replace fake_classify with a client.beta.chat.completions.parse(...) call.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

@app.get("/schemas/{version}")
async def get_schema(version: str) -> dict:
    """Expose the JSON Schema for a version: clients and tests can diff it."""
    model = SCHEMAS.get(version)
    if model is None:
        raise HTTPException(status_code=404, detail="unknown schema version")
    return model.model_json_schema()
# Use a request header or query (?schema=v3) to run canary traffic on a new schema version.
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
v3 = llm.with_structured_output(TariffV3)                 # field names + descriptions reach the model
# LangChain passes the descriptions to the LLM, so good descriptions = better extraction.
# LangGraph: keep node output schemas small; the graph state can hold several small models
# instead of one giant schema.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Answer field before reasoning
✅ Correct: Reasoning/evidence first, then the answer (the model generates left to right).

```python
# Wrong: class R(BaseModel): hs_code: str; reasoning: str
# Right: class R(BaseModel): reasoning: str; hs_code: str
```

❌ Mistake 2: Everything is `str`
✅ Correct: Use real types.

```python
# Wrong: duty: str   # "about 5 percent"
# Right: duty_percent: float = Field(description="percent number, 5.0 means 5%")
```

---

## 🧠 Tricky Interview Question

**Q**: "Two schemas have identical fields but different names (`d` vs `duty_percent`). Same model, same prompt. Accuracy differs by 8 points. How is that possible?"

**Answer**: Field names and descriptions are tokens the model reads, so they act as instructions. `duty_percent` tells unit and meaning; `d` is ambiguous. Likewise order matters: autoregressive models generate fields in order, so earlier fields condition later ones. Therefore schema design is prompt engineering and needs evaluation like any prompt.

---

## ⚫ Interview Questions + Answers

Q1: Why add descriptions to fields?
A1: They tell the model what to put (format, units, null rules); they are read as instructions.

Q2: Why put reasoning before the answer?
A2: Generation is sequential; reasoning first gives the model "working space" before committing to a final value.

Q3: Flat vs nested schemas?
A3: Prefer flat/shallow for accuracy and cost; nest only where the data is truly hierarchical.

Q4: How many fields are too many?
A4: Roughly more than 10-15 starts hurting accuracy and cost; split into stages.

Q5: How do you evolve a schema safely in production?
A5: Version it, keep the old one running, evaluate the new one on a labelled set and shadow/canary traffic, add new fields as optional, migrate consumers, then retire the old version.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Starting any structured-output feature
- Accuracy is below target and prompt tweaks stall

❌ Avoid when:
- Over-engineering a trivial one-field extraction

---

## 📊 Visual Diagram
```
 BAD                      GOOD
 {data: str,              {reasoning: str,        <- think first
  value: str,              hs_code: "8518.30",    <- format in description
  flag: str}               duty_percent: float,   <- unit in name
                           confidence: 0..1,
                           origin: Literal|null}  <- honest unknown
 vague / loose            clear / typed / ordered
```

---

## 💰 Cost Impact
Every field name and description is input tokens on every call; every field value is output tokens. A trimmed 6-field schema may save ~200 input tokens and ~50 output tokens versus a bloated one: at 1M calls that is real money.
Optimise: remove fields nobody uses, short but clear names, descriptions only where needed, a short reasoning field (one sentence, not a paragraph), reuse a stable prefix for caching.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Schema design | Shaping the output contract | Output contract बनाना |
| Description | Field instructions | Field के निर्देश |
| Field order | Sequence of generation | Fields का क्रम |
| Schema versioning | Tracking schema changes | Schema के versions |
| Eval set | Labelled test examples | Labelled test examples |

---

## ⚡ 3-Line Summary
English: A schema is part of the prompt: clear names, real types, good descriptions and reasoning first. Keep it small and shallow. Version it and evaluate every change.
Hindi: Schema prompt का हिस्सा है: साफ names, असली types, अच्छे descriptions और reasoning पहले। इसे छोटा और shallow रखो। इसे version करो और हर बदलाव evaluate करो।

---

## ➡️ Next Topic
**099. Common Structured Output Patterns** — reusable recipes: extraction, classification, routing, scoring.
