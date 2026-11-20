---

# 183. Critic Pattern
# हिंदी में: Critic Pattern (आलोचक Agent)
# Framework: All (LangGraph / CrewAI / OpenAI SDK / AutoGen)
# Already Known: No

> Code verified offline with a fake LLM (no API key). Python 3.13, fastapi 0.163.1, httpx 0.28.1, pydantic 2.14.3. Real model calls: not run, needs an LLM API key. Token numbers below are approximate formulas, not measurements.

---

## 🔵 Simple Definition (2-3 lines)
The Critic pattern adds a second, separate reviewer (the "critic") that reads an agent's draft and returns a structured verdict: pass or fail, plus a list of concrete problems. The critic does not rewrite the answer. It only judges it against a rubric.

## 🔵 सरल परिभाषा (Hindi)
Critic pattern में एक दूसरा, अलग reviewer ("critic") agent के draft को पढ़ता है और structured verdict देता है: pass या fail, साथ में ठोस समस्याओं की सूची। Critic जवाब दोबारा नहीं लिखता, सिर्फ़ rubric के आधार पर परखता है।

---

## 🔴 Problem it Solves
A single LLM call grades its own homework badly. It confidently returns an HS code that does not match the product, a wrong duty rate, or an answer with no source. Without an independent check, these errors reach the user or trigger a wrong action. The critic gives a cheap quality gate before output leaves the system.

## 🔴 यह क्यों बना? (Hindi)
एक ही LLM call अपनी कॉपी खुद जाँचे तो अक्सर चूक जाता है। वह पूरे आत्मविश्वास से ऐसा HS code दे देता है जो product से मेल नहीं खाता, या बिना source का duty rate। स्वतंत्र जाँच के बिना ये गलतियाँ user तक या किसी गलत action तक पहुँच जाती हैं। Critic output निकलने से पहले एक सस्ता quality gate देता है।

---

## 🟢 How it Works

```
Step 1 → Worker agent produces a draft (HS code + duty + source)
Step 2 → Critic receives draft + rubric (NOT the worker's hidden reasoning)
Step 3 → Critic returns structured verdict: {approved, issues[], score}
Step 4 → approved=True  → release the draft
Step 5 → approved=False → return issues to caller / worker (see 184 for the loop)
Step 6 → Log verdict + tokens for evaluation and audit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Worker agent draft बनाता है (HS code + duty + source)
Step 2 → Critic को draft + rubric मिलता है (worker की hidden reasoning नहीं)
Step 3 → Critic structured verdict देता है: {approved, issues[], score}
Step 4 → approved=True  → draft release करो
Step 5 → approved=False → issues वापस भेजो (loop के लिए note 184 देखो)
Step 6 → Verdict और tokens log करो ताकि evaluation और audit हो सके
```

---

## 🟡 Real World Example
**Tariff Agent**: The worker proposes "8518.22 – loudspeakers, duty 7.5%". The critic checks the rubric: (1) code format is `NNNN.NN`, (2) a source citation exists, (3) duty is a percentage between 0 and 100. If the source is missing, the verdict is `approved=False, issues=["missing source"]`. Other examples: a Code Agent whose patch is reviewed for tests, a Customer Support agent whose reply is checked for policy violations.

## 🟡 Real Example Hindi mein
**Tariff Agent**: Worker "8518.22 - loudspeakers, duty 7.5%" सुझाता है। Critic rubric से जाँचता है: (1) code का format `NNNN.NN`, (2) source citation मौजूद, (3) duty 0 से 100 के बीच का प्रतिशत। Source न हो तो verdict `approved=False, issues=["missing source"]`। दूसरे उदाहरण: Code Agent के patch में tests की जाँच, Customer Support के reply में policy violation की जाँच।

---

## 💻 Code Example — Basic
```python
# Basic Critic pattern: a worker drafts, a rule-based critic judges. Runs offline.
from dataclasses import dataclass, field          # simple data containers
import re                                         # format check for HS codes


@dataclass
class Verdict:                                    # the critic's structured output
    approved: bool                                # pass / fail
    issues: list[str] = field(default_factory=list)  # concrete problems found


def worker(product: str) -> dict[str, str]:       # fake worker (stands in for an LLM)
    # deliberately omits the source to show the critic catching it
    return {"product": product, "hs_code": "8518.22", "duty": "7.5%", "source": ""}


def critic(draft: dict[str, str]) -> Verdict:     # judges the draft, never edits it
    issues: list[str] = []                        # collect all problems, not just the first
    if not re.fullmatch(r"\d{4}\.\d{2}", draft.get("hs_code", "")):  # format rule
        issues.append("hs_code must look like 8518.22")
    if not draft.get("source"):                   # grounding rule
        issues.append("missing source citation")
    duty = draft.get("duty", "").rstrip("%")      # strip the percent sign
    try:
        if not 0 <= float(duty) <= 100:           # range rule
            issues.append("duty out of range")
    except ValueError:                            # not a number at all
        issues.append("duty is not numeric")
    return Verdict(approved=not issues, issues=issues)  # approved only if no issues


if __name__ == "__main__":
    draft = worker("bluetooth speaker")           # step 1: draft
    verdict = critic(draft)                       # step 2: critique
    print(draft)                                  # show draft
    print(verdict)                                # Verdict(approved=False, issues=['missing source citation'])
    assert verdict.approved is False              # sanity check for this demo
```

## 💻 Code Example — Advanced
```python
# Advanced: async FastAPI endpoint, LLM-style critic with schema validation,
# timeout, error handling, and approximate token accounting. Runs offline.
import asyncio                                    # async runtime
import json                                       # parse critic output
import logging                                    # structured logs
from fastapi import FastAPI, HTTPException        # web framework
from fastapi.testclient import TestClient         # in-process test client
from pydantic import BaseModel, Field, ValidationError  # validation (pydantic v2)

log = logging.getLogger("critic")                 # module logger


class Draft(BaseModel):                           # request body
    product: str = Field(min_length=2)            # product description
    hs_code: str                                  # proposed code
    source: str = ""                              # citation


class CriticOut(BaseModel):                       # strict contract for the critic LLM
    approved: bool
    issues: list[str]
    score: float = Field(ge=0, le=1)


def approx_tokens(text: str) -> int:              # rough estimate: ~4 chars per token
    return max(1, len(text) // 4)                 # approximate, not a real tokenizer


async def fake_critic_llm(prompt: str) -> str:    # stand-in for a real async LLM call
    await asyncio.sleep(0)                        # yield to the event loop like real I/O
    bad = "source: ''" in prompt                  # toy rule: empty source -> reject
    return json.dumps({"approved": not bad,       # LLMs return JSON text
                       "issues": ["missing source"] if bad else [],
                       "score": 0.4 if bad else 0.9})


async def run_critic(d: Draft, timeout_s: float = 5.0) -> tuple[CriticOut, int]:
    prompt = f"Rubric: code NNNN.NN, source required.\nproduct: {d.product}\nhs_code: {d.hs_code}\nsource: '{d.source}'"
    try:
        raw = await asyncio.wait_for(fake_critic_llm(prompt), timeout_s)  # bounded wait
    except asyncio.TimeoutError:                  # LLM too slow
        raise HTTPException(504, "critic timed out")
    try:
        out = CriticOut.model_validate_json(raw)  # never trust raw LLM JSON
    except ValidationError as exc:                # malformed critic output
        log.error("bad critic output: %s", exc)
        raise HTTPException(502, "critic returned invalid output")
    return out, approx_tokens(prompt) + approx_tokens(raw)  # estimate tokens used


app = FastAPI()                                   # the API


@app.post("/review")                              # async endpoint
async def review(d: Draft) -> dict:
    out, tokens = await run_critic(d)             # call the critic
    return {"verdict": out.model_dump(), "approx_tokens": tokens}


if __name__ == "__main__":
    client = TestClient(app)                      # no server needed
    r = client.post("/review", json={"product": "speaker", "hs_code": "8518.22"})
    print(r.status_code, r.json())                # approved False, issue: missing source
    r = client.post("/review", json={"product": "speaker", "hs_code": "8518.22", "source": "WCO"})
    print(r.status_code, r.json()["verdict"]["approved"])  # True
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Critic as | A graph node after the worker node | A second Agent with a review Task | A second Agent, called as a tool or after the first run | A second agent in a team chat |
| Branch on verdict | Conditional edge (approved vs not) | Task order / your own code | Your Python code (or handoff) | Termination condition or selector |
| Structured verdict | Pydantic/structured output in node | Task output schema | Agent `output_type` | Structured message / your parsing |
| State | Explicit shared state | Task context passed along | Run context / messages | Message history |
| Control | Highest (explicit) | Medium (declarative) | Medium (code-driven) | Medium (chat-driven) |

---

## ⚠️ Common Mistakes
❌ Mistake 1: The critic sees the worker's chain-of-thought and just agrees (anchoring).
✅ Correct: Give the critic only the final draft, the task and the rubric.

❌ Mistake 2: Vague rubric like "is this good?".
✅ Correct: Specific, checkable criteria (format, source present, range) and a numeric score.

❌ Mistake 3: Trusting the critic's raw JSON.
✅ Correct: Validate with Pydantic; treat invalid output as an error, not as "approved".

❌ Mistake 4: Same model, same prompt style for worker and critic, so they share blind spots.
✅ Correct: Use a different prompt, and ideally a different or stronger model, for the critic.

---

## 🧠 Tricky Interview Question
Your critic approves 98% of drafts, yet users still report wrong HS codes. What is wrong, and how do you fix it?

Answer: The critic is probably a "yes-man": same model family, no ground truth, and a loose rubric. An LLM critic can only catch errors it can recognise from text. Fixes: (1) add deterministic checks first (regex, lookup in the official tariff table) and use the LLM critic only for what rules cannot check; (2) build a labelled eval set of known-bad drafts and measure the critic's recall on it; (3) have the critic verify claims against retrieved evidence instead of its own memory; (4) use a different, stronger model; (5) track approval rate and disagreement with human review as a metric. A critic with no ground truth is a confidence amplifier, not a verifier.

---

## ⚫ Interview Questions + Answers

Q1: (Easy) What does a critic agent do?
A1: It reviews another agent's output against a rubric and returns a structured verdict with issues. It judges, it does not rewrite.

Q2: (Medium) Why separate the critic from the worker?
A2: Self-review is biased; the model tends to defend its own output. A separate call with a different prompt (and maybe model) gives an independent view and a clean place to attach a rubric, logging and metrics.

Q3: (Hard) How do you stop a critic from being too lenient or too harsh?
A3: Calibrate on a labelled set, measure precision and recall of its rejections, use explicit scored criteria, and tune a threshold. Combine with deterministic validators for hard rules.

Q4: (Hard) Critic vs guardrail vs evaluator: what is the difference?
A4: A guardrail blocks unsafe or invalid input/output in the live path (usually fast, rule-based). A critic is a quality judge in the live path that may trigger retries. An evaluator runs offline over many samples to measure quality. They can share the same rubric code.

Q5: (System Design) Design a critic layer for a tariff-classification API serving 50 requests per second.
A5: Worker returns a draft; run cheap deterministic checks first (format, table lookup); only borderline cases go to an LLM critic (small model, strict JSON schema, 3-5 s timeout). Run the critic async and in parallel across requests with a concurrency limit. On reject, return a "needs review" status or hand to the loop in note 184, with a max-attempt cap. Log verdicts, rubric version and tokens; sample a percentage for human audit to detect critic drift; cache verdicts by hash of (product, code).

---

## 💰 Cost Impact
- Extra calls: one critic call per draft. Approximate token formula: `critic_tokens = rubric + draft + verdict` which is typically a few hundred tokens for short drafts (approximate, depends on your prompt).
- Total cost per request is roughly `worker_cost + critic_cost`, so a critic on the same model about doubles the LLM cost; a smaller critic model is far cheaper (approximate, from public pricing at time of writing, verify).
- Tips: run deterministic checks first, send only uncertain drafts to the LLM critic, keep the rubric short, ask for a compact JSON verdict, cache by input hash.

---

## 🔷 When to Use
✅ Use when:
- Wrong output is costly (customs duty, legal, medical, financial)
- You can write a checkable rubric
- You need an audit trail of why output was accepted

❌ Avoid when:
- Low-stakes chat where latency matters most
- The check is fully rule-based (use plain validation code)
- You have no ground truth and no eval set to calibrate the critic

---

## 📊 Visual Diagram
```
 user request
     |
     v
 +----------+   draft    +----------+
 |  Worker  | ---------> |  Critic  |  rubric + draft only
 +----------+            +----------+
                              |
                  {approved, issues, score}
                      /               \
              approved=True       approved=False
                   |                    |
                   v                    v
             release answer      issues -> caller / loop (184)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Critic | Reviewer that judges output | आलोचक / समीक्षक |
| Rubric | Checklist of criteria | मूल्यांकन सूची |
| Verdict | Structured pass/fail result | निर्णय |
| Anchoring | Judge copies worker's bias | पूर्वाग्रह से प्रभावित होना |
| Ground truth | Known correct answer or data | सही आधार डेटा |
| Guardrail | Rule that blocks bad output | सुरक्षा नियम |

---

## ⚡ 3-Line Summary
English: A critic is a separate reviewer that judges a draft against a rubric and returns a structured verdict.
It improves safety and quality but costs an extra call and is only as good as its rubric and ground truth.
Validate its JSON, calibrate it on labelled data, and combine it with deterministic checks.

Hindi: Critic एक अलग reviewer है जो rubric से draft को परखकर structured verdict देता है।
इससे quality और safety बढ़ती है, पर एक extra call लगती है और वह rubric व ground truth जितना ही अच्छा है।
उसका JSON validate करो, labelled data पर calibrate करो और deterministic checks के साथ मिलाओ।

---

## ➡️ Next Topic
184. Generator-Critic Loop: connects the critic to the worker so rejected drafts are revised automatically until they pass or a retry limit is reached.

---
