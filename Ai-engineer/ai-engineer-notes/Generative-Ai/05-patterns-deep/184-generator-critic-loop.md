---

# 184. Generator-Critic Loop
# हिंदी में: Generator-Critic Loop (बनाओ, परखो, सुधारो)
# Framework: All (LangGraph shown in code)
# Already Known: No

> Verified offline with a fake generator and critic (no API key). Python 3.13, langgraph 1.2.22, langchain-core 1.8.1, fastapi 0.163.1, pydantic 2.14.3. Real LLM calls: not run, needs an LLM API key. Token figures are approximate formulas only.

---

## 🔵 Simple Definition (2-3 lines)
A Generator-Critic loop connects a generator (writes a draft) and a critic (reviews it). If the critic rejects the draft, its issues are fed back to the generator for a revision. The loop repeats until the critic approves or a maximum number of rounds is reached.

## 🔵 सरल परिभाषा (Hindi)
Generator-Critic loop में generator draft लिखता है और critic उसे परखता है। Critic reject करे तो उसकी बताई समस्याएँ generator को वापस जाती हैं और वह draft सुधारता है। यह चक्र तब तक चलता है जब तक critic approve न कर दे या अधिकतम rounds पूरे न हो जाएँ।

---

## 🔴 Problem it Solves
A critic alone (note 183) only says "no". Someone still has to fix the draft. Without an automatic loop a human must retry by hand. But an unbounded loop is dangerous: the generator and critic can ping-pong forever, burning tokens, or the generator may "game" the critic. The loop needs a hard round limit and a best-effort exit.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ critic (नोट 183) "नहीं" कहता है, सुधारता कोई नहीं। बिना automatic loop के इंसान को हाथ से दोबारा चलाना पड़ता है। पर बिना सीमा का loop ख़तरनाक है: generator और critic अनंत काल तक ping-pong करके tokens जला सकते हैं, या generator critic को "चकमा" दे सकता है। इसलिए hard round limit और best-effort exit ज़रूरी है।

---

## 🟢 How it Works

```
Step 1 → round = 0, feedback = none
Step 2 → Generator(task, feedback) -> draft
Step 3 → Critic(draft) -> {approved, issues}
Step 4 → approved           -> return draft (status "approved")
Step 5 → rejected, round < MAX -> feedback = issues, round += 1, go to Step 2
Step 6 → rejected, round >= MAX -> return best draft (status "max_rounds") + issues
Step 7 → Log every round: draft, verdict, tokens (for debugging and cost)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → round = 0, feedback = कुछ नहीं
Step 2 → Generator(task, feedback) -> draft
Step 3 → Critic(draft) -> {approved, issues}
Step 4 → approved हो        -> draft लौटाओ (status "approved")
Step 5 → reject और round < MAX -> feedback = issues, round += 1, Step 2 पर जाओ
Step 6 → reject और round >= MAX -> सबसे अच्छा draft + issues लौटाओ (status "max_rounds")
Step 7 → हर round log करो: draft, verdict, tokens (debug और cost के लिए)
```

---

## 🟡 Real World Example
**Tariff Agent**: Round 1 the generator returns an HS code without a source. The critic says "missing source". Round 2 the generator adds "WCO HS 2022, heading 8518". The critic approves. If it were still rejected after 3 rounds, the API returns the best draft marked `needs_human_review`. Other examples: Code Agent (write code, run tests as critic, fix), Research Agent (draft report, fact-check, revise).

## 🟡 Real Example Hindi mein
**Tariff Agent**: Round 1 में generator बिना source का HS code देता है। Critic कहता है "source गायब"। Round 2 में generator "WCO HS 2022, heading 8518" जोड़ देता है और critic approve करता है। 3 rounds बाद भी reject हो तो API सबसे अच्छा draft `needs_human_review` के साथ लौटाती है। अन्य उदाहरण: Code Agent (code लिखो, tests को critic बनाओ, सुधारो), Research Agent (draft, fact-check, revise)।

---

## 💻 Code Example — Basic
```python
# Basic generator-critic loop in plain Python with fakes. Runs offline.
from dataclasses import dataclass                 # result container

MAX_ROUNDS = 3                                    # hard stop so the loop cannot run forever


def generator(task: str, feedback: list[str]) -> str:   # fake LLM writer
    draft = f"HS 8518.22 for {task}"              # base draft
    if "missing source" in feedback:              # revise using the critic's feedback
        draft += " | source: WCO HS 2022"
    return draft


def critic(draft: str) -> list[str]:              # returns a list of issues ([] = approved)
    return [] if "source:" in draft else ["missing source"]


@dataclass
class Result:                                     # what the caller gets back
    draft: str
    status: str                                   # "approved" or "max_rounds"
    rounds: int


def run_loop(task: str) -> Result:
    feedback: list[str] = []                      # no feedback in round 1
    draft = ""                                    # keep the latest draft
    for rnd in range(1, MAX_ROUNDS + 1):          # bounded loop
        draft = generator(task, feedback)         # step: generate / revise
        feedback = critic(draft)                  # step: critique
        print(f"round {rnd}: {draft!r} issues={feedback}")  # observability
        if not feedback:                          # critic approved
            return Result(draft, "approved", rnd)
    return Result(draft, "max_rounds", MAX_ROUNDS)  # best effort exit


if __name__ == "__main__":
    print(run_loop("bluetooth speaker"))          # approved in round 2
```

## 💻 Code Example — Advanced
```python
# Advanced: LangGraph state machine (generate -> critique -> conditional edge),
# async nodes, FastAPI endpoint, error handling, approximate token counting.
import operator                                   # list-append reducer
from typing import Annotated, TypedDict           # typed graph state
from fastapi import FastAPI, HTTPException        # web framework
from fastapi.testclient import TestClient         # offline test client
from langgraph.graph import StateGraph, START, END  # LangGraph primitives
from pydantic import BaseModel                    # request model

MAX_ROUNDS = 3                                    # loop cap


class State(TypedDict):                           # shared graph state
    task: str
    draft: str
    issues: list[str]
    round: int
    tokens: int                                   # approximate running token count
    trace: Annotated[list[str], operator.add]     # reducer: nodes APPEND to this list


def est(text: str) -> int:                        # rough token estimate (~4 chars/token)
    return max(1, len(text) // 4)


async def generate(s: State) -> dict:             # async node: fake LLM writer
    draft = f"HS 8518.22 for {s['task']}"
    if "missing source" in s["issues"]:           # use critic feedback
        draft += " | source: WCO HS 2022"
    return {"draft": draft, "round": s["round"] + 1,
            "tokens": s["tokens"] + est(draft),
            "trace": [f"gen r{s['round'] + 1}"]}


async def critique(s: State) -> dict:             # async node: fake LLM critic
    issues = [] if "source:" in s["draft"] else ["missing source"]
    return {"issues": issues, "tokens": s["tokens"] + est(s["draft"]),
            "trace": [f"critic issues={issues}"]}


def route(s: State) -> str:                       # conditional edge decides loop or stop
    if not s["issues"]:                           # approved
        return "done"
    if s["round"] >= MAX_ROUNDS:                  # budget exhausted
        return "done"
    return "revise"                               # go back to the generator


g = StateGraph(State)                             # build the graph
g.add_node("generate", generate)
g.add_node("critique", critique)
g.add_edge(START, "generate")
g.add_edge("generate", "critique")
g.add_conditional_edges("critique", route, {"revise": "generate", "done": END})
graph = g.compile()                               # runnable graph

app = FastAPI()


class Req(BaseModel):
    task: str


@app.post("/classify")
async def classify(req: Req) -> dict:
    try:
        out = await graph.ainvoke(                # async run; recursion_limit is a 2nd safety net
            {"task": req.task, "draft": "", "issues": [], "round": 0, "tokens": 0, "trace": []},
            config={"recursion_limit": 25})
    except Exception as exc:                      # never leak raw errors
        raise HTTPException(500, f"loop failed: {type(exc).__name__}")
    status = "approved" if not out["issues"] else "needs_human_review"
    return {"status": status, "draft": out["draft"], "rounds": out["round"],
            "approx_tokens": out["tokens"], "trace": out["trace"]}


if __name__ == "__main__":
    print(TestClient(app).post("/classify", json={"task": "speaker"}).json())
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Loop expression | Cycle in graph via conditional edge | Re-run tasks in your code / task guardrail style retries | Plain `while` loop around `Runner` calls | Team chat until termination condition |
| Stop rule | Router function + `recursion_limit` | Your counter | Your counter or `max_turns` on a run | Max-turn / text-mention termination |
| Feedback passing | State field | Task context | Message appended to input | Chat message |
| Visibility | Best (per-node trace, checkpoints) | Logs | Tracing | Message log |
| Best for | Explicit, auditable loops | Role-based drafts | Simple code-driven loops | Conversational review |

---

## ⚠️ Common Mistakes
❌ Mistake 1: No max rounds ("loop until approved").
✅ Correct: Always cap rounds and define the exit status for the failure case.

❌ Mistake 2: Passing only "try again" to the generator.
✅ Correct: Pass the critic's specific issues so each round makes progress.

❌ Mistake 3: Discarding earlier drafts, so a late bad revision replaces a good one.
✅ Correct: Keep the best-scoring draft and return it on max rounds.

❌ Mistake 4: Ignoring that the history grows each round (context blow-up).
✅ Correct: Send only the latest draft and current issues, not the full chat.

---

## 🧠 Tricky Interview Question
Your loop averages 2.8 rounds and costs triple what you budgeted. Quality barely improved after round 1. What do you do?

Answer: Measure per-round gain: if round 2 and 3 rarely flip a rejection into approval, the loop is wasting money. Options: lower MAX_ROUNDS to 2, make the generator better in round 1 (few-shot, better prompt), make critic feedback more actionable, stop early when the score stops improving (plateau detection) or when the same issue repeats twice, and use a cheaper model for revisions. Also check whether the critic is too strict about cosmetic issues; split issues into blocking and advisory so only blocking ones trigger another round. Track "approved at round k" as a histogram to choose the cap with data.

---

## ⚫ Interview Questions + Answers

Q1: (Easy) What are the two roles in the loop?
A1: Generator creates or revises the draft; critic reviews it and returns issues.

Q2: (Medium) How do you prevent infinite loops?
A2: A hard round cap, a framework recursion limit as backup, plateau detection, and a defined fallback result (best draft plus `needs_human_review`).

Q3: (Hard) What is "reward hacking" in this loop?
A3: The generator learns to satisfy the critic's wording instead of the real goal (for example, inventing a source string so "source:" appears). Mitigate with checks that verify the source really exists, a different critic model, and periodic human audits.

Q4: (Hard) How do you make this loop resumable after a crash?
A4: Persist state each round (LangGraph checkpointer, or your own DB row keyed by request id) including round number and feedback. On restart, resume from the last completed node instead of regenerating.

Q5: (System Design) Design this loop for 1,000 concurrent requests with a 10 s p95 latency goal.
A5: Async workers, a concurrency semaphore per LLM provider, MAX_ROUNDS=2, per-call timeouts (about 3 s), small critic model, early exit on approval, queue for rejected cases that go to human review, and metrics: rounds histogram, approval rate, tokens per request, p95 latency.

---

## 💰 Cost Impact
- Token formula (approximate): `total ≈ rounds × (generator_tokens + critic_tokens)`, plus prompt growth if you carry history. Best case rounds=1, worst case MAX_ROUNDS.
- Expected cost = `E[rounds] × per-round cost`; measure E[rounds] from logs (do not guess).
- Tips: cap rounds at 2-3, send only latest draft and issues, cheaper critic model, cache by input hash, stop on plateau, make round 1 strong so most requests exit early.
- Pricing numbers: approximate, from public pricing at time of writing, verify.

---

## 🔷 When to Use
✅ Use when:
- Quality can be checked and improved by feedback (code with tests, structured data, reports)
- One-shot accuracy is not enough and latency allows 2-3 rounds

❌ Avoid when:
- Strict real-time latency (chat autocomplete)
- Critic cannot give actionable feedback
- Errors need external ground truth that neither agent has

---

## 📊 Visual Diagram
```
            +-------------------------+
 task -->   |       Generator         | <---- issues (feedback)
            +-------------------------+              ^
                        | draft                      |
                        v                            |
            +-------------------------+   rejected & round < MAX
            |         Critic          | --------------+
            +-------------------------+
                  | approved  OR  round >= MAX
                  v
        return draft + status ("approved" | "needs_human_review")
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generator | Produces/revises draft | बनाने वाला |
| Feedback | Critic's issues sent back | प्रतिक्रिया |
| Round | One generate+critique cycle | चरण |
| Plateau | No more improvement | ठहराव |
| Recursion limit | Framework-level loop cap | पुनरावृत्ति सीमा |
| Reward hacking | Gaming the critic | critic को चकमा देना |

---

## ⚡ 3-Line Summary
English: Generator writes, critic judges, and issues flow back until approval or a round cap.
Always cap rounds, pass specific feedback, and keep the best draft.
Cost grows roughly with rounds, so measure the average and tune.

Hindi: Generator लिखता है, critic परखता है, और approval या round cap तक issues वापस जाते हैं।
हमेशा rounds सीमित रखो, ठोस feedback दो और सबसे अच्छा draft बचाकर रखो।
Cost लगभग rounds के साथ बढ़ती है, इसलिए औसत नापो और tune करो।

---

## ➡️ Next Topic
185. Ensemble Pattern: instead of improving one answer in a loop, ask several agents in parallel and combine their answers (voting or merging).

---
