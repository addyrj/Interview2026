---

# 356. Critic + Generator Pattern
# हिंदी में: Critic + Generator Pattern

---

## 🔵 Simple Definition (English)
A **Generator** agent produces a draft. A **Critic** agent reviews it against a checklist and returns feedback or a score. The generator revises. The loop stops when the critic approves or the round limit is hit. It is also called Reflection or Generate-and-Review.

## 🔵 सरल परिभाषा (Hindi)
**Generator** agent draft बनाता है। **Critic** agent उसे checklist के हिसाब से जाँचकर feedback या score देता है। Generator draft सुधारता है। जब critic मंज़ूर कर दे या rounds की limit आ जाए तो loop रुकता है। इसे Reflection या Generate-and-Review भी कहते हैं।

---

## 🔴 Problem it Solves
A single LLM call gives a first draft with no self-check: wrong citations, missing fields, policy violations. Asking the same model "is this right?" inside the same prompt is weak. A separate critic prompt with strict criteria (and sometimes a different model) catches errors cheaply before they reach the user.

## 🔴 यह क्यों बना? (Hindi)
एक LLM call पहला draft देती है, खुद की जाँच नहीं करती: गलत citations, छूटे fields, policy उल्लंघन। उसी prompt में उसी model से "क्या यह सही है?" पूछना कमज़ोर है। सख़्त criteria वाला अलग critic prompt (कभी अलग model) user तक पहुँचने से पहले गलतियाँ सस्ते में पकड़ लेता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Generator gets the task and writes draft v1
Step 2 → Critic receives draft + checklist (rubric)
Step 3 → Critic returns JSON: {approved, score, issues[]}
Step 4 → approved? -> return draft
Step 5 → not approved -> send issues back to Generator
Step 6 → Generator revises draft (v2) using the issues
Step 7 → Repeat until approved or max_rounds reached
Step 8 → If still failing -> return best draft + flag for human
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Generator को task मिलता है, draft v1 लिखता है
Step 2 → Critic को draft + checklist (rubric) मिलती है
Step 3 → Critic JSON देता है: {approved, score, issues[]}
Step 4 → approved? -> draft लौटाओ
Step 5 → approved नहीं -> issues वापस Generator को
Step 6 → Generator issues के आधार पर draft सुधारता है (v2)
Step 7 → approved होने या max_rounds तक दोहराओ
Step 8 → फिर भी fail -> best draft + human flag
```

---

## 🟡 Real World Example
**Tariff Classification System**: Generator writes a classification explanation for a customs filing: HS code, reasoning, legal note citations. Critic checks: Is the code 8 digits? Does the reasoning cite a real chapter note? Does it contradict product facts (for example "wireless" but chapter for wired)? Is the duty rate present? Round 1 fails for "missing citation", round 2 passes, and only then the filing is sent.

**Amazon-style**: Generator writes a product description; critic checks for banned claims ("cures", "best in the world") and missing specs.

## 🟡 Real Example Hindi mein
**Tariff System**: Generator customs filing के लिए classification explanation लिखता है: HS code, reasoning, legal note citations। Critic जाँचता है: क्या code 8 digit है? क्या reasoning असली chapter note cite करती है? क्या यह product facts से टकराती है (जैसे "wireless" पर wired वाला chapter)? क्या duty rate है? Round 1 "citation missing" पर fail, round 2 pass, तभी filing भेजी जाती है।

**Amazon-style**: Generator product description लिखता है; critic प्रतिबंधित दावे ("cures", "दुनिया में सबसे अच्छा") और छूटे specs जाँचता है।

---

## 💻 Code Example — Basic
```python
# Generator + Critic loop with mock LLMs (runs offline)
from typing import TypedDict  # typed critic output

class Review(TypedDict):
    approved: bool       # did the draft pass
    issues: list[str]    # what to fix

def generator(task: str, issues: list[str]) -> str:
    # Mock generator: adds a citation only after being told it is missing
    draft = f"HS 8518.30 for {task}."  # basic draft
    if "missing citation" in issues:
        draft += " Cited: Chapter 85 Note 2."  # fix applied
    return draft

def critic(draft: str) -> Review:
    # Mock critic: rubric = must contain a citation
    if "Cited:" not in draft:
        return {"approved": False, "issues": ["missing citation"]}  # reject
    return {"approved": True, "issues": []}  # accept

def run(task: str, max_rounds: int = 3) -> tuple[str, int, bool]:
    issues: list[str] = []  # feedback from critic
    draft = ""
    for round_no in range(1, max_rounds + 1):  # bounded loop
        draft = generator(task, issues)  # write or revise
        review = critic(draft)  # evaluate
        if review["approved"]:  # success
            return draft, round_no, True
        issues = review["issues"]  # feed back
    return draft, max_rounds, False  # give best effort, flagged

if __name__ == "__main__":
    print(run("wireless headphones"))  # ('HS 8518.30 ... Cited: ...', 2, True)
```

## 💻 Code Example — Advanced
```python
# Async Generator/Critic with score threshold, best-draft tracking and token cost
import asyncio  # async runtime
from dataclasses import dataclass  # result container

@dataclass
class Outcome:
    draft: str          # best draft so far
    score: float        # best score
    rounds: int         # rounds used
    approved: bool      # passed threshold
    tokens: int         # token estimate

async def gen_llm(task: str, feedback: str) -> str:
    await asyncio.sleep(0)  # fake latency
    return f"Draft for {task}" + (f" | fixed: {feedback}" if feedback else "")

async def critic_llm(draft: str) -> tuple[float, str]:
    await asyncio.sleep(0)  # fake latency
    if "fixed" in draft:
        return 0.92, ""  # good after one fix
    return 0.60, "add legal citation and duty rate"  # first draft weak

async def refine(task: str, threshold: float = 0.85, max_rounds: int = 3) -> Outcome:
    best = Outcome("", -1.0, 0, False, 0)  # track the best draft
    feedback = ""
    try:
        for r in range(1, max_rounds + 1):
            draft = await gen_llm(task, feedback)  # generate
            score, feedback = await critic_llm(draft)  # critique
            best.tokens += 500 + 250  # generator + critic tokens
            best.rounds = r
            if score > best.score:  # keep best, not last
                best.draft, best.score = draft, score
            if score >= threshold:  # good enough
                best.approved = True
                break
    except Exception as exc:  # never crash the caller
        best.draft = f"error: {exc}"
    return best

if __name__ == "__main__":
    print(asyncio.run(refine("tariff filing")))
```

---

## 🟠 FastAPI Integration
Return the final draft with critic metadata (rounds, score, approved) so clients know when to show a "needs review" badge.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()

class DraftIn(BaseModel):
    task: str                 # what to write
    max_rounds: int = 3       # loop cap

class DraftOut(BaseModel):
    draft: str                # final text
    score: float              # critic score
    rounds: int               # iterations used
    approved: bool            # passed or not
    tokens: int               # estimated tokens

@app.post("/generate", response_model=DraftOut)
async def generate(body: DraftIn) -> DraftOut:
    out = await refine(body.task, max_rounds=min(body.max_rounds, 5))  # clamp user input
    return DraftOut(**out.__dict__)  # dataclass -> response model
```

---

## 🔗 LangChain / LangGraph Connection
```python
from typing import TypedDict  # state
from langgraph.graph import StateGraph, START, END  # graph
from langchain_core.prompts import ChatPromptTemplate  # prompts
from langchain_openai import ChatOpenAI  # llm
from pydantic import BaseModel  # structured critic output

class Critique(BaseModel):
    approved: bool
    feedback: str

class RState(TypedDict):
    task: str
    draft: str
    feedback: str
    approved: bool
    rounds: int

gen = ChatPromptTemplate.from_template("Task: {task}\nFeedback: {feedback}\nWrite the best answer.") | ChatOpenAI(model="gpt-4o-mini")
critic = ChatPromptTemplate.from_template("Rubric: cite law, give duty.\nDraft: {draft}\nReview strictly.") | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Critique)

def gen_node(s: RState) -> dict:
    out = gen.invoke({"task": s["task"], "feedback": s.get("feedback", "")})
    return {"draft": out.content, "rounds": s.get("rounds", 0) + 1}

def critic_node(s: RState) -> dict:
    c = critic.invoke({"draft": s["draft"]})
    return {"approved": c.approved, "feedback": c.feedback}

def route(s: RState) -> str:
    return "done" if s["approved"] or s["rounds"] >= 3 else "revise"

g = StateGraph(RState)
g.add_node("generate", gen_node)
g.add_node("critic", critic_node)
g.add_edge(START, "generate")
g.add_edge("generate", "critic")
g.add_conditional_edges("critic", route, {"done": END, "revise": "generate"})
graph = g.compile()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Vague critic ("is this good?")
✅ Correct: give a concrete rubric and structured output.

```python
# Wrong
critic_prompt = "Is this good?"
# Right
critic_prompt = "Check: 8-digit code, legal citation, duty rate. Return JSON {approved, issues[]}."
```

❌ Mistake 2: Unlimited rounds, or returning the last draft instead of the best
✅ Correct: cap rounds and keep the best-scoring draft.

```python
# Wrong
while not approved: draft = revise(draft)
# Right
for r in range(MAX): ...; best = max(best, draft, key=score)
```

---

## 🧠 Tricky Interview Question
**Q**: "The critic always approves. Quality did not improve. Why?"

**Answer**: Same model and similar prompt create self-preference bias: the critic likes its own style. Fixes: use a different (or stronger) model as critic, give a strict rubric with required evidence, ask for issues first and decision last, include deterministic checks (regex, schema, database lookups) that do not use an LLM, test the critic on known-bad drafts and measure its recall of errors.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does the critic return?
A1: A verdict (approved or not), a score and specific issues to fix, ideally as structured JSON.

Q2: [Easy] Why a separate critic instead of asking the generator to double-check?
A2: A fresh prompt with a strict rubric (and maybe another model) is less biased and easier to evaluate.

Q3: [Medium] How do you stop endless revisions?
A3: Max rounds, score threshold, and stop if the score does not improve. Return the best draft and flag it.

Q4: [Medium] Can the critic be non-LLM?
A4: Yes. Schema validation, regex, tariff-table lookups and unit tests are cheaper and more reliable. Combine them with an LLM critic for style and reasoning.

Q5: [Hard] How do you measure whether the pattern is worth its cost?
A5: Compare with and without critic on a labelled set: error rate, human edits per output, latency and cost. If the gain in accuracy per extra dollar is small, reduce to one revision or use deterministic checks only.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Output has clear quality rules (compliance, code, legal text)
- Errors are costly and can be described in a rubric

❌ Avoid when:
- Simple chat answers
- Real-time latency limits (each round adds 2 calls)
- No way to define "good", the critic will just rubber-stamp

---

## 📊 Visual Diagram
```
 Task -> [Generator] -> draft -> [Critic]
              ^                      |
              |   issues             | approved?
              +----------------------+--- yes --> Final output
              (max 3 rounds)         \-- no, rounds exhausted --> best draft + human flag
```

---

## 💰 Cost Impact
- Each round costs generator tokens plus critic tokens (about 750 per round in our example).
- Three rounds can triple the cost versus one call.
- Optimise: cheap critic model, send only the draft and a short rubric (not the whole context), deterministic checks first, 1-2 rounds max, stop early when the score is already high, cache approved outputs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Generator | Produces drafts | Draft बनाने वाला |
| Critic | Reviews against a rubric | Rubric से जाँचने वाला |
| Rubric | Checklist of criteria | जाँच की सूची |
| Reflection | Self-improvement loop | खुद सुधारने का loop |
| Self-preference bias | Model likes its own output | Model को अपना ही output पसंद आना |

---

## ⚡ 3-Line Summary
English: A generator drafts, a critic checks with a rubric, and the loop repeats until approved. Use strict rubrics, deterministic checks and a round cap. It improves quality but multiplies token cost.
Hindi: Generator draft बनाता है, critic rubric से जाँचता है, और approved होने तक loop चलता है। सख़्त rubric, deterministic checks और round cap रखो। इससे quality बढ़ती है पर token cost कई गुना हो जाती है।

---

## ➡️ Next Topic
**357. Agent State Sharing** — how multiple agents read and write the same state safely.
