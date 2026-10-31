---

# 260. Chains — Legacy
# हिंदी में: Chains — पुराना तरीका (Legacy)

---

## 🔵 Simple Definition (English)
Legacy chains are the older LangChain classes (`LLMChain`, `SimpleSequentialChain`, `SequentialChain`, `TransformChain`, `RetrievalQA`, ...) that wire prompt, model, and parsing into a fixed pipeline. They are now deprecated in favour of **LCEL** (`prompt | llm | parser`) and LangGraph, but interviews and old codebases still use them.

## 🔵 सरल परिभाषा (Hindi)
Legacy chains LangChain की पुरानी classes हैं (`LLMChain`, `SimpleSequentialChain`, `SequentialChain`, `TransformChain`, `RetrievalQA`, ...) जो prompt, model और parsing को एक fixed pipeline में जोड़ती हैं। अब इनकी जगह **LCEL** (`prompt | llm | parser`) और LangGraph आ गए हैं, पर interviews और पुराने codebases में ये अब भी मिलती हैं।

---

## 🔴 Problem it Solves
- Early LLM apps repeated the same glue code: fill template, call model, parse output.
- Multi-step workflows (summarise, then translate, then classify) needed structure.
- Why replaced: hidden magic, hard to stream, hard to customise, weak async, many special classes with different interfaces.

## 🔴 यह क्यों बना? (Hindi)
- शुरुआती LLM apps में वही glue code बार-बार था: template भरो, model बुलाओ, output parse करो।
- Multi-step workflows (summarise, फिर translate, फिर classify) को structure चाहिए था।
- बदला क्यों गया: छिपा हुआ जादू, streaming कठिन, customise करना मुश्किल, कमज़ोर async, और अलग-अलग interface वाली बहुत सारी special classes।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build a prompt template with input variables
Step 2 → LLMChain(llm=llm, prompt=prompt) bundles prompt + model
Step 3 → chain.invoke({"var": value}) runs prompt → model
Step 4 → Output arrives in a dict under key "text"
Step 5 → SequentialChain connects chains: output keys of A become input keys of B
Step 6 → Legacy chains use input_keys / output_keys to pass data around
Step 7 → Modern replacement: prompt | llm | StrOutputParser() (LCEL)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Input variables वाला prompt template बनाओ
Step 2 → LLMChain(llm=llm, prompt=prompt) prompt + model को जोड़ता है
Step 3 → chain.invoke({"var": value}) prompt → model चलाता है
Step 4 → Output dict में "text" key के अंदर आता है
Step 5 → SequentialChain chains जोड़ता है: A की output keys, B की input keys बनती हैं
Step 6 → Legacy chains data पास करने के लिए input_keys / output_keys इस्तेमाल करती हैं
Step 7 → आधुनिक विकल्प: prompt | llm | StrOutputParser() (LCEL)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A two-step legacy pipeline: chain 1 "extract product facts from the description", chain 2 "pick the HS code from those facts". With `SequentialChain` the output key `facts` of chain 1 feeds chain 2. Today you write `extract | classify` in LCEL.
**Zomato AI**: chain 1 summarises a review, chain 2 labels sentiment.

## 🟡 Real Example Hindi mein
**Tariff System**: दो-step legacy pipeline: chain 1 "description से product facts निकालो", chain 2 "उन facts से HS code चुनो"। `SequentialChain` में chain 1 की output key `facts` chain 2 को जाती है। आज LCEL में `extract | classify` लिखते हैं।
**Zomato AI**: chain 1 review का सार बनाती है, chain 2 sentiment लेबल करती है।

---

## 💻 Code Example — Basic
```python
# Basic: how a legacy SequentialChain works internally (pure Python, runnable)
from typing import Callable, Dict, List

Step = Callable[[Dict[str, str]], Dict[str, str]]    # a "chain": dict in -> dict out

def extract_facts(inputs: Dict[str, str]) -> Dict[str, str]:
    # Fake LLM #1: turns a description into short facts
    return {"facts": f"electronic, battery powered, audio ({inputs['description']})"}

def classify(inputs: Dict[str, str]) -> Dict[str, str]:
    # Fake LLM #2: uses the 'facts' key produced by step 1
    code = "8518.22" if "audio" in inputs["facts"] else "9999.99"
    return {"hs_code": code}

def run_sequential(steps: List[Step], inputs: Dict[str, str]) -> Dict[str, str]:
    state = dict(inputs)                              # copy so we do not mutate the caller's dict
    for step in steps:
        state.update(step(state))                     # merge outputs: later steps see earlier keys
    return state

if __name__ == "__main__":
    result = run_sequential([extract_facts, classify], {"description": "Bluetooth speaker"})
    print(result["hs_code"])                          # 8518.22
    print(sorted(result))                             # ['description', 'facts', 'hs_code']
```

## 💻 Code Example — Advanced
```python
# Legacy chain vs LCEL: same two-step task written both ways (async, typed, error handling)
import asyncio
import warnings

from langchain.chains import LLMChain, SequentialChain       # legacy imports
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

warnings.filterwarnings("ignore", category=DeprecationWarning)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=150)

facts_prompt = PromptTemplate.from_template("List 3 key facts for customs about: {description}")
code_prompt = PromptTemplate.from_template("Given these facts:\n{facts}\nGive the most likely HS code only.")

# ---------- LEGACY ----------
facts_chain = LLMChain(llm=llm, prompt=facts_prompt, output_key="facts")   # output_key names the result
code_chain = LLMChain(llm=llm, prompt=code_prompt, output_key="hs_code")
legacy = SequentialChain(
    chains=[facts_chain, code_chain],
    input_variables=["description"],
    output_variables=["facts", "hs_code"],
)

# ---------- MODERN (LCEL) ----------
modern = (
    {"facts": facts_prompt | llm | StrOutputParser()}        # step 1 result stored under 'facts'
    | code_prompt | llm | StrOutputParser()                  # step 2 uses {facts}
)

async def run(description: str) -> dict[str, str]:
    try:
        old = await legacy.ainvoke({"description": description})
        new = await modern.ainvoke({"description": description})
        return {"legacy": old["hs_code"], "modern": new}
    except Exception as exc:                                  # API errors, missing keys
        return {"error": f"{type(exc).__name__}: {exc}"}

if __name__ == "__main__":
    print(asyncio.run(run("Bluetooth speaker")))   # needs OPENAI_API_KEY and langchain<1 installed
```

---

## 🟠 FastAPI Integration
Both styles are `Runnable`s, so you can call `ainvoke` from a route. Prefer LCEL in new code.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class In(BaseModel):
    description: str

@app.post("/classify")
async def classify_route(body: In) -> dict[str, str]:
    try:
        code = await modern.ainvoke({"description": body.description})   # LCEL chain above
    except Exception as exc:
        raise HTTPException(status_code=502, detail=type(exc).__name__)
    return {"hs_code": code}
```

---

## 🔗 LangChain / LangGraph Connection
Legacy chains live in the `langchain.chains` package. Most are deprecated since 0.1/0.2, and the docs give migration guides: `LLMChain` to `prompt | llm`, `RetrievalQA` to `create_retrieval_chain`, `ConversationalRetrievalChain` to `create_history_aware_retriever`, `SequentialChain` to LCEL or a **LangGraph** `StateGraph` when you need branches, loops or persistence.

```python
# LangGraph version of the two-step pipeline (state flows between nodes)
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class S(TypedDict, total=False):
    description: str
    facts: str
    hs_code: str

def n1(s: S) -> S:
    return {"facts": "audio, battery powered"}        # call an LLM here
def n2(s: S) -> S:
    return {"hs_code": "8518.22"}                      # call an LLM here

g = StateGraph(S)
g.add_node("facts", n1); g.add_node("code", n2)
g.add_edge(START, "facts"); g.add_edge("facts", "code"); g.add_edge("code", END)
print(g.compile().invoke({"description": "speaker"}))
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Starting new code with `LLMChain`.
✅ Correct: Use LCEL.

```python
# Wrong (deprecated)
chain = LLMChain(llm=llm, prompt=prompt)
out = chain.run(description="speaker")        # .run is also deprecated
# Right
chain = prompt | llm | StrOutputParser()
out = chain.invoke({"description": "speaker"})
```

❌ Mistake 2: Mismatching `output_key` and the next chain's input variable (KeyError).
✅ Correct: Names must match exactly.

❌ Mistake 3: Using `SimpleSequentialChain` with multiple inputs (it supports one input and one output only).
✅ Correct: Use `SequentialChain` or LCEL.

---

## 🧠 Tricky Interview Question
**Q**: "You inherit a codebase using `LLMChain` and `SequentialChain`. After upgrading LangChain, imports warn or fail. How do you migrate safely?"

**Answer**: Write tests that lock current behaviour (inputs and expected outputs, with a mocked or recorded LLM). Then migrate chain by chain: `LLMChain` becomes `prompt | llm | parser`; `output_key` becomes dict keys via `RunnablePassthrough.assign` or `RunnableParallel`; `.run()/.__call__` become `.invoke()`. Check that outputs are strings, not dicts with `"text"`. Add streaming and async at the same time. Pin versions in between and migrate retrieval chains using the `create_*` helpers.

---

## ⚫ Interview Questions + Answers

Q1: What was LLMChain?
A1: A legacy class that combined a prompt template and an LLM; calling it filled the prompt and returned `{"text": ...}`.

Q2: SimpleSequentialChain vs SequentialChain?
A2: Simple: one input, one output per step; output of one step becomes input to the next. Sequential: named multiple inputs/outputs.

Q3: Why were legacy chains deprecated?
A3: Opaque internals, inconsistent interfaces, hard to stream or run in parallel, limited async, awkward customisation. LCEL gives one `Runnable` interface with streaming, batch, async by default.

Q4: How do you replace a SequentialChain with LCEL?
A4: Pipe steps with `|`, and use `RunnablePassthrough.assign(new_key=...)` to carry earlier values forward.

Q5: When would you choose LangGraph over LCEL when migrating?
A5: When the flow has branches, loops, retries, human approval, shared state, or persistence. LCEL is for linear DAG-like compositions; LangGraph is for stateful, cyclic workflows.

---

## 🔷 When to Use + When Not to Use
✅ Use legacy chains when:
- Maintaining old code you cannot yet migrate
- Reading old tutorials or answering interview questions

❌ Avoid when:
- Writing any new code (use LCEL/LangGraph)
- You need streaming, batching, tracing of each step

---

## 📊 Visual Diagram
```
 LEGACY:  {description} ──► LLMChain A ──"facts"──► LLMChain B ──"hs_code"──► out
                           (class, dict in/out)    (class, dict in/out)

 LCEL:    {description} ──► prompt | llm | parser ──► prompt | llm | parser ──► out
                           (Runnable)                (Runnable)  with .stream/.batch/.ainvoke
```

---

## 💰 Cost Impact
- Cost is the same per LLM call; chains do not change token prices.
- Hidden cost: each chained step is a separate LLM call, so tokens add up (facts step ~100 in / 80 out; code step ~120 in / 20 out).
- Optimise: merge steps into one prompt when quality allows, use a small model for early steps, `max_tokens` per step, and cache repeated steps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LLMChain | Prompt + model bundle | Prompt + model का bundle |
| SequentialChain | Chains run one after another | एक के बाद एक चलने वाली chains |
| output_key | Name of a chain's result | Chain के नतीजे का नाम |
| Deprecated | Old API, avoid in new code | पुराना API, नए code में न लें |
| LCEL | Modern pipe-based composition | आधुनिक pipe वाला तरीका |

---

## ⚡ 3-Line Summary
English: Legacy chains (LLMChain, SequentialChain) bundle prompt, model and parsing with dict keys. They are deprecated and replaced by LCEL for linear flows and LangGraph for stateful flows. Know both: you must read old code and write new code.
Hindi: Legacy chains (LLMChain, SequentialChain) prompt, model और parsing को dict keys से जोड़ती हैं। ये deprecated हैं; सीधे flows के लिए LCEL और stateful flows के लिए LangGraph आया है। दोनों जानो: पुराना code पढ़ना और नया लिखना दोनों आना चाहिए।

---

## ➡️ Next Topic
**261. RetrievalQA Chain**: the legacy one-liner RAG chain, and what replaced it.
