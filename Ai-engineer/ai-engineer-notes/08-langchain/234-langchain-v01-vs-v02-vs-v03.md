---

# 234. LangChain v0.1 vs v0.2 vs v0.3
# हिंदी में: LangChain v0.1 बनाम v0.2 बनाम v0.3

---

## 🔵 Simple Definition (English)
These are three milestones of LangChain. v0.1 (Jan 2024) introduced stable packages and LCEL. v0.2 (May 2024) removed hidden dependence on `langchain-community` and moved to explicit imports. v0.3 (Sep 2024) dropped Pydantic v1 in favor of Pydantic v2 and Python 3.8 support, and made LangGraph the recommended path for agents.

## 🔵 सरल परिभाषा (Hindi)
ये LangChain के तीन पड़ाव हैं। v0.1 (Jan 2024) में stable packages और LCEL आया। v0.2 (May 2024) में `langchain-community` पर छिपी निर्भरता हटी और explicit imports आए। v0.3 (Sep 2024) में Pydantic v1 की जगह Pydantic v2 आया, Python 3.8 support हटा, और agents के लिए LangGraph recommended बना।

---

## 🔴 Problem it Solves
Old code breaks silently on upgrade: wrong imports, deprecated `LLMChain`, `AgentExecutor`, Pydantic v1/v2 clashes. Interviewers also ask "what changed between versions?" to test whether you have used it for real. Knowing the timeline lets you migrate safely and read old tutorials critically.

## 🔴 यह क्यों बना? (Hindi)
Upgrade पर पुराना code चुपचाप टूटता है: गलत imports, deprecated `LLMChain`, `AgentExecutor`, Pydantic v1/v2 टकराव। Interview में भी पूछा जाता है कि versions में क्या बदला, ताकि पता चले आपने असल में use किया है। Timeline जानने से migration सुरक्षित होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → v0.0.x : monolith, LLMChain, Agent classes, many hidden imports
Step 2 → v0.1   : split into langchain-core / -community / partners; LCEL
Step 3 → v0.2   : langchain no longer depends on langchain-community;
                  old import paths deprecated; agents guided to LangGraph
Step 4 → v0.3   : Pydantic v2 only; Python 3.9+; v0.2 deprecations removed
Step 5 → Migrate: run `langchain-cli migrate`, fix imports, swap legacy chains to LCEL
Step 6 → Test   : run golden prompts before/after, compare outputs
Step 7 → Pin    : lock versions in requirements
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → v0.0.x : monolith, LLMChain, Agent classes, छिपे imports
Step 2 → v0.1   : core / community / partner packages में बँटा; LCEL
Step 3 → v0.2   : langchain की community पर निर्भरता खत्म; पुराने imports deprecated;
                  agents के लिए LangGraph की सलाह
Step 4 → v0.3   : सिर्फ Pydantic v2; Python 3.9+; v0.2 की deprecations हटीं
Step 5 → Migrate: `langchain-cli migrate`, imports ठीक, legacy chains -> LCEL
Step 6 → Test   : migrate के पहले/बाद golden prompts की तुलना
Step 7 → Pin    : requirements में versions lock
```

---

## 🟡 Real World Example
**Tariff Classification System** started in 2023 with `LLMChain(llm=OpenAI(...))` and `AgentExecutor`. Migration plan: replace with `prompt | ChatOpenAI | parser`; move agent to `langgraph.prebuilt.create_react_agent`; change `from pydantic.v1 import BaseModel` to `from pydantic import BaseModel`. Result: fewer hidden LLM calls and full streaming support. **Amazon-style** team with 40 microservices pins one LangChain minor per release train.

## 🟡 Real Example Hindi mein
**Tariff System** 2023 में `LLMChain(llm=OpenAI(...))` और `AgentExecutor` से शुरू हुआ। Migration: `prompt | ChatOpenAI | parser` से बदला; agent को `langgraph.prebuilt.create_react_agent` में; `from pydantic.v1 import BaseModel` को `from pydantic import BaseModel` में। नतीजा: छिपे LLM calls कम और पूरी streaming support।

---

## 💻 Code Example — Basic
```python
# Same job in "old" vs "new" style. The new style runs offline with core only.
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# ---- OLD (v0.0/v0.1 era, now deprecated; shown as text, not executed) ----
OLD = '''
from langchain.chains import LLMChain
from langchain.llms import OpenAI
chain = LLMChain(llm=OpenAI(), prompt=prompt)
result = chain.run(product="earbuds")      # .run() returned str, hidden behaviour
'''

# ---- NEW (v0.2/v0.3): everything is a Runnable ----
prompt = PromptTemplate.from_template("HS code for {product}?")  # template
fake_llm = RunnableLambda(lambda p: f"(fake) {p.text}")  # swap for ChatOpenAI
chain = prompt | fake_llm  # LCEL pipe
print(chain.invoke({"product": "earbuds"}))  # .invoke instead of .run
print("old style was:", OLD.strip().splitlines()[2])  # just to show what changed
```

## 💻 Code Example — Advanced
```python
# Migration helper: scan a codebase for legacy imports and report fixes (pure Python)
import re
from pathlib import Path

LEGACY: dict[str, str] = {
    r"from langchain\.chat_models import ChatOpenAI": "from langchain_openai import ChatOpenAI",
    r"from langchain\.embeddings import OpenAIEmbeddings": "from langchain_openai import OpenAIEmbeddings",
    r"from langchain\.vectorstores import Chroma": "from langchain_chroma import Chroma",
    r"from langchain\.llms import OpenAI": "from langchain_openai import OpenAI",
    r"from langchain\.chains import LLMChain": "# replace LLMChain with: prompt | llm | parser",
    r"from langchain\.agents import AgentExecutor": "# prefer langgraph.prebuilt.create_react_agent",
    r"from pydantic\.v1 import": "from pydantic import   # v0.3 requires Pydantic v2",
    r"from langchain_core\.pydantic_v1 import": "from pydantic import   # pydantic_v1 shim removed",
}

def scan(root: str) -> list[tuple[str, int, str, str]]:
    findings: list[tuple[str, int, str, str]] = []
    for path in Path(root).rglob("*.py"):  # every python file
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue  # skip unreadable files
        for no, line in enumerate(lines, start=1):
            for pattern, fix in LEGACY.items():
                if re.search(pattern, line):
                    findings.append((str(path), no, line.strip(), fix))
    return findings

if __name__ == "__main__":
    for f, n, old, new in scan("."):
        print(f"{f}:{n}\n  - {old}\n  + {new}")
    # Official tool: pip install langchain-cli && langchain-cli migrate
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel  # v0.3: use Pydantic v2 models directly

app = FastAPI()

class Req(BaseModel):
    product: str

@app.post("/classify")
async def classify(req: Req) -> dict:
    out = await chain.ainvoke({"product": req.product})  # modern Runnable API
    return {"result": str(out)}
# FastAPI >= 0.100 uses Pydantic v2, which is why LangChain 0.3 moving to v2 removed the v1/v2 mixing pain.
```

---

## 🔗 LangChain / LangGraph Connection
From v0.2 the docs steer agents to **LangGraph** (`create_react_agent`, `StateGraph`), and memory classes (`ConversationBufferMemory`) are replaced by LangGraph checkpointers or message-history Runnables. `AgentExecutor` still exists but is legacy.

```python
# Modern agent:
# from langgraph.prebuilt import create_react_agent
# agent = create_react_agent(model, tools)
# agent.invoke({"messages": [("user", "HS code for earbuds?")]})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Following 2023 tutorials with 2026 versions
```python
# Wrong
chain = LLMChain(llm=llm, prompt=prompt); chain.run(x)
# Right
chain = prompt | llm | StrOutputParser(); chain.invoke({"x": x})
```

❌ Mistake 2: Mixing Pydantic v1 models into tools/structured output
```python
# Wrong
from pydantic.v1 import BaseModel
# Right
from pydantic import BaseModel   # v2
```

---

## 🧠 Tricky Interview Question
**Q**: "After upgrading to LangChain 0.3 your app raises validation errors in tools. Why?"

**Answer**: 0.3 uses Pydantic v2 internally. Tool schemas written with `pydantic.v1` or `langchain_core.pydantic_v1` no longer fit. Convert models to Pydantic v2 (`model_validator`, `field_validator`, `model_dump`), then re-test tool-call schemas.

---

## ⚫ Interview Questions + Answers

Q1: What did v0.1 introduce? (Easy)
A1: Package split (core, community, partners) and a stable, versioned LCEL.

Q2: What is the main v0.3 breaking change? (Easy)
A2: Move to Pydantic v2 (v1 dropped) and removal of Python 3.8 support.

Q3: How do you migrate imports automatically? (Medium)
A3: `langchain-cli migrate` rewrites common legacy paths; then run tests and fix leftovers by hand.

Q4: What replaced `ConversationBufferMemory`? (Medium)
A4: `RunnableWithMessageHistory` for simple chains, and LangGraph state + checkpointers for agents.

Q5: Plan a safe upgrade for a production RAG. (Hard)
A5: Freeze current behaviour with a golden eval set, create a branch with pinned new versions, run migration tool, replace legacy chains, compare answers and token usage via traces, canary-deploy to 5 percent traffic, keep rollback to the old lockfile.

---

## 🔷 When to Use + When Not to Use
✅ Upgrade when:
- Security/bug fixes needed, or you want LangGraph/Pydantic v2 features

❌ Delay when:
- No test coverage; add evals first

---

## 📊 Visual Diagram
```
 v0.0.x  ── monolith, LLMChain, Agent ──┐
 v0.1    ── core/community/partners, LCEL│  Jan 2024
 v0.2    ── explicit imports, agents->LangGraph │ May 2024
 v0.3    ── Pydantic v2, Py3.9+, cleanup │  Sep 2024
                     │
                     ▼
        1.x line ── stable APIs, LangGraph-first agents
```

---

## 💰 Cost Impact
Migration can lower cost: legacy `AgentExecutor` runs with verbose scratchpads and extra LLM calls; LangGraph agents with trimmed state use fewer tokens. Compare token traces before and after. Risk: new defaults may change prompt text and thus tokens, so always compare usage on the golden set.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Deprecation | Marked for removal | हटाने के लिए चिह्नित |
| LCEL | Pipe composition | Pipe से जोड़ना |
| langchain-cli | Migration tool | Migration टूल |
| Pydantic v2 | New validation lib | नई validation library |
| Breaking change | Old code fails | पुराना code टूटना |

---

## ⚡ 3-Line Summary
English: v0.1 split packages and introduced LCEL, v0.2 made imports explicit and pushed agents to LangGraph, v0.3 moved to Pydantic v2. Legacy `LLMChain` and memory classes are replaced by LCEL and LangGraph. Migrate with the CLI plus golden tests.
Hindi: v0.1 में packages बँटे और LCEL आया, v0.2 में imports explicit हुए और agents LangGraph की ओर गए, v0.3 में Pydantic v2। `LLMChain` और memory classes की जगह LCEL और LangGraph। CLI और golden tests से migrate करो।

---

## ➡️ Next Topic
**235. LCEL: LangChain Expression Language** — the pipe-based way to build chains in detail.
