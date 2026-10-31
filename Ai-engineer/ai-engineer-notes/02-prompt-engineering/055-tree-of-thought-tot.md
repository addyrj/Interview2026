---

# 055. Tree of Thought (ToT)
# हिंदी में: Tree of Thought (ToT)

---

## 🔵 Simple Definition (English)
Tree of Thought lets the model explore several possible reasoning paths (branches), score or evaluate them, drop weak ones, and continue from the best ones. Unlike CoT, which follows one line of thought, ToT does search with backtracking: generate, evaluate, select, repeat.

## 🔵 सरल परिभाषा (Hindi)
Tree of Thought में model कई संभावित reasoning रास्ते (branches) खोजता है, उन्हें score/evaluate करता है, कमज़ोर रास्ते छोड़ता है और सबसे अच्छे से आगे बढ़ता है। CoT एक ही सोच की लाइन पर चलता है, ToT में search और backtracking होती है: generate, evaluate, select, repeat।

---

## 🔴 Problem it Solves
- CoT commits to its first idea; if step 2 is wrong, everything after is wrong.
- Planning, puzzles and ambiguous decisions need exploring alternatives.
- A single sample may miss the best option.

## 🔴 यह क्यों बना? (Hindi)
- CoT पहले विचार पर अड़ जाता है; step 2 गलत हो तो आगे सब गलत।
- Planning, puzzles और ambiguous decisions में विकल्प खोजने पड़ते हैं।
- एक ही sample सबसे अच्छा विकल्प चूक सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Break the problem into steps (levels of the tree)
Step 2 → At each level, generate N candidate thoughts (branches)
Step 3 → Evaluate each candidate (LLM scores it, or a rule/tool checks it)
Step 4 → Keep the top K candidates (beam), prune the rest
Step 5 → Expand each kept candidate into the next level
Step 6 → Repeat until a solution level or a budget limit (max calls/tokens)
Step 7 → Return the best-scoring leaf path
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Problem को steps (tree के levels) में तोड़ो
Step 2 → हर level पर N candidate thoughts (branches) generate करो
Step 3 → हर candidate को evaluate करो (LLM score दे, या rule/tool जाँचे)
Step 4 → Top K candidates रखो (beam), बाकी prune करो
Step 5 → रखे गए candidates को अगले level में expand करो
Step 6 → Solution level या budget limit (max calls/tokens) तक दोहराओ
Step 7 → सबसे ज़्यादा score वाला path लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: A hard product: "Kit containing a phone holder, charger and cable sold together." Candidate headings: 8504 (chargers), 8517 (phone parts), 8544 (cables), or "goods put up in sets" under General Rule 3. ToT generates 3 hypotheses, evaluates each against the legal notes (retrieved text), prunes two, and expands the best into sub-heading options. It costs 8-10 calls, so we use it only when simple classification confidence is under 0.6.

**Zomato-style**: Planning a multi-restaurant order that meets budget and delivery time: explore combinations, score them, keep the best.

## 🟡 Real Example Hindi mein
**Tariff System**: कठिन product: "Phone holder, charger और cable एक साथ बिकने वाला kit"। संभावित headings: 8504 (chargers), 8517 (phone parts), 8544 (cables) या General Rule 3 के तहत "sets"। ToT 3 hypotheses बनाता है, हर एक को legal notes (retrieved text) से evaluate करता है, दो prune करता है और सबसे अच्छे को sub-heading options में expand करता है। इसमें 8-10 calls लगती हैं, इसलिए सिर्फ़ तब इस्तेमाल करते हैं जब simple classification confidence 0.6 से कम हो।

**Zomato-style**: कई restaurants का order plan करना जो budget और delivery time में फिट हो: combinations खोजो, score दो, सबसे अच्छा रखो।

---

## 💻 Code Example — Basic
```python
# Basic: beam search over "thoughts" with a mock generator and scorer (runs offline)

CANDIDATES = {  # fake knowledge: candidate headings and how well they fit the notes
    "8504": 0.55,  # chargers
    "8517": 0.70,  # phone apparatus parts
    "8544": 0.30,  # cables
    "set-GRI3": 0.85,  # goods put up in sets
}

def generate(state: str, n: int = 3) -> list[str]:
    # Mock generator: return n candidate thoughts (a real one calls an LLM)
    return list(CANDIDATES)[:n + 1]

def evaluate(thought: str) -> float:
    return CANDIDATES.get(thought, 0.0)  # mock scorer (a real one asks an LLM or checks rules)

def tree_of_thought(problem: str, beam: int = 2) -> list[tuple[str, float]]:
    thoughts = generate(problem)  # level 1 candidates
    scored = [(t, evaluate(t)) for t in thoughts]  # score each
    scored.sort(key=lambda x: x[1], reverse=True)  # best first
    return scored[:beam]  # keep top K (prune the rest)

best = tree_of_thought("Kit: phone holder + charger + cable")
print("Kept branches:", best)  # [('set-GRI3', 0.85), ('8517', 0.7)]
print("Chosen:", best[0][0])  # best branch
```

## 💻 Code Example — Advanced
```python
# Production-style: async ToT with parallel generation/evaluation and a hard call budget
import asyncio  # parallel calls
import json  # parse JSON answers
from dataclasses import dataclass, field  # tree node
from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI(timeout=20.0)  # shared client

@dataclass
class Node:
    path: list[str]  # thoughts so far
    score: float = 0.0  # evaluator score 0..1

@dataclass
class Budget:
    calls_left: int = 20  # hard cap to control cost
    used: int = 0

async def llm_json(prompt: str, budget: Budget) -> dict:
    if budget.calls_left <= 0:  # budget guard
        raise RuntimeError("ToT budget exhausted")
    budget.calls_left -= 1
    budget.used += 1
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0.7, max_tokens=300,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}])
        return json.loads(resp.choices[0].message.content or "{}")
    except (APIError, json.JSONDecodeError):
        return {}  # treat failures as empty results

async def propose(problem: str, node: Node, n: int, budget: Budget) -> list[Node]:
    out = await llm_json(
        f'Problem: {problem}\nSo far: {node.path}\n'
        f'Propose {n} different next HS heading hypotheses. '
        'Return JSON {"thoughts": [string]}', budget)
    return [Node(node.path + [t]) for t in out.get("thoughts", [])[:n]]

async def judge(problem: str, node: Node, budget: Budget) -> Node:
    out = await llm_json(
        f'Problem: {problem}\nHypothesis path: {node.path}\n'
        'Score 0 to 1 how well it matches HS rules. Return JSON {"score": number}', budget)
    node.score = float(out.get("score", 0.0))  # default 0 if parsing failed
    return node

async def tree_of_thought(problem: str, depth: int = 2, n: int = 3, beam: int = 2) -> Node:
    budget = Budget()
    frontier = [Node([])]  # start from the root
    for _ in range(depth):
        proposals = await asyncio.gather(*(propose(problem, nd, n, budget) for nd in frontier))
        children = [c for group in proposals for c in group]  # flatten
        if not children:
            break
        judged = await asyncio.gather(*(judge(problem, c, budget) for c in children))
        frontier = sorted(judged, key=lambda x: x.score, reverse=True)[:beam]  # prune
    return frontier[0] if frontier else Node([])

# best = asyncio.run(tree_of_thought("Kit: phone holder + charger + cable"))
```

---

## 🟠 FastAPI Integration
Because ToT is slow and costly, expose it as an opt-in "deep" mode, with a timeout and call budget.

```python
import asyncio  # timeout
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app

class Q(BaseModel):
    product: str  # product text
    confidence: float  # confidence from the fast classifier

@app.post("/classify-deep")
async def classify_deep(q: Q) -> dict:
    if q.confidence >= 0.6:  # fast path is enough
        return {"mode": "fast", "message": "ToT not needed"}
    try:
        node = await asyncio.wait_for(tree_of_thought(q.product), timeout=45)  # limit time
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Deep analysis timed out; manual review")
    except RuntimeError as exc:  # budget exhausted
        raise HTTPException(status_code=429, detail=str(exc))
    return {"mode": "tot", "path": node.path, "score": node.score}
```

---

## 🔗 LangChain / LangGraph Connection
ToT is naturally a graph: a "propose" node, an "evaluate" node, a "prune" node and a loop edge with a depth counter. LangGraph supports loops with conditional edges and a recursion limit. LangChain `RunnableParallel` / `abatch` can score branches in parallel. (Libraries like `langgraph` examples include "tree search" patterns.)

```python
from typing import TypedDict  # state type
from langgraph.graph import StateGraph, END  # graph builder

class State(TypedDict):
    problem: str  # input
    frontier: list[dict]  # current branches
    depth: int  # loop counter

def propose_node(s: State) -> dict:  # generate branches (LLM call in real code)
    return {"frontier": s["frontier"], "depth": s["depth"] + 1}

def prune_node(s: State) -> dict:  # score and keep top-K (LLM/rules in real code)
    return {"frontier": s["frontier"][:2]}

g = StateGraph(State)  # build graph
g.add_node("propose", propose_node)
g.add_node("prune", prune_node)
g.set_entry_point("propose")
g.add_edge("propose", "prune")
g.add_conditional_edges("prune", lambda s: END if s["depth"] >= 2 else "propose")  # loop
app_graph = g.compile()  # runnable graph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using ToT for every request
✅ Correct: Use cheap methods first and ToT only for hard cases.

```python
# Wrong: always run tree_of_thought()   # 10x cost
# Right: if confidence < 0.6: tree_of_thought() else: fast path
```

❌ Mistake 2: No budget or depth limit
✅ Correct: Cap calls, depth and time.

```python
# Wrong: while not solved: expand()   # can loop and burn money
# Right: Budget(calls_left=20), depth=2, wait_for(timeout=45)
```

---

## 🧠 Tricky Interview Question
**Q**: "ToT with an LLM as evaluator gives confident scores, but results are not better than CoT. Why?"

**Answer**: The evaluator is also an LLM and may be uncalibrated: it often gives high scores to fluent but wrong thoughts. If scoring is noisy, pruning removes good branches. Improve by using verifiable evaluators (rules, retrieval against legal notes, unit tests, tools), comparing branches pairwise instead of absolute scoring, sampling the evaluation several times, or using self-consistency. If the task is not search-like, ToT is wasted cost.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How is ToT different from CoT?
A1: CoT follows a single chain; ToT explores multiple branches, evaluates them and can backtrack.

Q2: [Easy] Name the main components of ToT.
A2: Thought generator, state evaluator, search strategy (BFS/DFS/beam), and a stopping rule or budget.

Q3: [Medium] When is ToT worth it?
A3: Tasks with several plausible paths and checkable intermediate results: planning, puzzles, code generation with tests, complex classification. Not for simple QA.

Q4: [Medium] How do you control cost?
A4: Limit depth, branching factor and beam size; use cheap models for proposing; set a call budget and timeouts; trigger only on low-confidence cases.

Q5: [Hard] How would you implement ToT as a production workflow?
A5: Use a graph runtime (LangGraph): nodes for propose, evaluate, prune and finalize; state includes frontier and budget; persistent checkpoints for long runs; parallel branch evaluation; verifiers using tools/rules; traces for audit; metrics for cost per solved case, and an offline eval showing ToT beats CoT enough to justify the cost.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Search-like problems with verifiable steps
- High-value decisions where accuracy beats cost

❌ Avoid when:
- Simple tasks or real-time chat
- No reliable way to evaluate branches

---

## 📊 Visual Diagram
```
                 Problem
               /    |     \
          H1(0.55) H2(0.70) H3(0.30)      <- generate 3 thoughts
             x        |        x           <- prune low scores (beam=1..2)
                    /   \
              H2a(0.8)  H2b(0.6)          <- expand best
                 |
              FINAL path (best score)
```

---

## 💰 Cost Impact
- ToT cost is roughly branches x depth x (generation + evaluation) calls. With n=3, depth=2, beam=2: about 3 + 3x2 + judging 9 = ~15-20 calls, i.e. 10-20x a single call.
- Example (illustrative): 1,000 tokens per call x 18 calls = 18,000 tokens per hard item.
- Optimise: run only on low-confidence cases (maybe 5% of traffic), small model for proposals, parallel calls (reduces latency, not tokens), strict budget, and cache evaluations.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Thought | One reasoning step/candidate | एक reasoning कदम/विकल्प |
| Branch | Alternative path | वैकल्पिक रास्ता |
| Beam search | Keep top K candidates | Top K विकल्प रखना |
| Pruning | Dropping weak branches | कमज़ोर branches हटाना |
| Evaluator | Scores thoughts | Thoughts को score देने वाला |
| Backtracking | Return to an earlier choice | पिछले choice पर लौटना |

---

## ⚡ 3-Line Summary
English: ToT explores multiple reasoning branches, scores them and keeps the best. It can beat CoT on search-like tasks but costs 10-20x more. Use verifiable evaluators and strict budgets.
Hindi: ToT कई reasoning branches खोजता है, score देता है और सबसे अच्छी रखता है। Search जैसे tasks में CoT से बेहतर हो सकता है पर 10-20x महँगा है। Verifiable evaluators और सख्त budget रखो।

---

## ➡️ Next Topic
**056. Self-Consistency** — a cheaper way to improve reasoning: sample several answers and vote.
