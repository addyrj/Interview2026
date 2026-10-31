---

# 357. Agent State Sharing
# हिंदी में: Agents के बीच State Sharing

---

## 🔵 Simple Definition (English)
Agent state sharing means several agents read from and write to one common, structured **state** object (like a shared whiteboard) instead of passing long chat text to each other. Each agent writes only its own fields, and **reducers** define how concurrent updates are merged.

## 🔵 सरल परिभाषा (Hindi)
Agent state sharing का मतलब है कि कई agents एक साझा, structured **state** object (साझा whiteboard) से पढ़ते और उसमें लिखते हैं, लंबा chat text एक-दूसरे को भेजने की जगह। हर agent सिर्फ अपने fields लिखता है और **reducers** तय करते हैं कि एक साथ आए updates कैसे merge हों।

---

## 🔴 Problem it Solves
If agents talk by pasting full conversations, tokens explode, details get lost in summaries, and two agents can overwrite each other. Without a schema nobody knows where the "HS code" lives. A typed shared state gives one source of truth, small prompts (each agent reads only the fields it needs), and safe merging.

## 🔴 यह क्यों बना? (Hindi)
अगर agents पूरी बातचीत paste करके बात करें तो tokens फट जाते हैं, summary में details खो जाती हैं और दो agents एक-दूसरे का लिखा मिटा सकते हैं। Schema न हो तो पता नहीं "HS code" कहाँ रखा है। Typed shared state एक सच्चा स्रोत, छोटे prompts (हर agent सिर्फ ज़रूरी fields पढ़ता है) और सुरक्षित merging देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a schema: fields, types, and a reducer per field
Step 2 → Initial state is created from the user request
Step 3 → Agent A runs, reads its input fields, returns a PARTIAL update
Step 4 → Framework merges update using reducers (overwrite / append / custom)
Step 5 → Agent B runs on the merged state, writes its own fields
Step 6 → Parallel agents' updates are merged together, no overwrite loss
Step 7 → State is checkpointed so runs can resume and be audited
Step 8 → Final state is the response
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Schema तय करो: fields, types, और हर field का reducer
Step 2 → User request से शुरुआती state बनती है
Step 3 → Agent A अपने input fields पढ़ता है, PARTIAL update लौटाता है
Step 4 → Framework reducers से update merge करता है (overwrite / append / custom)
Step 5 → Agent B merged state पर चलता है, अपने fields लिखता है
Step 6 → Parallel agents के updates बिना loss के merge होते हैं
Step 7 → State checkpoint होती है ताकि run resume और audit हो सके
Step 8 → अंतिम state ही response है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Three agents share one state: `Classifier` writes `hs_code`; `DutyAgent` reads `hs_code` and writes `duty_rate`; `ComplianceAgent` reads `hs_code` and appends to `warnings` (for example "anti-dumping duty applies"). `DutyAgent` and `ComplianceAgent` run in parallel; `warnings` uses an append reducer so none are lost.

**Zomato-style**: Order state has `cart`, `address`, `eta`, `offers`. Pricing, delivery and offers agents each update their own field.

## 🟡 Real Example Hindi mein
**Tariff System**: तीन agents एक state शेयर करते हैं: `Classifier` `hs_code` लिखता है; `DutyAgent` `hs_code` पढ़कर `duty_rate` लिखता है; `ComplianceAgent` `hs_code` पढ़कर `warnings` में जोड़ता है (जैसे "anti-dumping duty लागू")। `DutyAgent` और `ComplianceAgent` parallel चलते हैं; `warnings` में append reducer है इसलिए कोई entry खोती नहीं।

**Zomato-style**: Order state में `cart`, `address`, `eta`, `offers` हैं। Pricing, delivery और offers agents अपना-अपना field अपडेट करते हैं।

---

## 💻 Code Example — Basic
```python
# Shared state with per-field merge rules (reducers) in plain Python
from typing import Any, Callable  # type hints

# Reducers: how to combine old and new values for a field
def overwrite(old: Any, new: Any) -> Any: return new          # last write wins
def append(old: list[str], new: list[str]) -> list[str]: return old + new  # keep both

REDUCERS: dict[str, Callable[[Any, Any], Any]] = {
    "hs_code": overwrite,      # single value
    "duty_rate": overwrite,    # single value
    "warnings": append,        # many agents can add warnings
}

def merge(state: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    new_state = dict(state)  # never mutate in place
    for key, value in update.items():  # apply each changed field
        reducer = REDUCERS.get(key)  # find the rule
        if reducer is None:
            raise KeyError(f"unknown field {key}")  # schema protection
        new_state[key] = reducer(state.get(key), value)  # merge
    return new_state

# Agents return partial updates only
def classifier(s: dict[str, Any]) -> dict[str, Any]: return {"hs_code": "8518.30"}
def duty_agent(s: dict[str, Any]) -> dict[str, Any]: return {"duty_rate": 0.20 if s["hs_code"].startswith("85") else 0.1}
def compliance(s: dict[str, Any]) -> dict[str, Any]: return {"warnings": ["BIS certificate needed"]}

if __name__ == "__main__":
    state: dict[str, Any] = {"hs_code": "", "duty_rate": 0.0, "warnings": []}  # initial
    state = merge(state, classifier(state))  # step 1
    u1, u2 = duty_agent(state), compliance(state)  # these two could run in parallel
    state = merge(merge(state, u1), u2)  # merged without loss
    print(state)  # {'hs_code': '8518.30', 'duty_rate': 0.2, 'warnings': ['BIS certificate needed']}
```

## 💻 Code Example — Advanced
```python
# Async shared state with a lock, versioning and field ownership
import asyncio  # async runtime
from typing import Any  # type hints

class SharedState:
    """Thread/async-safe shared state with ownership rules and version history."""

    def __init__(self, owners: dict[str, str]) -> None:
        self._data: dict[str, Any] = {k: None for k in owners}  # fields
        self._owners = owners                                   # field -> agent name
        self._lock = asyncio.Lock()                             # prevents races
        self.version = 0                                        # increments per write
        self.history: list[tuple[int, str, str]] = []           # (version, agent, field)

    async def write(self, agent: str, field: str, value: Any) -> None:
        async with self._lock:  # one writer at a time
            if self._owners.get(field) != agent:  # ownership check
                raise PermissionError(f"{agent} cannot write {field}")
            self._data[field] = value  # apply
            self.version += 1  # bump version
            self.history.append((self.version, agent, field))  # audit

    async def read(self, *fields: str) -> dict[str, Any]:
        async with self._lock:  # consistent snapshot
            return {f: self._data[f] for f in fields}  # only what the agent needs

async def duty_agent(st: SharedState) -> None:
    snap = await st.read("hs_code")  # read just one field (saves tokens)
    await st.write("duty", "duty_rate", 0.20 if snap["hs_code"] else 0.0)

async def main() -> None:
    st = SharedState({"hs_code": "classifier", "duty_rate": "duty"})  # owners
    await st.write("classifier", "hs_code", "8518.30")  # classifier writes
    await duty_agent(st)  # duty agent reads and writes
    try:
        await st.write("duty", "hs_code", "0000")  # violates ownership
    except PermissionError as exc:
        print("blocked:", exc)  # expected
    print(await st.read("hs_code", "duty_rate"), st.version)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Keep state per `run_id` in Redis or a database, and expose it so the UI can show live progress. Never use a module-level dict across workers.

```python
import json  # serialise state
from fastapi import FastAPI, HTTPException  # framework
import redis.asyncio as redis  # async redis client

app = FastAPI()
r = redis.Redis()  # one client per process

@app.post("/runs/{run_id}/state")
async def patch_state(run_id: str, update: dict) -> dict:
    raw = await r.get(f"run:{run_id}")  # load current state
    state = json.loads(raw) if raw else {}  # empty on first write
    allowed = {"hs_code", "duty_rate", "warnings"}  # schema guard
    if not set(update) <= allowed:
        raise HTTPException(422, "unknown fields")
    for k, v in update.items():
        state[k] = (state.get(k, []) + v) if k == "warnings" else v  # same reducers as graph
    await r.set(f"run:{run_id}", json.dumps(state), ex=3600)  # expire in 1 hour
    return state

@app.get("/runs/{run_id}/state")
async def get_state(run_id: str) -> dict:
    raw = await r.get(f"run:{run_id}")
    if raw is None:
        raise HTTPException(404, "run not found")
    return json.loads(raw)
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph is built around shared state. Each node returns a partial dict; `Annotated[..., reducer]` defines the merge.

```python
from typing import Annotated, TypedDict  # state typing
import operator  # list add reducer
from langgraph.graph import StateGraph, START, END  # graph

class TariffState(TypedDict):
    description: str                                  # input, no reducer: overwrite
    hs_code: str                                      # overwrite
    duty_rate: float                                  # overwrite
    warnings: Annotated[list[str], operator.add]      # append from many nodes

def classifier(s: TariffState) -> dict: return {"hs_code": "8518.30"}
def duty(s: TariffState) -> dict: return {"duty_rate": 0.20}
def compliance(s: TariffState) -> dict: return {"warnings": ["BIS certificate needed"]}

g = StateGraph(TariffState)
g.add_node("classifier", classifier)
g.add_node("duty", duty)
g.add_node("compliance", compliance)
g.add_edge(START, "classifier")
g.add_edge("classifier", "duty")        # fan-out: duty and compliance run in parallel
g.add_edge("classifier", "compliance")
g.add_edge("duty", END)
g.add_edge("compliance", END)
print(g.compile().invoke({"description": "headphones", "warnings": []}))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Parallel nodes writing the same field without a reducer
✅ Correct: add a reducer (append, max, merge) or give each node its own field.

```python
# Wrong: two nodes write "warnings" with plain list -> InvalidUpdateError in LangGraph
class S(TypedDict): warnings: list[str]
# Right
class S(TypedDict): warnings: Annotated[list[str], operator.add]
```

❌ Mistake 2: Putting everything (full chat history, documents) in state and giving it all to every agent
✅ Correct: each agent reads only its fields.

```python
# Wrong
prompt = f"Here is the state: {state}"
# Right
prompt = f"HS code: {state['hs_code']}"
```

---

## 🧠 Tricky Interview Question
**Q**: "Two agents run in parallel and both update `confidence`. Final value is random. What is wrong and how do you fix it?"

**Answer**: A last-write-wins field with parallel writers is a race. Fix by design: separate fields (`classifier_conf`, `validator_conf`) and compute the final value in a later join node, or use an explicit reducer (for example `min`), so the result is deterministic. Also add tests that run parallel branches repeatedly.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is shared state?
A1: One typed object all agents read and write, used instead of passing long messages.

Q2: [Easy] What is a reducer?
A2: A function that tells how to combine the old value and an update, for example overwrite or list append.

Q3: [Medium] Why return partial updates from nodes?
A3: It avoids overwriting fields the node does not own, lets the framework merge parallel results, and keeps nodes simple.

Q4: [Medium] Where should state live in production?
A4: In a checkpointer backed by Postgres, Redis or SQLite so it survives restarts and supports resume. Not in process memory.

Q5: [Hard] How do you keep shared state from growing without bound?
A5: Store large artifacts (documents) outside and keep only ids in state, trim or summarise message lists, use TTLs, and give each agent a filtered view so prompts stay small.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several agents depend on each other's outputs
- You need parallel branches merged safely
- You need audit, resume and debugging

❌ Avoid when:
- A single agent with local variables is enough
- Agents are fully independent services (use messages or events)

---

## 📊 Visual Diagram
```
           +-----------------------------+
           |        SHARED STATE         |
           | hs_code | duty_rate | warns |
           +-----------------------------+
             ^  |         ^  |      ^ |
        write|  |read     |  |      | |
        +----+--v-+  +----+--v-+  +-+-v------+
        |Classifier|  |  Duty   |  |Compliance|
        +----------+  +---------+  +----------+
        (hs_code)     (duty_rate)   (warnings: append)
```

---

## 💰 Cost Impact
- Passing full transcripts between 3 agents can cost 3-5x more input tokens than passing 3 small fields.
- Example: transcript of 3,000 tokens x 3 agents = 9,000 tokens; fields only = about 150 tokens x 3 = 450 tokens.
- Optimise: per-agent field views, ids instead of documents, summarise long histories, cache stable fields in the prompt prefix.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shared state | Common object for all agents | सभी agents की साझा state |
| Reducer | Merge rule for a field | Field merge करने का नियम |
| Partial update | Only changed fields returned | सिर्फ बदले fields लौटाना |
| Checkpoint | Saved snapshot of state | State का सेव किया snapshot |
| Field ownership | One agent owns a field | एक field का एक मालिक agent |

---

## ⚡ 3-Line Summary
English: Agents share one typed state instead of long messages. Reducers decide how updates merge, so parallel agents do not overwrite each other. Give each agent only the fields it needs.
Hindi: Agents लंबे messages की जगह एक typed state शेयर करते हैं। Reducers तय करते हैं कि updates कैसे merge हों, इसलिए parallel agents एक-दूसरे को overwrite नहीं करते। हर agent को सिर्फ ज़रूरी fields दो।

---

## ➡️ Next Topic
**358. Agent Context Management** — deciding what each agent sees, so context stays small and relevant.
