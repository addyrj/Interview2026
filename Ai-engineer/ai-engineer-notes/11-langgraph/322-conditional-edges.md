---

# 322. Conditional Edges
# हिंदी में: Conditional Edges (शर्त वाले रास्ते)

---

## 🔵 Simple Definition (English)
A conditional edge is a connection in a LangGraph graph where the next node is chosen at runtime by a Python function. The function reads the current state and returns the name of the next node (or `END`). It is the `if/else` of a graph. Without it, a graph can only run in a fixed straight line.

## 🔵 सरल परिभाषा (Hindi)
Conditional edge LangGraph में ऐसा connection है जिसमें अगला node runtime पर एक Python function चुनता है। यह function current state पढ़ता है और अगले node का नाम (या `END`) return करता है। यह graph का `if/else` है। इसके बिना graph सिर्फ एक fixed सीधी line में चल सकता है।

---

## 🔴 Problem it Solves
Real workflows branch. A tariff query about a phone needs the electronics checker; a query about shirts needs the textile checker; a low-confidence answer needs a human. Plain edges (`add_edge`) always go to the same node, so you would have to hide branching inside one giant node. That makes the flow invisible, untestable and impossible to draw. Loops (retry until good) were also impossible.

## 🔴 यह क्यों बना? (Hindi)
Real workflows में branching होती है। Phone वाली tariff query को electronics checker चाहिए, shirt वाली को textile checker, और low-confidence answer को human चाहिए। साधारण edge (`add_edge`) हमेशा एक ही node पर जाता है, इसलिए branching एक बड़े node के अंदर छुपानी पड़ती थी। इससे flow दिखता नहीं, test नहीं होता। Retry loops भी संभव नहीं थे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Node A finishes and writes its result into the shared state
Step 2 → LangGraph calls your routing function with the latest state
Step 3 → Routing function returns a key (e.g. "electronics") - no side effects
Step 4 → LangGraph maps the key to a node via the path_map (or uses the name directly)
Step 5 → The chosen node runs next; unchosen branches never run (no tokens spent)
Step 6 → If the function returns END the graph stops
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Node A खत्म होता है और result shared state में लिखता है
Step 2 → LangGraph आपके routing function को latest state के साथ call करता है
Step 3 → Routing function एक key return करता है (जैसे "electronics") - कोई side effect नहीं
Step 4 → LangGraph key को path_map से node में बदलता है
Step 5 → चुना हुआ node चलता है; बाकी branches नहीं चलतीं (tokens नहीं लगते)
Step 6 → Function END return करे तो graph रुक जाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Step 1 classifies the product category. A conditional edge then routes: `electronics` goes to the Chapter 85 node, `textile` goes to the Chapter 61/62 node, `unknown` goes to a human-review node. If the confidence of the answer is below 0.7 the edge loops back to a "refine" node (max 2 times). **Zomato AI**: "order status" goes to the order-lookup node, "refund" goes to the refund node, "chit-chat" goes straight to END with a cheap model.

## 🟡 Real Example Hindi mein
**Tariff System**: पहले product category तय होती है। फिर conditional edge route करता है: `electronics` को Chapter 85 node, `textile` को Chapter 61/62 node, `unknown` को human-review node। Confidence 0.7 से कम हो तो edge वापस "refine" node पर loop करता है (max 2 बार)। **Zomato AI**: "order status" order-lookup node पर जाता है, "refund" refund node पर, और "chit-chat" सस्ते model के साथ सीधे END पर।

---

## 💻 Code Example — Basic
```python
# Basic conditional edge - runs offline (pip install langgraph)
from typing import Literal, TypedDict  # typing helpers for state and router return type

from langgraph.graph import END, START, StateGraph  # graph building blocks


class TariffState(TypedDict):  # shared state schema
    product: str  # user product text
    category: str  # filled by classify node
    hs_code: str  # final answer


def classify(state: TariffState) -> dict[str, str]:  # node 1: decide category
    text = state["product"].lower()  # normalise the text
    category = "electronics" if "phone" in text else "textile"  # fake classifier, no LLM
    return {"category": category}  # partial state update


def electronics(state: TariffState) -> dict[str, str]:  # node 2a
    return {"hs_code": "8517.13"}  # smartphones heading


def textile(state: TariffState) -> dict[str, str]:  # node 2b
    return {"hs_code": "6109.10"}  # cotton t-shirts heading


def route(state: TariffState) -> Literal["electronics", "textile"]:  # the routing function
    return "electronics" if state["category"] == "electronics" else "textile"  # pure function of state


builder = StateGraph(TariffState)  # create builder with the state schema
builder.add_node("classify", classify)  # register node
builder.add_node("electronics", electronics)  # register node
builder.add_node("textile", textile)  # register node
builder.add_edge(START, "classify")  # entry edge
builder.add_conditional_edges("classify", route)  # branch after classify (Literal hint draws the graph)
builder.add_edge("electronics", END)  # finish
builder.add_edge("textile", END)  # finish
graph = builder.compile()  # compile into a runnable

print(graph.invoke({"product": "Apple phone"}))  # {'product': ..., 'category': 'electronics', 'hs_code': '8517.13'}
print(graph.invoke({"product": "Cotton shirt"}))  # goes to textile branch
```

## 💻 Code Example — Advanced
```python
# Production style: path_map, retry loop with a cap, safe fallback, async
import asyncio  # async runner
import logging  # structured logs
from typing import Literal, TypedDict  # typing

from langgraph.graph import END, START, StateGraph  # graph API

log = logging.getLogger("tariff.graph")  # module logger


class State(TypedDict):  # state schema
    product: str  # input
    category: str  # classifier output
    confidence: float  # 0..1
    attempts: int  # loop counter (guards infinite loops)
    hs_code: str  # result


async def classify(state: State) -> dict[str, object]:  # async node (real code awaits an LLM here)
    await asyncio.sleep(0)  # placeholder for network call
    conf = 0.55 + 0.2 * state["attempts"]  # confidence grows after each refine (fake)
    return {"category": "electronics", "confidence": conf, "attempts": state["attempts"] + 1}


async def finalize(state: State) -> dict[str, str]:  # happy path node
    return {"hs_code": "8517.13"}


async def human_review(state: State) -> dict[str, str]:  # fallback node
    return {"hs_code": "PENDING_REVIEW"}


def decide(state: State) -> Literal["done", "retry", "escalate"]:  # router with 3 outcomes
    try:  # routers must never crash the graph
        if state["confidence"] >= 0.7:  # good enough
            return "done"
        if state["attempts"] < 3:  # still allowed to retry
            return "retry"
        return "escalate"  # out of attempts
    except KeyError:  # missing key = bug upstream, fail safe
        log.exception("router saw incomplete state")
        return "escalate"


builder = StateGraph(State)  # builder
builder.add_node("classify", classify)  # node
builder.add_node("finalize", finalize)  # node
builder.add_node("human_review", human_review)  # node
builder.add_edge(START, "classify")  # entry
builder.add_conditional_edges(  # branching with explicit path_map
    "classify",
    decide,
    {"done": "finalize", "retry": "classify", "escalate": "human_review"},  # key -> node name
)
builder.add_edge("finalize", END)  # end
builder.add_edge("human_review", END)  # end
graph = builder.compile()  # compile


async def main() -> None:  # entry
    out = await graph.ainvoke({"product": "phone", "category": "", "confidence": 0.0, "attempts": 0, "hs_code": ""})
    print(out)  # confidence reaches 0.75 on 2nd try -> hs_code 8517.13


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Expose the graph as one endpoint. The conditional branching stays inside the graph; the API only passes input and returns state. Add `recursion_limit` so a buggy loop returns an error instead of burning tokens.

```python
from fastapi import FastAPI, HTTPException  # web framework
from langgraph.errors import GraphRecursionError  # raised when loop exceeds the limit
from pydantic import BaseModel  # request validation (v2)

app = FastAPI()  # app instance


class ClassifyIn(BaseModel):  # request body
    product: str  # product text


@app.post("/classify")  # route
async def classify_route(body: ClassifyIn) -> dict[str, object]:  # typed handler
    try:
        result = await graph.ainvoke(  # graph from the Advanced example
            {"product": body.product, "category": "", "confidence": 0.0, "attempts": 0, "hs_code": ""},
            config={"recursion_limit": 10},  # hard stop for runaway loops
        )
    except GraphRecursionError:  # loop never converged
        raise HTTPException(status_code=508, detail="Routing loop did not converge")
    return {"hs_code": result["hs_code"], "confidence": result["confidence"]}  # small response
```

---

## 🔗 LangChain / LangGraph Connection
A very common router is an LLM with structured output. The LLM returns a Pydantic object and the routing function just reads one field. This is cheaper and more reliable than asking the LLM to "write the node name".

```python
from typing import Literal  # allowed values
from pydantic import BaseModel  # schema
from langchain_openai import ChatOpenAI  # pip install langchain-openai


class Route(BaseModel):  # LLM must fill this
    category: Literal["electronics", "textile", "other"]


router_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Route)  # structured output


def llm_route(state: dict) -> str:  # routing function used in add_conditional_edges
    return router_llm.invoke(f"Category of: {state['product']}").category  # one cheap call
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Doing work or mutating state inside the routing function
✅ Correct: Routers only read state and return a key. Put work in nodes.

```python
# Wrong - router mutates state; the change is lost and logic is hidden
def route(state):
    state["category"] = "electronics"  # lost! routers cannot update state
    return "electronics"

# Right - node writes, router reads
def classify(state):
    return {"category": "electronics"}  # state update belongs in a node
def route(state):
    return state["category"]  # pure read
```

❌ Mistake 2: Loop without a counter or recursion limit
✅ Correct: Keep an `attempts` field and escalate when it is exhausted.

```python
# Wrong - may loop forever if confidence never rises
def decide(state):
    return "done" if state["confidence"] > 0.9 else "retry"

# Right - bounded
def decide(state):
    if state["confidence"] > 0.9:
        return "done"
    return "retry" if state["attempts"] < 3 else "escalate"
```

---

## 🧠 Tricky Interview Question

**Q**: "Your router returns `'electronic'` (typo) but the node is named `'electronics'`. What happens, and how do you stop it reaching production?"

**Answer**: Without a `path_map`, LangGraph tries to run a node called `electronic`, which does not exist, and raises an error at runtime (only for that branch, so tests that skip it will pass!). Prevention: (1) annotate the router with `Literal[...]` so the compiled graph knows all possible targets and type checkers flag typos, (2) pass an explicit `path_map` dict, (3) write one test per branch, (4) return an enum value, not free text, especially when an LLM produces the key.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `add_edge` and `add_conditional_edges`? (Easy)
A1: `add_edge(a, b)` always goes from a to b. `add_conditional_edges(a, fn)` calls `fn(state)` after a finishes and goes to whichever node `fn` returns.

Q2: What can a routing function return? (Easy)
A2: A node name, `END`, a key of the `path_map`, or a list of node names/`Send` objects for parallel fan-out. It should be a pure function of state.

Q3: How do you build a retry loop in LangGraph? (Medium)
A3: Add a conditional edge from the evaluating node back to the earlier node, keep an `attempts` counter in state, and route to an escalate/END node when attempts run out. Also set `recursion_limit` in config as a safety net.

Q4: Router in a node (`Command`) vs conditional edge - when to choose which? (Medium)
A4: A conditional edge keeps routing separate from work and shows up clearly in the graph drawing. `Command(goto=..., update=...)` lets one node update state AND choose the next node in one step, which is better when the decision needs data computed inside that same node (handoffs, multi-agent). Use edges for simple branching, `Command` for dynamic or agent-style routing.

Q5: Design routing for a tariff graph with 30 chapters without 30 hard-coded branches. (Hard)
A5: Use a two-level design: a cheap classifier returns a chapter group (`Literal` of ~6 groups), then a sub-graph per group does fine-grained work. Alternatively the router returns `Send("chapter_node", {...})` for dynamic fan-out, or a single generic "chapter" node receives the chapter id from state and loads the right prompt/tools from a registry. This keeps the graph small, testable, and cheap (only one branch's tokens are spent).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The next step depends on content (category, confidence, error flag)
- You need retry/refine loops with a cap
- You want human escalation on uncertainty

❌ Avoid when:
- The flow is always A then B (use `add_edge`)
- The branching logic is one tiny `if` inside a single node and nobody needs to see it
- You want the LLM to freely invent node names (use structured output instead)

---

## 📊 Visual Diagram
```
START
  │
  ▼
[classify] ──► route(state)
                 │
     ┌───────────┼─────────────┐
     ▼ "done"    ▼ "retry"     ▼ "escalate"
[finalize]     (back to       [human_review]
     │          classify)          │
     ▼                             ▼
    END                           END
```

---

## 💰 Cost Impact
- Tokens are spent only on the branch that actually runs. A 3-branch graph where each branch costs ~800 tokens spends ~800, not 2400.
- A router LLM call costs ~150 input + ~10 output tokens with `gpt-4o-mini` (about $0.00003). Use rule-based routers (keywords, regex, metadata) when possible: zero tokens.
- Retry loops multiply cost (attempts x tokens). Cap attempts at 2-3.
- Optimise: cheap model for routing, strong model only in the chosen branch; cache routing result per product string.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Conditional edge | Edge whose target is chosen at runtime | Runtime पर चुना जाने वाला रास्ता |
| Routing function | Function returning next node key | Router function |
| path_map | Dict mapping router keys to node names | Key से node का नक्शा |
| END | Special terminal node | Graph का अंत |
| Recursion limit | Max steps before error | Loop की अधिकतम सीमा |
| Literal | Type listing allowed strings | Allowed values का type |

---

## ⚡ 3-Line Summary
English: A conditional edge lets a function pick the next node from the current state. It enables branching, retry loops and human escalation, and only the chosen branch costs tokens. Keep routers pure, typed with `Literal`, and loops capped.
Hindi: Conditional edge में एक function state देखकर अगला node चुनता है। इससे branching, retry loop और human escalation मिलते हैं, और सिर्फ चुनी हुई branch के tokens लगते हैं। Router pure रखो, `Literal` से type करो और loop की limit लगाओ।

---

## ➡️ Next Topic
**323. Entry Point + END** — how a graph starts (`START`, `set_entry_point`) and ends (`END`, `set_finish_point`), including multiple end nodes.
