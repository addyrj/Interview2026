---

# 003. Python Classes + OOP for LangChain
# हिंदी में: LangChain के लिए Python Classes + OOP

---

## 🔵 Simple Definition (English)
A class is a blueprint that bundles data (attributes) and behaviour (methods). OOP concepts you need for AI work: `__init__`, inheritance, abstract base classes, dataclasses, and Pydantic models. LangChain is built from classes, so custom tools, retrievers and callbacks are made by subclassing.

## 🔵 सरल परिभाषा (Hindi)
Class एक blueprint है जो data (attributes) और behaviour (methods) को साथ रखता है। AI काम के लिए ज़रूरी OOP: `__init__`, inheritance, abstract base class, dataclass और Pydantic model। LangChain classes से बना है, इसलिए custom tools, retrievers और callbacks subclass करके बनते हैं।

---

## 🔴 Problem it Solves
Plain functions with global variables get messy: where do you keep the API client, the prompt, the config, the cache? A class groups them and lets you swap parts (OpenAI vs Anthropic) through a shared interface. Without OOP you cannot extend LangChain's `BaseRetriever`, `BaseCallbackHandler` or `BaseTool`.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ functions और global variables से code उलझ जाता है: API client, prompt, config, cache कहाँ रखें? Class इन्हें group करती है और एक common interface से parts बदलने देती है (OpenAI की जगह Anthropic)। OOP के बिना LangChain के `BaseRetriever`, `BaseCallbackHandler`, `BaseTool` को extend नहीं कर सकते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define class with __init__(self, ...) to store dependencies (client, model, config)
Step 2 → Add methods that use self (classify, build_prompt)
Step 3 → Define an abstract base class (ABC) with @abstractmethod to set the contract
Step 4 → Subclass it: each subclass implements the abstract methods (OpenAIClassifier, MockClassifier)
Step 5 → Code depends on the base type, not the concrete class (polymorphism)
Step 6 → Use @dataclass for plain data, Pydantic BaseModel for validated data
Step 7 → In LangChain, subclass BaseRetriever / BaseCallbackHandler and override the documented method
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → __init__(self, ...) वाली class बनाओ, dependencies (client, model, config) store करो
Step 2 → self use करने वाले methods जोड़ो (classify, build_prompt)
Step 3 → ABC और @abstractmethod से contract तय करो
Step 4 → Subclass बनाओ: हर subclass abstract methods implement करे (OpenAIClassifier, MockClassifier)
Step 5 → Code base type पर depend करे, concrete class पर नहीं (polymorphism)
Step 6 → सादे data के लिए @dataclass, validated data के लिए Pydantic BaseModel
Step 7 → LangChain में BaseRetriever / BaseCallbackHandler subclass करके method override करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: An abstract `Classifier` class defines `async classify(description) -> Classification`. `LLMClassifier` calls GPT, `RuleClassifier` uses keyword rules, and `MockClassifier` is used in tests. FastAPI depends on `Classifier`, so switching the model needs no route changes.

**Zomato AI**: A `BaseRetriever` subclass searches restaurant menus; a callback handler logs tokens per request.

## 🟡 Real Example Hindi mein
**Tariff System**: Abstract `Classifier` class में `async classify(description)` तय है। `LLMClassifier` GPT call करता है, `RuleClassifier` keywords से, `MockClassifier` tests में। FastAPI `Classifier` पर depend करता है, इसलिए model बदलने पर routes नहीं बदलते।

**Zomato AI**: `BaseRetriever` subclass restaurant menus search करता है; callback handler हर request के tokens log करता है।

---

## 💻 Code Example — Basic
```python
# Basic OOP - pure Python, runs directly
from dataclasses import dataclass  # auto-generates __init__ and __repr__


@dataclass  # a simple data holder
class Classification:  # result of a classification
    hs_code: str  # the HS code
    confidence: float  # 0.0 to 1.0


class RuleClassifier:  # a normal class
    def __init__(self, rules: dict[str, str]) -> None:  # constructor stores the rules
        self.rules = rules  # keyword -> HS code mapping

    def classify(self, description: str) -> Classification:  # method uses self
        text = description.lower()  # normalise text
        for keyword, code in self.rules.items():  # loop over rules
            if keyword in text:  # keyword found
                return Classification(code, 0.9)  # return a match
        return Classification("0000", 0.0)  # default: unknown


clf = RuleClassifier({"phone": "8517", "shoe": "6403"})  # create an object
print(clf.classify("Smartphone 128GB"))  # Classification(hs_code='8517', confidence=0.9)
print(clf.classify("banana"))  # Classification(hs_code='0000', confidence=0.0)
```

## 💻 Code Example — Advanced
```python
# Production style: abstract interface + two implementations + async + error handling
import asyncio  # async runtime
from abc import ABC, abstractmethod  # abstract base class tools
from pydantic import BaseModel, Field  # validated data model (pydantic v2)


class Classification(BaseModel):  # validated output model
    hs_code: str = Field(pattern=r"^\d{4}(\.\d{2})?$")  # 4 digits or 4.2 digits
    confidence: float = Field(ge=0.0, le=1.0)  # 0..1


class ClassifierError(Exception):  # our own error type
    """Raised when classification fails."""


class Classifier(ABC):  # contract every classifier must follow
    @abstractmethod  # subclasses MUST implement this
    async def classify(self, description: str) -> Classification:  # async interface
        ...  # no body in the abstract method


class RuleClassifier(Classifier):  # cheap, free, deterministic
    def __init__(self, rules: dict[str, str]) -> None:  # store rules
        self._rules = rules  # underscore = internal

    async def classify(self, description: str) -> Classification:  # implements contract
        for word, code in self._rules.items():  # check each rule
            if word in description.lower():  # match
                return Classification(hs_code=code, confidence=0.95)  # confident
        raise ClassifierError("no rule matched")  # signal "I don't know"


class FakeLLMClassifier(Classifier):  # stands in for a real LLM call
    async def classify(self, description: str) -> Classification:  # same signature
        await asyncio.sleep(0.05)  # pretend network time
        return Classification(hs_code="8517.13", confidence=0.7)  # canned answer


class FallbackClassifier(Classifier):  # composition: try cheap first, then LLM
    def __init__(self, primary: Classifier, secondary: Classifier) -> None:  # two strategies
        self._primary = primary  # tried first
        self._secondary = secondary  # tried on failure

    async def classify(self, description: str) -> Classification:  # same interface
        try:  # try the free rule-based path
            return await self._primary.classify(description)  # no tokens used
        except ClassifierError:  # rules failed
            return await self._secondary.classify(description)  # pay tokens only now


async def main() -> None:  # demo
    clf: Classifier = FallbackClassifier(RuleClassifier({"phone": "8517"}), FakeLLMClassifier())  # compose
    print(await clf.classify("Android phone"))  # served by rules
    print(await clf.classify("industrial widget"))  # falls back to LLM


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Store long-lived objects (classifier, client) on the class and create them once at startup, not per request. Routes depend on the abstract type, so tests can inject a fake.

```python
# FastAPI + class-based service with dependency
from fastapi import Depends, FastAPI  # framework + DI
from pydantic import BaseModel  # request model

app = FastAPI()  # app


class Req(BaseModel):  # request body
    description: str  # product text


class ClassifierService:  # service class holds state
    def __init__(self) -> None:  # constructor
        self.calls = 0  # simple counter

    async def classify(self, text: str) -> str:  # business method
        self.calls += 1  # update state
        return "8517"  # fake code


service = ClassifierService()  # created once at import time


def get_service() -> ClassifierService:  # dependency provider
    return service  # same instance for all requests


@app.post("/classify")  # route
async def classify(req: Req, svc: ClassifierService = Depends(get_service)) -> dict[str, str | int]:  # DI
    return {"code": await svc.classify(req.description), "calls": svc.calls}  # JSON
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's extension points are classes: `BaseRetriever` (override `_get_relevant_documents`), `BaseCallbackHandler` (override `on_llm_end`), `BaseTool`. Pydantic models describe structured output and tool inputs.

```python
# Custom LangChain retriever and callback (langchain-core)
from langchain_core.callbacks import BaseCallbackHandler  # callback base class
from langchain_core.documents import Document  # document type
from langchain_core.retrievers import BaseRetriever  # retriever base class


class KeywordRetriever(BaseRetriever):  # our custom retriever
    docs: list[Document]  # pydantic field (BaseRetriever is a pydantic model)

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:  # required override
        return [d for d in self.docs if query.lower() in d.page_content.lower()]  # naive keyword match


class TokenLogger(BaseCallbackHandler):  # logs token usage
    def on_llm_end(self, response, **kwargs) -> None:  # called when LLM call ends
        usage = (response.llm_output or {}).get("token_usage", {})  # may be empty for some providers
        print("tokens:", usage)  # print usage


r = KeywordRetriever(docs=[Document(page_content="Phones are in chapter 85")])  # build
print(r.invoke("phones"))  # returns the matching document
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutable default argument or shared class attribute
✅ Correct: create mutable state in `__init__`.

```python
# Wrong: the same list is shared by ALL instances (chat histories leak between users)
class Memory:
    history = []
    def add(self, m): self.history.append(m)

# Right: each instance gets its own list
class Memory:
    def __init__(self) -> None:
        self.history: list[str] = []
    def add(self, m: str) -> None:
        self.history.append(m)
```

❌ Mistake 2: Creating a new client object (new HTTP connection pool) on every request
✅ Correct: build it once and reuse it.

```python
# Wrong: new client per request, slow and leaks connections
@app.post("/ask")
async def ask(q: str):
    client = AsyncOpenAI()
    ...
# Right: one shared client created at startup
client = AsyncOpenAI()
```

❌ Mistake 3: Forgetting `super().__init__()` when subclassing a LangChain/Pydantic class with a custom `__init__`. Prefer declaring fields and not overriding `__init__`.

---

## 🧠 Tricky Interview Question

**Q**: "Two users of your chatbot sometimes see each other's messages. The code has `class Chat: messages = []`. Why?"

**Answer**: `messages = []` is a class attribute: one list shared by every instance (and the same object across requests in a long-running server). Appending from user A is visible to user B. This is also a privacy leak. Fix: initialise `self.messages = []` in `__init__`, or use `field(default_factory=list)` in a dataclass, and key sessions by `session_id` in a store such as Redis.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a class and an object? (Easy)
A1: A class is the blueprint; an object (instance) is one thing built from it, with its own attribute values. `Classifier` is the class; `clf = Classifier()` is an object.

Q2: What does `self` mean? (Easy)
A2: It is the instance the method is called on. `clf.classify(x)` is the same as `Classifier.classify(clf, x)`. It lets each object keep its own data.

Q3: Dataclass vs Pydantic BaseModel? (Medium)
A3: A dataclass only generates boilerplate and does no validation at runtime (type hints are not enforced). Pydantic validates and coerces input, parses JSON and generates JSON Schema, which is why FastAPI and LangChain use it for request bodies and LLM structured output. Use dataclass for internal plain data, Pydantic at boundaries.

Q4: Why prefer composition over inheritance for AI pipelines? (Medium)
A4: Inheritance chains get rigid (LLMRuleCachedClassifier...). Composition combines small parts at runtime: `FallbackClassifier(primary, secondary)`. It is easier to test with fakes and to add caching or guardrails as wrappers.

Q5: How would you design swappable LLM providers in a codebase? (Hard)
A5: Define an abstract `LLMClient` with `async complete(messages, **opts) -> LLMResult` where `LLMResult` holds text and token usage. Implement `OpenAIClient`, `AnthropicClient`, `FakeClient`. Inject through FastAPI `Depends`. Normalise errors into your own exceptions (RateLimitError, ContextTooLong) so retry logic is provider-independent. In LangChain you get this free through `BaseChatModel`; with `init_chat_model` the provider is a config string.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You hold state (clients, config, caches) that several methods share
- You need swappable implementations (real vs mock, OpenAI vs Anthropic)
- You extend a framework (LangChain base classes)

❌ Avoid when:
- A single pure function is enough (no state)
- Inheritance is used only to share two lines of code (use a helper function)
- You create deep hierarchies that nobody understands

---

## 📊 Visual Diagram
```
            ┌───────────────────┐
            │  Classifier (ABC) │  classify(desc) -> Classification
            └─────────┬─────────┘
        ┌─────────────┼───────────────┐
        ▼             ▼               ▼
 RuleClassifier  LLMClassifier  FallbackClassifier(primary, secondary)
   (free)         (tokens)         └─ tries rule, then LLM

 FastAPI route ──depends on──> Classifier  (never on a concrete class)
```

---

## 💰 Cost Impact
OOP does not use tokens by itself, but design controls cost. A `FallbackClassifier` that tries free rules first avoids the LLM for easy items: if 50 percent of 100K daily queries match rules, you save 50K calls (about 600 tokens each = 30M tokens, roughly $4.5/day on gpt-4o-mini input pricing). A shared client avoids connection setup overhead. Keep token usage inside the result object (`LLMResult.usage`) so every class reports spend. Optimise by caching in a wrapper class and by setting `max_tokens` in one place.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Class | Blueprint for objects | objects का blueprint |
| Instance | One object made from a class | class से बना एक object |
| `__init__` | Constructor method | constructor method |
| Inheritance | Subclass reuses parent | subclass parent को reuse करे |
| ABC | Abstract base class (interface) | abstract interface class |
| Polymorphism | Same call, different behaviour | एक call, अलग behaviour |
| Composition | Build by combining objects | objects जोड़कर बनाना |
| Dataclass | Auto-boilerplate data class | auto data class |

---

## ⚡ 3-Line Summary
English: Classes bundle state and behaviour; ABCs define contracts so parts are swappable. LangChain extension points (retriever, callback, tool) are classes. Prefer composition, Pydantic at boundaries, and never share mutable class attributes.
Hindi: Classes state और behaviour को जोड़ती हैं; ABC contract देकर parts बदलना आसान करता है। LangChain के extension points classes हैं। Composition चुनो, boundaries पर Pydantic लगाओ, और mutable class attributes share मत करो।

---

## ➡️ Next Topic
**004. Python Type Hints for AI Code** — type hints power Pydantic, FastAPI validation and LangChain tool schemas, so they are the next building block.
