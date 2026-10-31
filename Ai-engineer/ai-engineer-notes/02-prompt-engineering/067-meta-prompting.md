---

# 067. Meta Prompting
# हिंदी में: Meta Prompting — LLM से prompt लिखवाना और सुधरवाना

---

## 🔵 Simple Definition (English)
Meta prompting means using an LLM to create, critique or improve prompts. You give it a task description, some examples and failures, and it returns a better prompt. It treats the prompt as something to be generated and tested, like code.

## 🔵 सरल परिभाषा (Hindi)
Meta prompting में हम LLM से prompts बनवाते, परखवाते या सुधरवाते हैं। आप task का विवरण, कुछ examples और failures देते हैं, और वह बेहतर prompt लौटाता है। Prompt को code की तरह generate और test करने वाली चीज़ माना जाता है।

---

## 🔴 Problem it Solves
Writing a good prompt by hand is slow trial and error. Humans miss edge cases, use vague wording and forget formats. When a prompt fails on 15 inputs, it is hard to see the pattern.

A meta prompt shows the failures to an LLM and asks "what rule is missing?" It speeds up iteration, but the result must still be tested on a real eval set.

## 🔴 यह क्यों बना? (Hindi)
हाथ से अच्छा prompt लिखना धीमा trial-and-error है। इंसान edge cases भूल जाते हैं और शब्द अस्पष्ट रखते हैं। जब prompt 15 inputs पर फेल हो तो pattern देखना मुश्किल है। Meta prompt failures LLM को दिखाकर पूछता है "कौन सा rule missing है?" इससे iteration तेज़ होता है, पर नतीजा eval set पर test करना ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a first draft prompt (even a rough one)
Step 2 → Run it on an eval set; collect failed cases
Step 3 → Build a meta prompt: task + current prompt + failures + constraints
Step 4 → LLM proposes an improved prompt (and explains the change)
Step 5 → Run the NEW prompt on the same eval set
Step 6 → Keep it only if the score improves (no regressions)
Step 7 → Repeat a few rounds, then freeze and version the winner
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहला draft prompt लिखो (rough भी चलेगा)
Step 2 → Eval set पर चलाओ; failed cases इकट्ठा करो
Step 3 → Meta prompt बनाओ: task + मौजूदा prompt + failures + constraints
Step 4 → LLM सुधरा हुआ prompt सुझाता है (बदलाव की वजह के साथ)
Step 5 → नया prompt उसी eval set पर चलाओ
Step 6 → तभी रखो जब score बढ़े (regression नहीं)
Step 7 → कुछ rounds दोहराओ, फिर winner को freeze और version करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The first prompt "Give HS code" fails on accessories (a phone case classified as a phone). The failures list is sent in a meta prompt. The LLM suggests adding: "Accessories take their own heading, not the main product's heading" and one example. After re-testing, accuracy goes from 82% to 89%, and the new prompt becomes `v2`.

**Zomato-style**: An LLM generates 5 variants of a restaurant-review summariser prompt; the best by eval score ships.

## 🟡 Real Example Hindi mein
**Tariff System**: पहला prompt "HS code दो" accessories पर फेल होता है (phone case को phone की तरह classify किया)। Failures की list meta prompt में भेजी जाती है। LLM सुझाता है: "Accessories का अपना heading होता है, main product का नहीं" और एक example। Re-test के बाद accuracy 82% से 89% हुई, और नया prompt `v2` बना।

**Zomato-style**: LLM restaurant-review summariser के 5 prompt variants बनाता है; eval score में सबसे अच्छा ship होता है।

---

## 💻 Code Example — Basic
```python
# Basic: build a meta prompt from failures (pure Python, offline)

current_prompt = "Give the HS code for the product."            # prompt we want to improve

failures = [                                                     # cases where it failed
    {"input": "phone case", "expected": "3926.90", "got": "8517.13"},
    {"input": "usb charger", "expected": "8504.40", "got": "8517.13"},
]

def build_meta_prompt(task: str, prompt: str, fails: list[dict[str, str]]) -> str:
    lines = [f"- input: {f['input']} | expected: {f['expected']} | got: {f['got']}" for f in fails]
    return (
        "You are a prompt engineer.\n"                           # role of the meta model
        f"TASK: {task}\n"                                         # what the prompt must do
        f"CURRENT PROMPT:\n{prompt}\n"                            # the prompt to improve
        "FAILURES:\n" + "\n".join(lines) + "\n"                   # evidence of what is wrong
        "Rewrite the prompt to fix these failures without breaking other cases.\n"
        "Return ONLY the new prompt text."                        # strict output rule
    )

meta = build_meta_prompt("Classify products to HS codes", current_prompt, failures)
print(meta)                                                       # inspect the meta prompt
# In real life: new_prompt = llm(meta); then re-run the eval set on new_prompt
```

## 💻 Code Example — Advanced
```python
# Production: optimisation loop with eval gating, async, and error handling
from __future__ import annotations

import asyncio                                    # async runner
from dataclasses import dataclass                 # small data classes
from typing import Awaitable, Callable            # type hints

LLM = Callable[[str], Awaitable[str]]             # prompt -> reply

@dataclass(frozen=True)
class Case:
    product: str                                  # eval input
    expected: str                                 # correct HS code

async def score(llm: LLM, prompt: str, cases: list[Case]) -> tuple[float, list[Case]]:
    """Run a prompt on all cases; return accuracy and the failed cases."""
    async def one(c: Case) -> bool:
        reply = await llm(f"{prompt}\nProduct: {c.product}")      # classify one case
        return reply.strip() == c.expected                        # exact match check
    results = await asyncio.gather(*(one(c) for c in cases))      # run cases concurrently
    failed = [c for c, ok in zip(cases, results) if not ok]       # collect failures
    return sum(results) / len(cases), failed                      # accuracy, failures

async def improve(llm: LLM, meta_llm: LLM, prompt: str, cases: list[Case], rounds: int = 3) -> str:
    best_prompt = prompt                                          # current best
    best_score, failed = await score(llm, best_prompt, cases)     # baseline score
    for _ in range(rounds):                                       # limited rounds (cost control)
        if not failed:                                            # nothing left to fix
            break
        fail_text = "\n".join(f"{c.product} -> expected {c.expected}" for c in failed[:10])
        meta = (f"Improve this prompt.\nPROMPT:\n{best_prompt}\nFAILURES:\n{fail_text}\n"
                "Return ONLY the new prompt.")
        try:
            candidate = (await meta_llm(meta)).strip()            # meta model proposes
        except Exception as exc:                                  # provider error
            raise RuntimeError(f"meta call failed: {exc}") from exc
        if not candidate or len(candidate) > 2000:                # basic sanity guard
            continue
        cand_score, cand_failed = await score(llm, candidate, cases)   # test candidate
        if cand_score > best_score:                               # accept only real gains
            best_prompt, best_score, failed = candidate, cand_score, cand_failed
    return best_prompt

async def _demo() -> None:
    async def llm(p: str) -> str:
        fixed = "accessories" in p                                # new prompt contains the rule
        if "case" in p:
            return "3926.90" if fixed else "8517.13"
        return "8518.30"
    async def meta_llm(p: str) -> str:
        return "Give the HS code. Note: accessories take their own heading."
    cases = [Case("phone case", "3926.90"), Case("earbuds", "8518.30")]
    print(await improve(llm, meta_llm, "Give the HS code.", cases))

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: each round costs one meta call (prompt + up to 10 failures, ~500-1500 tokens) plus a full eval run (cases x prompt tokens). Cap rounds and use a small eval subset while exploring.

---

## 🟠 FastAPI Integration
Expose an internal admin endpoint that proposes a new prompt version for review. Never auto-deploy; a human approves after seeing eval scores.

```python
from fastapi import FastAPI                      # framework
from pydantic import BaseModel                   # models
from openai import AsyncOpenAI                   # openai>=1

app = FastAPI()                                  # app
client = AsyncOpenAI()                           # client

class ImproveIn(BaseModel):
    prompt: str                                  # current prompt
    failures: list[str]                          # failure descriptions

async def meta_llm(p: str) -> str:
    r = await client.chat.completions.create(
        model="gpt-4o", temperature=0.4, max_tokens=800,
        messages=[{"role": "user", "content": p}])
    return r.choices[0].message.content or ""

@app.post("/admin/prompt/suggest")
async def suggest(body: ImproveIn) -> dict[str, str]:
    meta = f"Improve this prompt.\nPROMPT:\n{body.prompt}\nFAILURES:\n" + "\n".join(body.failures)
    return {"suggested_prompt": await meta_llm(meta), "status": "needs_eval_and_approval"}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's prompt hub and LangSmith support prompt iteration with datasets and evaluators. In LangGraph, build a loop: `run_eval -> propose_prompt -> run_eval -> (better? keep : discard) -> repeat`, with a max-iterations counter in the state to stop.

```python
from langchain_core.prompts import ChatPromptTemplate          # prompt template
from langchain_core.output_parsers import StrOutputParser      # string output
from langchain_openai import ChatOpenAI                        # model

meta_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a prompt engineer. Return ONLY an improved prompt."),
    ("user", "PROMPT:\n{prompt}\nFAILURES:\n{failures}"),
])
meta_chain = meta_prompt | ChatOpenAI(model="gpt-4o", temperature=0.4) | StrOutputParser()
# new_prompt = await meta_chain.ainvoke({"prompt": old, "failures": fail_text})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Accepting the generated prompt without testing
✅ Correct: Gate on eval score.
```python
# Wrong
prompt = await meta_llm(meta)             # ship it directly

# Right
new_score, _ = await score(llm, candidate, cases)
if new_score > old_score:
    prompt = candidate
```

❌ Mistake 2: Overfitting to the failures (prompt memorises the 10 examples)
✅ Correct: Keep a held-out test set that the meta loop never sees.
```python
# Wrong: tune and report on the same cases
# Right
train, holdout = cases[:80], cases[80:]
```

❌ Mistake 3: Letting the prompt grow every round. Ask for "shorter and clearer" and cap length.

---

## 🧠 Tricky Interview Question
**Q**: "After 5 rounds of meta prompting your prompt scores 95% on the eval set, but production accuracy is 80%. Why?"

**Answer**: Overfitting and distribution shift. The eval set was reused for every round, so the prompt memorised its quirks, and the eval set may not match real traffic. Fix: split train/validation/holdout, refresh the eval set with sampled production data, limit rounds, prefer general rules over case-specific hacks, and monitor live accuracy by sampling and human labelling.

---

## ⚫ Interview Questions + Answers

Q1: What is meta prompting?
A1: Using an LLM to write or improve prompts, often by showing it the task and failures.

Q2: Why is human review still needed?
A2: The model may add wrong rules, bias, or overfit. A human checks intent, safety and tone before release.

Q3: What inputs go into a good meta prompt?
A3: Task description, current prompt, concrete failures with expected outputs, constraints (length, format), and an instruction to return only the new prompt.

Q4: Which model should do the meta step?
A4: Often a stronger model (it is a low-volume, high-value call), while the production prompt runs on a cheaper model.

Q5 (Hard): How do you build an automatic prompt optimiser safely?
A5: Use a train/validation/holdout split, a metric with a baseline, candidate generation with several variants per round, selection by validation score with a margin to avoid noise, a length and safety check, a max-rounds budget, and final human approval plus versioning. Log every candidate and score for audit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have an eval set and failure examples
- Hand-tuning has plateaued
- You need many prompt variants quickly

❌ Avoid when:
- You have no eval set (you cannot tell better from worse)
- The prompt is already meeting the target
- The task is safety-critical and unreviewed changes are not allowed

---

## 📊 Visual Diagram
```
     +--------------------+
     |  Current prompt v1 |
     +--------------------+
               |
               v
      Run eval set  ---> score 82%, failed cases
               |
               v
   +-------------------------+
   | META PROMPT             |
   | task + prompt + failures|
   +-------------------------+
               |
               v
        Stronger LLM
               |
               v
      Candidate prompt v2
               |
               v
      Run eval set again
         |            |
   score up       score same/down
         |            |
   keep v2         discard
```

---

## 💰 Cost Impact
- Meta calls are few but use a strong model and long inputs.
- The expensive part is re-running the eval set each round (cases x tokens).
- A better prompt can lower production cost (fewer retries, shorter outputs, cheaper model possible).

Optimisation: use a small dev subset during search and the full set only for the final check, limit rounds, cache eval results for unchanged prompts, and ask the meta model for concise prompts.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Meta prompt | Prompt that writes/improves prompts | Prompts बनाने वाला prompt |
| Eval set | Labelled test cases | Labelled test cases |
| Overfitting | Works on tests, fails in real use | Test पर अच्छा, असल में कमज़ोर |
| Holdout | Data kept unseen for final check | अंतिम जाँच के लिए छुपाया data |
| Regression | New version breaks old behaviour | नया version पुराना तोड़ दे |
| Candidate | Proposed new prompt | सुझाया गया नया prompt |

---

## ⚡ 3-Line Summary
English: Meta prompting uses an LLM to draft or fix prompts from task descriptions and failures. Accept a new prompt only if the eval score improves on held-out data. Keep a human in the loop and version the result.
Hindi: Meta prompting में LLM task और failures से prompts बनाता या सुधारता है। नया prompt तभी रखो जब held-out data पर eval score बढ़े। Human को loop में रखो और नतीजे को version करो।

---

## ➡️ Next Topic
**068. Prompt Compression** — shrinking prompts and context to save tokens without losing meaning.
