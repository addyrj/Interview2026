---

# 350. Hierarchical Agents
# हिंदी में: Hierarchical Agents

---

## 🔵 Simple Definition (English)
Hierarchical agents are arranged in levels like a company: a top manager agent delegates to team-lead agents, and each team lead delegates to worker agents. Each level only sees its own children, so no single prompt has to know everything.

## 🔵 सरल परिभाषा (Hindi)
Hierarchical agents company की तरह levels में होते हैं: top manager agent team-lead agents को काम देता है, और हर team lead अपने workers को। हर level सिर्फ अपने children को देखता है, इसलिए किसी एक prompt को सब कुछ नहीं जानना पड़ता।

---

## 🔴 Problem it Solves
- A flat supervisor with 20+ workers gets confused and routes badly.
- Its prompt becomes huge (every worker description) and expensive.
- Teams (legal, data, writing) want to own and change their own agents independently.

## 🔴 यह क्यों बना? (Hindi)
- 20+ workers वाला flat supervisor confuse होकर गलत route करता है।
- उसका prompt बहुत बड़ा और महँगा हो जाता है।
- Teams (legal, data, writing) अपने agents खुद own और change करना चाहती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Group workers into teams by skill (research team, legal team)
Step 2 → Each team gets a team supervisor with only its workers
Step 3 → A top supervisor knows only the teams (not individual workers)
Step 4 → Top supervisor sends the task to a team
Step 5 → Team supervisor routes within its team and collects results
Step 6 → Team returns ONE summarised result upward
Step 7 → Top supervisor merges team results into the final answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workers को skill से teams में बाँटो (research team, legal team)
Step 2 → हर team का अपना team supervisor, सिर्फ अपने workers के साथ
Step 3 → Top supervisor सिर्फ teams को जानता है, individual workers को नहीं
Step 4 → Top supervisor task किसी team को भेजता है
Step 5 → Team supervisor team के अंदर route करके results जमा करता है
Step 6 → Team ऊपर सिर्फ एक summarised result लौटाती है
Step 7 → Top supervisor team results से final answer बनाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Top manager has two teams. The *Classification team* (attribute extractor, HS searcher, rulings searcher, classifier) and the *Compliance team* (sanctions checker, restricted-goods checker, duty calculator). A request for "import 500 drones" goes to both teams; each returns a short summary and the manager combines them.

**Amazon**: Seller-support manager with Listings team and Payments team. **Zomato**: City-ops manager with Delivery team and Restaurant team.

## 🟡 Real Example Hindi mein
**Tariff System**: Top manager के पास दो teams हैं। *Classification team* (attribute extractor, HS searcher, rulings searcher, classifier) और *Compliance team* (sanctions checker, restricted-goods checker, duty calculator)। "500 drones import करो" दोनों teams को जाता है; हर team छोटा summary देती है और manager उन्हें जोड़ता है।

---

## 💻 Code Example — Basic
```python
# Two-level hierarchy with rule-based supervisors (offline)
from typing import Callable  # type hints

Worker = Callable[[str], str]  # worker takes text, returns text


def extractor(t: str) -> str:  # classification worker
    return f"attrs({t})"


def classifier(t: str) -> str:  # classification worker
    return "code 8806.21"


def sanctions(t: str) -> str:  # compliance worker
    return "no sanctions"


def duty(t: str) -> str:  # compliance worker
    return "duty 5%"


class Team:
    def __init__(self, name: str, workers: list[Worker]) -> None:
        self.name = name  # team name
        self.workers = workers  # members

    def run(self, task: str) -> str:  # team supervisor logic
        outs = [w(task) for w in self.workers]  # call each worker
        return f"{self.name}: " + "; ".join(outs)  # ONE summary upward


teams = [Team("classification", [extractor, classifier]), Team("compliance", [sanctions, duty])]
task = "import 500 drones"  # user task
summary = [t.run(task) for t in teams]  # top manager delegates
print("\n".join(summary))  # merged answer
```

## 💻 Code Example — Advanced
```python
# Async hierarchy: teams run in parallel, failures isolated, depth/step limits enforced
import asyncio  # async runtime
from dataclasses import dataclass  # containers
from typing import Awaitable, Callable  # types

AsyncWorker = Callable[[str], Awaitable[str]]  # async worker type


@dataclass
class TeamResult:
    team: str  # team name
    summary: str  # short result
    ok: bool  # success flag


class AsyncTeam:
    def __init__(self, name: str, workers: dict[str, AsyncWorker], timeout: float = 3.0) -> None:
        self.name, self.workers, self.timeout = name, workers, timeout  # store config

    async def run(self, task: str) -> TeamResult:
        async def safe(n: str, w: AsyncWorker) -> str:  # isolate each worker
            try:
                return await asyncio.wait_for(w(task), self.timeout)  # bounded time
            except Exception as exc:  # worker failure must not kill the team
                return f"{n} failed: {type(exc).__name__}"
        outs = await asyncio.gather(*(safe(n, w) for n, w in self.workers.items()))
        ok = not any("failed" in o for o in outs)  # team health
        return TeamResult(self.name, " | ".join(outs)[:200], ok)  # truncate summary


async def w_attrs(t: str) -> str:
    await asyncio.sleep(0.01)
    return "attrs ok"


async def w_sanctions(t: str) -> str:
    await asyncio.sleep(0.01)
    raise RuntimeError("db down")  # simulate failure


async def manager(task: str) -> list[TeamResult]:
    teams = [AsyncTeam("classification", {"attrs": w_attrs}),
             AsyncTeam("compliance", {"sanctions": w_sanctions})]
    return await asyncio.gather(*(t.run(task) for t in teams))  # teams in parallel


if __name__ == "__main__":
    for r in asyncio.run(manager("import 500 drones")):
        print(r)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app


class TeamOut(BaseModel):
    team: str  # team name
    summary: str  # summary text
    ok: bool  # success


class Out(BaseModel):
    answer: str  # merged answer
    teams: list[TeamOut]  # per-team details


@app.post("/import-check", response_model=Out)
async def import_check(item: dict) -> Out:
    teams = [TeamOut(team="classification", summary="8806.21", ok=True),
             TeamOut(team="compliance", summary="no sanctions, duty 5%", ok=True)]  # mocked
    status = "approved" if all(t.ok for t in teams) else "needs review"  # simple merge rule
    return Out(answer=status, teams=teams)
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph supports hierarchical teams by using a compiled sub-graph as a node of the parent graph.

```python
from typing import TypedDict  # state type
from langgraph.graph import StateGraph, START, END  # graph


class S(TypedDict, total=False):
    task: str  # input
    summary: str  # result


def build_team(name: str):  # builds one team graph
    def work(s: S) -> dict:
        return {"summary": f"{name} done for {s['task']}"}
    g = StateGraph(S)
    g.add_node("work", work)
    g.add_edge(START, "work")
    g.add_edge("work", END)
    return g.compile()  # compiled graph is a Runnable


top = StateGraph(S)  # parent graph
top.add_node("classification", build_team("classification"))  # subgraph as node
top.add_edge(START, "classification")
top.add_edge("classification", END)
print(top.compile().invoke({"task": "drones"}))
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Too many levels.
✅ Correct: Two levels are usually enough.

```python
# Wrong: manager -> director -> lead -> worker (4 LLM hops per task)
# Right: manager -> team lead -> worker
```

❌ Mistake 2: Teams return their full transcripts upward.
✅ Correct: Return a short summary.

```python
# Wrong
result = team.full_history  # thousands of tokens
# Right
result = team.summary[:500]  # compact
```

---

## 🧠 Tricky Interview Question
**Q**: "Adding a middle manager layer made answers worse. Why?"

**Answer**: Each layer compresses information (summaries lose details) and adds a chance of misrouting; this is like a game of telephone. Fix: pass structured fields, not prose; let workers write detailed artifacts to shared storage and pass only references; limit depth; test accuracy per level; flatten the hierarchy if a team has fewer than about 5 workers.

---

## ⚫ Interview Questions + Answers

Q1: What are hierarchical agents?
A1: Agents in levels: a top manager, team supervisors and workers, each delegating downward.

Q2: Why not one flat supervisor?
A2: With many workers its prompt grows and routing accuracy and cost get worse.

Q3: How do subgraphs help in LangGraph?
A3: A compiled graph can be used as a node, so each team is built and tested independently and then embedded in the parent graph.

Q4: What goes wrong with deep hierarchies?
A4: Latency adds up per level, details are lost in summaries, and debugging gets harder.

Q5: How do you design the interface between levels?
A5: A typed contract: task in (goal, constraints), result out (status, summary, artifact_ids, confidence). Large data goes into a store and only ids move between levels. Add timeouts and fallbacks per team so one team failure gives a partial answer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- 15+ workers or several domains
- Different teams own different agents

❌ Avoid when:
- 3-6 workers (flat supervisor is simpler)
- Strict latency limits

---

## 📊 Visual Diagram
```
                 ┌──────────────┐
                 │ TOP MANAGER  │
                 └───┬──────┬───┘
          ┌──────────┘      └──────────┐
   ┌──────▼───────┐            ┌───────▼──────┐
   │Classification│            │  Compliance  │
   │  supervisor  │            │  supervisor  │
   └──┬────┬────┬─┘            └──┬────┬────┬─┘
      W1   W2   W3                W4   W5   W6
```

---

## 💰 Cost Impact
Every level adds LLM calls, but each prompt is smaller because it lists only its children. Net cost can go down for large systems (a 25-worker flat prompt is paid on every routing call). Optimise with small models for routing, short summaries upward and parallel teams.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hierarchy | Levels of agents | agents के levels |
| Team supervisor | Manages one team | एक team का manager |
| Subgraph | Graph used as node | node के रूप में graph |
| Delegation | Handing work down | काम नीचे देना |
| Summary upward | Short result to parent | parent को छोटा result |
| Depth limit | Max levels | अधिकतम levels |

---

## ⚡ 3-Line Summary
English: Hierarchical agents organise workers into teams under supervisors, and a top manager over the teams. This scales routing and ownership for big systems. Keep depth small and pass compact, typed summaries.
Hindi: Hierarchical agents workers को teams में और teams को top manager के नीचे रखते हैं। इससे बड़े systems में routing और ownership scale होती है। Depth कम रखो और compact, typed summaries भेजो।

---

## ➡️ Next Topic
**351. Peer-to-Peer Agents** — agents with no boss that talk directly to each other.
