---

# 089. Parsing LLM Output
# हिंदी में: LLM Output को Parse करना

---

## 🔵 Simple Definition (English)
Parsing LLM output means converting the model's raw text into a Python data structure. When native structured output is not available, you extract JSON from the text (strip markdown fences, find the first `{...}`), then convert it with `json.loads` and validate. LangChain offers ready-made output parsers for this.

## 🔵 सरल परिभाषा (Hindi)
LLM output को parse करने का मतलब है model के raw text को Python data structure में बदलना। जब native structured output उपलब्ध नहीं होता, तब text से JSON निकालते हैं (markdown fences हटाना, पहला `{...}` ढूँढना), फिर `json.loads` से convert और validate करते हैं। LangChain इसके लिए तैयार output parsers देता है।

---

## 🔴 Problem it Solves
LLMs are chatty: "Here is the result:\n[json fence]{...}[/fence]\nHope this helps!" A plain `json.loads` crashes on this. Parsing code makes your app robust against such wrappers, trailing commas and single quotes, especially with models or open-source servers that lack strict modes.

## 🔴 यह क्यों बना? (Hindi)
LLMs बातूनी होते हैं: "Here is the result:\n[json fence]{...}[/fence]\nHope this helps!" इस पर सीधा `json.loads` crash करता है। Parsing code आपकी app को ऐसे wrappers, trailing commas और single quotes के सामने मज़बूत बनाता है, खासकर उन models/open-source servers के साथ जिनमें strict mode नहीं है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Get raw text from the LLM
Step 2 → Strip whitespace; remove json code-fence fences
Step 3 → Try json.loads on the whole text first (fast path)
Step 4 → If it fails, find the first balanced {...} or [...] in the text
Step 5 → json.loads that slice
Step 6 → Validate with Pydantic (types, ranges)
Step 7 → On failure raise a clear ParseError (so caller can retry)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → LLM से raw text लो
Step 2 → Whitespace हटाओ; json code-fence fences हटाओ
Step 3 → पहले पूरे text पर json.loads try करो (fast path)
Step 4 → फेल हो तो text में पहला balanced {...} या [...] ढूँढो
Step 5 → उस slice पर json.loads करो
Step 6 → Pydantic से validate करो (types, ranges)
Step 7 → फेल हो तो साफ ParseError raise करो (ताकि caller retry करे)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A self-hosted Llama model replies "Sure! [json fence]{"hs_code": "8518.30",}[/fence]" with a trailing comma. The parser strips the fence, repairs the comma, validates and the pipeline continues instead of failing.

**Amazon-style**: An LLM returns a review analysis wrapped in explanation text; the parser grabs only the JSON object.

## 🟡 Real Example Hindi mein
**Tariff System**: Self-hosted Llama model जवाब देता है "Sure! [json fence]{"hs_code": "8518.30",}[/fence]" — trailing comma के साथ। Parser fence हटाता है, comma ठीक करता है, validate करता है और pipeline fail होने की जगह चलती रहती है।

**Amazon-style**: LLM review analysis को explanation text में लपेटकर देता है; parser सिर्फ JSON object निकालता है।

---

## 💻 Code Example — Basic
```python
# Basic: robust JSON extraction from chatty LLM text. Pure Python, runs offline.
import json                                          # JSON parser
import re                                            # regex for fence removal
from typing import Any                               # type hint

class ParseError(ValueError):
    """Raised when no valid JSON can be extracted."""

def extract_json(text: str) -> Any:
    """Extract and parse the first JSON object/array found in text."""
    cleaned = text.strip()                                        # remove outer whitespace
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned)    # strip code fences
    try:
        return json.loads(cleaned)                                # fast path: already clean
    except json.JSONDecodeError:
        pass                                                      # fall through to search
    start = min((i for i in (cleaned.find("{"), cleaned.find("[")) if i != -1), default=-1)
    if start == -1:                                               # no JSON-looking char at all
        raise ParseError("no JSON found")
    opener = cleaned[start]                                       # '{' or '['
    closer = "}" if opener == "{" else "]"                        # matching closer
    depth = 0                                                     # bracket depth counter
    for i in range(start, len(cleaned)):                          # scan forward
        if cleaned[i] == opener:
            depth += 1                                            # entering nested level
        elif cleaned[i] == closer:
            depth -= 1                                            # leaving a level
            if depth == 0:                                        # balanced -> done
                snippet = cleaned[start:i + 1]                    # exact JSON slice
                snippet = re.sub(r",\s*([}\]])", r"\1", snippet)  # remove trailing commas
                try:
                    return json.loads(snippet)
                except json.JSONDecodeError as exc:
                    raise ParseError(f"invalid JSON: {exc}") from exc
    raise ParseError("unbalanced brackets")

chatty = 'Sure! Here you go:\n```json\n{"hs_code": "8518.30", "duty_percent": 0,}\n```\nHope it helps!'
print(extract_json(chatty))                                       # {'hs_code': '8518.30', 'duty_percent': 0}
try:
    extract_json("I cannot help with that.")                      # no JSON
except ParseError as exc:
    print("ParseError:", exc)
```

## 💻 Code Example — Advanced
```python
# Production: parser + Pydantic + async LLM call with parse-aware retry.
import asyncio
import json
import re
from typing import Optional, TypeVar
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError

client = AsyncOpenAI()
T = TypeVar("T", bound=BaseModel)                     # any Pydantic model

class TariffResult(BaseModel):
    hs_code: str
    duty_percent: float = Field(ge=0, le=100)

FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)   # capture inside fences

def parse_model(text: str, model: type[T]) -> T:
    """Turn raw LLM text into a validated Pydantic object."""
    m = FENCE.search(text)                             # prefer fenced block
    candidate = m.group(1) if m else text              # else whole text
    start, end = candidate.find("{"), candidate.rfind("}")   # outermost braces
    if start == -1 or end <= start:
        raise ValueError("no JSON object in output")
    return model.model_validate_json(candidate[start:end + 1])   # parse + validate

async def classify(product: str, retries: int = 2) -> Optional[TariffResult]:
    """Ask for JSON in the prompt, parse, retry once or twice on failure."""
    messages = [{"role": "system", "content": 'Reply with JSON only: {"hs_code": str, "duty_percent": number}'},
                {"role": "user", "content": product}]
    for attempt in range(retries + 1):                 # initial try + retries
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, max_tokens=150, temperature=0)
        except OpenAIError as exc:
            print("API error:", exc)
            return None
        text = resp.choices[0].message.content or ""
        try:
            return parse_model(text, TariffResult)
        except (ValueError, ValidationError) as exc:   # JSONDecode & Validation are ValueErrors
            print(f"parse failed (attempt {attempt}): {exc}")
            messages += [{"role": "assistant", "content": text},
                         {"role": "user", "content": f"Invalid: {exc}. Return only valid JSON."}]
    return None

if __name__ == "__main__":
    print(asyncio.run(classify("Wireless earbuds")))   # needs API key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/classify-raw", response_model=TariffResult)
async def classify_raw(product: str) -> TariffResult:
    result = await classify(product)                   # parser-based pipeline
    if result is None:
        raise HTTPException(status_code=502, detail="LLM output could not be parsed")
    return result
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

parser = PydanticOutputParser(pydantic_object=TariffResult)       # parse + validate
prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the product.\n{format_instructions}"),   # parser writes the instructions
    ("human", "{product}"),
]).partial(format_instructions=parser.get_format_instructions())
chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | parser   # LCEL
result = chain.invoke({"product": "Wireless earbuds"})            # TariffResult
# JsonOutputParser -> dict; StrOutputParser -> plain string.
# LangGraph node: wrap chain.invoke in try/except OutputParserException.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `json.loads(response)` directly
✅ Correct: Clean fences and search for the JSON block.

```python
# Wrong:
# data = json.loads(text)   # JSONDecodeError on "```json ..."
# Right:
# data = extract_json(text)
```

❌ Mistake 2: Parsing with regex like `re.findall(r"\{.*\}", text)` on nested JSON
✅ Correct: Count brackets or use `rfind("}")`; regex greediness breaks on multiple objects.

```python
# Wrong: re.search(r"\{.*?\}", text)  # stops at the first inner }
# Right: bracket-depth scan (see extract_json)
```

---

## 🧠 Tricky Interview Question

**Q**: "Your parser works in testing but in production 2% of replies still fail. The raw text looks fine to a human. What do you check?"

**Answer**: (1) Truncation (`finish_reason == "length"`), (2) smart quotes or Unicode characters, (3) JSON inside a string field containing braces that confuses naive bracket counting (need string-aware scanning), (4) comments or `...` placeholders, (5) the model apologising before the JSON. Log the raw text of failures, add the failing cases to a test set, and prefer native structured output or tool calling to avoid parsing entirely.

---

## ⚫ Interview Questions + Answers

Q1: Why not call `json.loads` directly on LLM text?
A1: The text often contains explanations or code fences, so parsing raises an error.

Q2: Name a LangChain output parser.
A2: `StrOutputParser`, `JsonOutputParser`, `PydanticOutputParser`.

Q3: What does `get_format_instructions()` do?
A3: Produces prompt text describing the required JSON format so the model knows how to answer.

Q4: What is "output repair"?
A4: Fixing small defects such as trailing commas, single quotes or missing braces automatically (e.g. `json-repair` library or LangChain `OutputFixingParser`), or asking the LLM to fix its output.

Q5: When is parsing better than native structured output?
A5: For models or servers without schema support, for streaming text mixed with JSON, or for reasoning models where you let the model think first and then extract the final JSON block. Otherwise, native modes are more reliable and cheaper to maintain.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Open-source or local models
- Legacy prompts you cannot change
- Extracting JSON after a chain-of-thought

❌ Avoid when:
- Native structured output or tool calling is available

---

## 📊 Visual Diagram
```
 raw text: "Sure! ```json {...,} ``` Hope it helps"
      │
      ▼ strip fences / find {...}
 candidate: {"hs_code":"8518.30",}
      │
      ▼ repair trailing comma
 json.loads ─► dict ─► Pydantic validate ─► object
      │ fail
      ▼
 ParseError ─► retry with error message
```

---

## 💰 Cost Impact
Parsing itself is free (local CPU). The hidden cost is retries: each parse failure that triggers a re-ask resends the conversation. Prompt instructions for format add input tokens (format instructions can be 100+ tokens).
Optimise: repair locally before re-asking, limit retries to 1-2, shorten format instructions, move to native structured output to remove the problem.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Output parser | Converts text to data | Text को data में बदलने वाला |
| Code fence | json fence block in markdown | Markdown का code block |
| Trailing comma | Extra comma before } | अंत में फालतू comma |
| Output repair | Auto-fix broken JSON | टूटे JSON को ठीक करना |
| ParseError | Failure to extract data | Parse की विफलता |

---

## ⚡ 3-Line Summary
English: Parsing turns raw LLM text into data by stripping fences, finding the JSON block and validating it. Use it for models without native structured output. Keep a clear error path for retries.
Hindi: Parsing fences हटाकर, JSON block ढूँढकर और validate करके raw LLM text को data बनाती है। जिन models में native structured output नहीं है वहाँ इसे use करो। Retries के लिए साफ error path रखो।

---

## ➡️ Next Topic
**090. Output Validation** — checking that parsed data is not just well-formed but also correct and safe.
