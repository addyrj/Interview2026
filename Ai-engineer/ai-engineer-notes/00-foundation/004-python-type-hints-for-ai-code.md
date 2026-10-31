---

# 004. Python Type Hints for AI Code
# हिंदी में: AI Code के लिए Python Type Hints

---

## 🔵 Simple Definition (English)
Type hints are labels on variables, parameters and return values, like `def f(x: int) -> str`. Python does not enforce them at runtime, but tools do: mypy/pyright check them, and Pydantic, FastAPI and LangChain read them to validate data and build JSON schemas.

## 🔵 सरल परिभाषा (Hindi)
Type hints variables, parameters और return values पर लगे labels हैं, जैसे `def f(x: int) -> str`। Python runtime पर इन्हें enforce नहीं करता, लेकिन tools करते हैं: mypy/pyright check करते हैं, और Pydantic, FastAPI, LangChain इन्हें पढ़कर validation और JSON schema बनाते हैं।

---

## 🔴 Problem it Solves
LLM code passes dicts and strings everywhere. Without types you find bugs only in production ("KeyError: 'choices'", passing a list where a string was expected). Types document intent, catch bugs in the editor, and let frameworks auto-validate requests and tool arguments.

## 🔴 यह क्यों बना? (Hindi)
LLM code में dicts और strings हर जगह घूमते हैं। Types के बिना bugs production में मिलते हैं ("KeyError: 'choices'", string की जगह list भेज देना)। Types intent document करते हैं, editor में bugs पकड़ते हैं, और frameworks को requests व tool arguments अपने आप validate करने देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Annotate: `def classify(text: str, top_k: int = 3) -> list[str]`
Step 2 → Python stores annotations in func.__annotations__ (no runtime checks)
Step 3 → Static checker (mypy/pyright) reads them and reports mismatches before running
Step 4 → Pydantic reads class annotations and validates real data at runtime
Step 5 → FastAPI reads route annotations to parse JSON, validate, and generate OpenAPI docs
Step 6 → LangChain reads function annotations in @tool to build the schema sent to the LLM
Step 7 → Use Optional/Union, Literal, TypedDict, Protocol, Generic for richer contracts
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Annotate करो: `def classify(text: str, top_k: int = 3) -> list[str]`
Step 2 → Python annotations को func.__annotations__ में रखता है (runtime check नहीं)
Step 3 → mypy/pyright इन्हें पढ़कर चलाने से पहले mismatch बताते हैं
Step 4 → Pydantic class annotations पढ़कर असली data validate करता है
Step 5 → FastAPI route annotations से JSON parse, validate और OpenAPI docs बनाता है
Step 6 → LangChain @tool में annotations से LLM को भेजा जाने वाला schema बनाता है
Step 7 → Optional/Union, Literal, TypedDict, Protocol, Generic से और बारीक contracts
```

---

## 🟡 Real World Example
**Tariff Classification System**: The LLM must return `{"hs_code": "8517.13", "confidence": 0.82}`. A `Literal` type restricts `duty_type` to `"ad_valorem" | "specific"`. A TypedDict describes LangGraph state (`description`, `candidates`, `answer`). When the model returns bad JSON, validation fails fast instead of corrupting the database.

**Amazon AI**: Product attribute extraction returns `Optional[float]` for price, so "missing" is explicit and not a magic `-1`.

## 🟡 Real Example Hindi mein
**Tariff System**: LLM को `{"hs_code": "8517.13", "confidence": 0.82}` देना है। `Literal` से `duty_type` केवल `"ad_valorem" | "specific"` हो सकता है। LangGraph state को TypedDict से describe करते हैं। Model गलत JSON दे तो validation तुरंत fail होता है, database खराब नहीं होता।

**Amazon AI**: Product extraction में price `Optional[float]` है, "missing" साफ़ दिखता है, `-1` जैसा जादुई number नहीं।

---

## 💻 Code Example — Basic
```python
# Basic type hints - pure Python, runs directly
from typing import Literal, Optional  # typing helpers


def build_prompt(description: str, country: str = "IN") -> str:  # str in, str out
    return f"Classify '{description}' for {country}"  # f-string prompt


def pick_best(codes: list[str], scores: list[float]) -> Optional[str]:  # may return None
    if not codes or len(codes) != len(scores):  # guard invalid input
        return None  # explicit "no answer"
    best_index = max(range(len(scores)), key=lambda i: scores[i])  # index of the max score
    return codes[best_index]  # best code


DutyType = Literal["ad_valorem", "specific"]  # only these two strings allowed


def describe(duty: DutyType) -> str:  # checker flags any other string
    return f"duty type: {duty}"  # readable output


print(build_prompt("phone"))  # Classify 'phone' for IN
print(pick_best(["8517", "8471"], [0.7, 0.9]))  # 8471
print(pick_best([], []))  # None
print(describe("specific"))  # duty type: specific
print(build_prompt.__annotations__)  # shows stored annotations
```

## 💻 Code Example — Advanced
```python
# Production: Pydantic v2 validation of LLM output + Protocol + TypedDict + async + errors
import asyncio  # async runtime
import json  # parse LLM JSON text
from typing import Literal, Protocol, TypedDict  # advanced typing tools

from pydantic import BaseModel, Field, ValidationError, field_validator  # pydantic v2


class TariffResult(BaseModel):  # schema the LLM must follow
    hs_code: str = Field(pattern=r"^\d{4}(\.\d{2}){0,2}$")  # 4, 4.2 or 4.2.2 digits
    confidence: float = Field(ge=0, le=1)  # probability range
    duty_type: Literal["ad_valorem", "specific"] = "ad_valorem"  # restricted values
    reasoning: str = Field(max_length=500)  # keep output short (saves tokens)

    @field_validator("hs_code")  # custom validator
    @classmethod
    def strip_spaces(cls, v: str) -> str:  # normalise
        return v.strip()  # remove stray whitespace


class GraphState(TypedDict):  # LangGraph-style state dict
    description: str  # input
    result: TariffResult | None  # output, None until done


class LLM(Protocol):  # structural interface: anything with this method works
    async def complete(self, prompt: str) -> str: ...  # returns raw text


class FakeLLM:  # satisfies the Protocol without inheriting
    async def complete(self, prompt: str) -> str:  # canned reply
        return json.dumps({"hs_code": "8517.13", "confidence": 0.82, "reasoning": "smartphone"})  # JSON text


async def classify(llm: LLM, description: str, retries: int = 2) -> TariffResult:
    """Ask the LLM, validate the JSON, retry on bad output."""
    last_error: Exception | None = None  # remember last failure
    for _ in range(retries + 1):  # initial try + retries
        raw = await llm.complete(f"Return JSON for: {description}")  # call model
        try:  # validate
            return TariffResult.model_validate_json(raw)  # parse + validate in one step
        except ValidationError as exc:  # bad shape or values
            last_error = exc  # keep it
    raise ValueError(f"LLM output invalid after retries: {last_error}")  # fail loudly


async def main() -> None:  # demo
    state: GraphState = {"description": "Android phone", "result": None}  # typed state
    state["result"] = await classify(FakeLLM(), state["description"])  # fill result
    print(state["result"])  # validated object
    try:  # show a validation failure
        TariffResult.model_validate({"hs_code": "abc", "confidence": 2, "reasoning": "x"})  # invalid
    except ValidationError as exc:  # catch
        print(exc.error_count(), "errors")  # 2 errors


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
FastAPI turns annotations into behaviour: body models are parsed and validated, query/path parameters are converted, and `response_model` filters the output. Invalid input becomes an automatic 422 error with details.

```python
# FastAPI: types drive validation + docs
from typing import Annotated, Literal  # Annotated for metadata
from fastapi import FastAPI, Query  # framework
from pydantic import BaseModel, Field  # models

app = FastAPI()  # app


class ClassifyIn(BaseModel):  # input schema
    description: str = Field(min_length=3, max_length=2000)  # bounds protect token cost
    country: Literal["IN", "US", "EU"] = "IN"  # only allowed countries


class ClassifyOut(BaseModel):  # output schema
    hs_code: str  # code
    confidence: float  # score


@app.post("/classify", response_model=ClassifyOut)  # output is validated too
async def classify(
    body: ClassifyIn,  # parsed from JSON
    top_k: Annotated[int, Query(ge=1, le=10)] = 3,  # query param with limits
) -> ClassifyOut:  # return type documented
    return ClassifyOut(hs_code="8517.13", confidence=0.8)  # fake answer
```

---

## 🔗 LangChain / LangGraph Connection
`llm.with_structured_output(PydanticModel)` uses your type hints and Field descriptions to make the model return validated objects. LangGraph state is a `TypedDict` (or Pydantic model); `Annotated[list, add_messages]` tells LangGraph how to merge updates.

```python
# LangChain structured output + LangGraph state typing
from typing import Annotated, TypedDict  # typing
from pydantic import BaseModel, Field  # schema
from langgraph.graph.message import add_messages  # reducer for message lists


class Answer(BaseModel):  # schema sent to the LLM
    hs_code: str = Field(description="HS code like 8517.13")  # description guides the model
    confidence: float = Field(description="0 to 1")  # numeric field


class State(TypedDict):  # LangGraph state
    messages: Annotated[list, add_messages]  # reducer: new messages are appended, not replaced


# Usage (needs OPENAI_API_KEY):
# from langchain_openai import ChatOpenAI
# structured = ChatOpenAI(model="gpt-4o-mini").with_structured_output(Answer)
# result: Answer = structured.invoke("HS code for a smartphone")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking type hints are enforced at runtime
✅ Correct: validate external data with Pydantic.

```python
# Wrong: no error, price stays a string and breaks later math
def total(price: float) -> float:
    return price * 2
total("12")  # returns "1212" silently!

# Right: Pydantic validates/coerces at the boundary
from pydantic import BaseModel
class Item(BaseModel):
    price: float
Item(price="12").price  # 12.0
```

❌ Mistake 2: `list` / `dict` without item types, and mutable defaults
✅ Correct: `list[str]`, `dict[str, float]`, and `Field(default_factory=list)`.

```python
# Wrong
def f(items=[]): ...
# Right
def f(items: list[str] | None = None) -> None:
    items = items or []
```

❌ Mistake 3: Using `Any` everywhere for LLM output. Define a Pydantic model so bad outputs fail early.

---

## 🧠 Tricky Interview Question

**Q**: "Your function is annotated `-> int` but returns a string and nothing fails. Production shows wrong totals. Why, and how do you stop it?"

**Answer**: Python ignores annotations at runtime; they are only metadata. Mypy/pyright in CI would catch it statically, but data coming from outside (LLM JSON, HTTP bodies) is never checked by them. Use Pydantic (or `TypeAdapter`) at boundaries to validate and coerce, run mypy in CI for internal code, and use `strict` mode in Pydantic if coercion ("12" to 12) is unwanted.

---

## ⚫ Interview Questions + Answers

Q1: What is `Optional[str]`? (Easy)
A1: It means `str | None`. The value may be a string or None. It does not mean the argument is optional; that is decided by having a default value.

Q2: What does `-> None` mean? (Easy)
A2: The function returns nothing useful. A checker will complain if you try to use its result.

Q3: What is the difference between `TypedDict` and a Pydantic `BaseModel`? (Medium)
A3: TypedDict is only a static hint for plain dicts: no runtime validation and no methods. BaseModel validates, converts and serialises. LangGraph state often uses TypedDict (fast, simple); API boundaries and LLM outputs use BaseModel.

Q4: What is `Protocol` and why is it useful for LLM clients? (Medium)
A4: A Protocol defines an interface by shape (structural typing). Any class with `async complete(prompt) -> str` is accepted, without inheriting. It makes it easy to pass fakes in tests and swap providers without a shared base class.

Q5: How do type hints help a model call tools correctly? (Hard)
A5: LangChain `@tool` and OpenAI function calling build a JSON schema from parameter annotations and the docstring. `Literal["IN","US"]` becomes an `enum`, `int` becomes `integer`, `Optional` becomes nullable. The model sees this schema in its prompt (these tokens are billed on every call), so precise types reduce wrong arguments, and concise descriptions keep the schema token cost low. The tool runner validates arguments with Pydantic before executing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Function signatures of any shared or production code
- All API request/response bodies and LLM structured output
- LangGraph state and tool definitions

❌ Avoid when:
- Throwaway notebook experiments (light hints are enough)
- Over-engineering with complex generics that hurt readability
- Believing hints replace runtime validation (they do not)

---

## 📊 Visual Diagram
```
  source code with hints
        │
        ├─> mypy / pyright ──> errors BEFORE running (static)
        │
        ├─> Pydantic ────────> validates data AT runtime
        │
        ├─> FastAPI ─────────> parses request, 422 on error, OpenAPI docs
        │
        └─> LangChain @tool ─> JSON schema sent to LLM (tokens!)
```

---

## 💰 Cost Impact
Type hints cost no tokens at runtime. They save money indirectly. Strict output models plus `Field(max_length=...)` cap output size. `with_structured_output` and tool schemas add tokens to every request (a 10-field schema is roughly 150-300 input tokens), so keep descriptions short. Validation failures that trigger a retry double the cost of a call, so use clear schemas and a low temperature. Rough example: 100K calls per day with a 200-token schema on gpt-4o-mini input pricing is 20M tokens, about $3/day; trimming the schema to 120 tokens saves about $1.2/day.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Type hint | Label for a type | type का label |
| Optional | Value or None | value या None |
| Literal | Only fixed values allowed | सिर्फ़ तय values |
| TypedDict | Dict with typed keys | typed keys वाला dict |
| Protocol | Interface by shape | shape वाला interface |
| Pydantic | Runtime validation library | runtime validation library |
| mypy | Static type checker | static type checker |
| Schema | Description of data shape | data के shape का वर्णन |

---

## ⚡ 3-Line Summary
English: Type hints document code and let tools check it, but Python does not enforce them at runtime. Pydantic, FastAPI and LangChain turn hints into validation and JSON schemas. Always validate LLM output at the boundary.
Hindi: Type hints code document करते हैं और tools उन्हें check करते हैं, पर Python runtime पर enforce नहीं करता। Pydantic, FastAPI और LangChain hints से validation और JSON schema बनाते हैं। LLM output हमेशा boundary पर validate करो।

---

## ➡️ Next Topic
**005. Python Error Handling in AI Apps** — LLM calls fail in many ways (rate limits, timeouts, bad JSON), so robust error handling comes next.
