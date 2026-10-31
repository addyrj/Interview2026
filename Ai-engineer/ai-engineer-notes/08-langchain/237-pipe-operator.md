---

# 237. Pipe Operator (|)
# हिंदी में: Pipe Operator (|)

---

## 🔵 Simple Definition (English)
In LangChain the pipe `|` connects two Runnables so the output of the left becomes the input of the right. `a | b | c` creates a `RunnableSequence`. It works because Python calls `__or__` on the left object, and Runnable defines it.

## 🔵 सरल परिभाषा (Hindi)
LangChain में pipe `|` दो Runnables को जोड़ता है: बाएँ का output दाएँ का input बनता है। `a | b | c` एक `RunnableSequence` बनाता है। यह इसलिए चलता है क्योंकि Python बाएँ object पर `__or__` बुलाता है और Runnable इसे define करता है।

---

## 🔴 Problem it Solves
Nested function calls `parser(llm(prompt(x)))` read inside-out and lose features: no streaming, no async, no tracing per step. The pipe reads left-to-right like a Unix pipeline and the resulting object keeps all Runnable features.

## 🔴 यह क्यों बना? (Hindi)
Nested calls `parser(llm(prompt(x)))` अंदर से बाहर पढ़े जाते हैं और features खो देते हैं: streaming, async, per-step tracing नहीं। Pipe Unix pipeline की तरह बाएँ से दाएँ पढ़ा जाता है और नया object सारे Runnable features रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Python evaluates  a | b  by calling a.__or__(b)
Step 2 → Runnable.__or__ coerces b: function -> RunnableLambda, dict -> RunnableParallel
Step 3 → Returns RunnableSequence(first=a, middle=[], last=b); chaining flattens it
Step 4 → invoke(x): out1 = a.invoke(x); out2 = b.invoke(out1)
Step 5 → stream(x): streams the LAST component that supports streaming transforms
Step 6 → Each step becomes a child run in traces
Step 7 → Left side str/dict (non-Runnable) uses __ror__: {"k": r} | prompt works
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Python  a | b  के लिए a.__or__(b) बुलाता है
Step 2 → b को coerce: function -> RunnableLambda, dict -> RunnableParallel
Step 3 → RunnableSequence(first=a, ..., last=b) लौटता है; chaining flatten होती है
Step 4 → invoke(x): out1 = a.invoke(x); out2 = b.invoke(out1)
Step 5 → stream(x): chain के streaming-capable हिस्से token-by-token बहते हैं
Step 6 → हर step traces में child run बनता है
Step 7 → बाएँ में non-Runnable (dict) हो तो __ror__ काम आता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: `normalize | retrieve | prompt | llm | parser | validate`. `normalize` and `validate` are plain Python functions auto-wrapped as RunnableLambda. A failure shows exactly which step broke in LangSmith. **Zomato AI**: `intent_classifier | route | answer_writer`.

## 🟡 Real Example Hindi mein
**Tariff System**: `normalize | retrieve | prompt | llm | parser | validate`। `normalize` और `validate` सादे Python functions हैं जो अपने-आप RunnableLambda बन जाते हैं। कोई step fail हो तो LangSmith में साफ दिखता है कौन सा। **Zomato AI**: `intent_classifier | route | answer_writer`।

---

## 💻 Code Example — Basic
```python
# Runs offline: what `|` really builds
from langchain_core.runnables import RunnableLambda

strip = RunnableLambda(lambda s: s.strip())  # step 1
upper = RunnableLambda(lambda s: s.upper())  # step 2
exclaim = RunnableLambda(lambda s: s + "!")  # step 3

chain = strip | upper | exclaim  # builds a RunnableSequence
print(type(chain).__name__)  # RunnableSequence
print(chain.invoke("  hs code  "))  # HS CODE!

# Plain functions are coerced when at least one side is a Runnable:
chain2 = strip | (lambda s: s.replace(" ", "_")) | exclaim
print(chain2.invoke(" hs code "))  # hs_code!

# Dict on the left becomes RunnableParallel via __ror__:
chain3 = {"a": strip, "b": upper} | RunnableLambda(lambda d: f"{d['a']}|{d['b']}")
print(chain3.invoke(" x "))  # x| X ... (a stripped, b uppercased of original)

# Equivalent without pipe:
from langchain_core.runnables import RunnableSequence
print(RunnableSequence(strip, upper, exclaim).invoke(" ok "))  # OK!
```

## 💻 Code Example — Advanced
```python
# Production pipeline of many pipes with per-step error context and async
import asyncio
from pydantic import BaseModel
from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class Out(BaseModel):
    hs_code: str
    confidence: float

def normalize(text: str) -> dict:
    cleaned = " ".join(text.lower().split())  # collapse whitespace, lowercase
    if not cleaned:
        raise ValueError("empty product description")  # fail fast
    return {"product": cleaned}

def validate(out: Out) -> Out:
    if out.confidence < 0.5:
        raise ValueError(f"low confidence {out.confidence}")  # caller can send to review
    return out

prompt = ChatPromptTemplate.from_template("HS code and confidence for: {product}")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Out)

chain = (
    RunnableLambda(normalize).with_config(run_name="normalize")
    | prompt
    | llm
    | RunnableLambda(validate).with_config(run_name="validate")
)

async def classify(text: str) -> Out | None:
    try:
        return await chain.ainvoke(text, config=RunnableConfig(tags=["tariff"]))
    except ValueError as exc:  # business-rule failures
        print("needs review:", exc)
        return None
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/classify")
async def classify_route(product: str) -> dict:
    result = await classify(product)  # pipe chain above
    if result is None:
        raise HTTPException(status_code=422, detail="Needs human review")
    return result.model_dump()
# Tip: build `chain` once at import/startup, not per request.
```

---

## 🔗 LangChain / LangGraph Connection
`|` is LCEL. In LangGraph you usually add Runnables as nodes instead of piping, but each node can itself be a piped chain. For debugging: `chain.get_graph().draw_ascii()`; `chain.steps` (on RunnableSequence) lists components.

```python
# graph.add_node("classify", prompt | llm)    # a piped chain as one node
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Piping two non-Runnables
```python
# Wrong: (lambda x: x) | (lambda y: y)   # TypeError: neither is a Runnable
# Right
RunnableLambda(lambda x: x) | (lambda y: y)
```

❌ Mistake 2: Mismatched types between steps
```python
# Wrong: prompt | parser          # parser expects a model message, not PromptValue
# Right: prompt | llm | parser
```

---

## 🧠 Tricky Interview Question
**Q**: "Does `prompt | llm | parser` stream tokens end-to-end? What if you add a `RunnableLambda(lambda s: s.upper())` at the end?"

**Answer**: Streaming works end-to-end if every step supports streaming transform of chunks. `StrOutputParser` does. A plain `RunnableLambda` consumes the full input before calling the function, so it breaks token streaming: output arrives once at the end. To keep streaming, write a generator-based `RunnableGenerator` / `transform` that processes chunks.

---

## ⚫ Interview Questions + Answers

Q1: What does `a | b` return? (Easy)
A1: A `RunnableSequence`; it is itself a Runnable.

Q2: Can I pipe a dict? (Easy)
A2: Yes; a dict of runnables (on the left or inside the chain) is coerced to `RunnableParallel`.

Q3: How is `|` implemented? (Medium)
A3: `Runnable.__or__` and `__ror__` call `coerce_to_runnable` and wrap in `RunnableSequence`.

Q4: How to debug a long chain? (Medium)
A4: Use LangSmith traces, `chain.get_graph().print_ascii()`, add `RunnableLambda(print_and_return)` taps, or run sub-chains separately.

Q5: Explain streaming behavior across pipes. (Hard)
A5: `stream` calls `transform` through each step; components implementing `transform` stream chunks onward, while components that don't (default) buffer all input first. The first non-streaming step becomes a barrier, so latency to the first token worsens.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Linear pipelines that read well left-to-right

❌ Avoid when:
- Heavy branching/loops (use LangGraph); very long chains become hard to read: split into named sub-chains

---

## 📊 Visual Diagram
```
 x ─► [normalize] ─► [prompt] ─► [llm] ─► [parser] ─► [validate] ─► y
        │              │          │         │            │
      lambda        template    model      str/pydantic  lambda
 chain = normalize | prompt | llm | parser | validate
```

---

## 💰 Cost Impact
Pipes add no tokens. Put cheap deterministic steps (normalise, cache lookup, regex, validation) BEFORE the LLM to avoid calls: e.g., `cache_lookup | llm_if_miss`. Fewer LLM calls = lower cost. Make sure retries (`with_retry`) wrap only the LLM step, not the entire chain.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pipe | Connect output to input | Output को input से जोड़ना |
| RunnableSequence | Ordered chain | क्रमबद्ध chain |
| Coercion | Auto-wrap into Runnable | अपने-आप Runnable बनाना |
| `__or__` | Python pipe hook | Python का | hook |
| Barrier | Non-streaming step | Streaming रोकने वाला step |

---

## ⚡ 3-Line Summary
English: `|` composes Runnables left-to-right into a RunnableSequence. Functions and dicts are auto-converted. Non-streaming steps break token streaming.
Hindi: `|` Runnables को बाएँ से दाएँ RunnableSequence में जोड़ता है। Functions और dicts अपने-आप convert होते हैं। Non-streaming step token streaming तोड़ देता है।

---

## ➡️ Next Topic
**238. RunnablePassthrough** — carrying the original input forward alongside computed values.
