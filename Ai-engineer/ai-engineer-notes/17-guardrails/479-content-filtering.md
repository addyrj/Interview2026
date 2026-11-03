
# 479. Content Filtering
# हिंदी में: Content Filtering

---

## 🔵 Simple Definition (English)
Content filtering checks text going into or coming out of an LLM and blocks, redacts or flags anything that breaks your policy: hate, harassment, sexual content, self-harm, violence, illegal advice, secrets, profanity, or off-brand content. It is a safety layer around the model.

## 🔵 सरल परिभाषा (Hindi)
Content filtering LLM में जाने वाले और उससे निकलने वाले text को check करता है और policy तोड़ने वाली चीज़ें (hate, harassment, sexual content, self-harm, violence, illegal advice, secrets, गाली, off-brand content) block, redact या flag करता है। यह model के चारों तरफ़ एक safety layer है।

---

## 🔴 Problem it Solves
Models can produce or be fed harmful content. A public chatbot that insults users, a support bot that leaks internal notes, or a user who pastes abusive text can cause legal, brand and safety damage. Built-in model safety is not enough: it is generic, can change between versions, and does not know your company policy.

## 🔴 यह क्यों बना? (Hindi)
Models harmful content बना सकते हैं या उन्हें दिया जा सकता है। Public chatbot जो users को गाली दे, support bot जो internal notes leak करे, या user जो abusive text paste करे: इनसे legal, brand और safety नुक़सान हो सकता है। Model की built-in safety काफ़ी नहीं: वह generic है, versions में बदलती है और आपकी company policy नहीं जानती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define policy: categories, severity levels, action per category (block / redact / flag / escalate)
Step 2 → INPUT filter: check user text (rules + classifier / moderation API) before the LLM
Step 3 → If violation -> return a safe refusal message, log the event, skip the LLM call (saves tokens)
Step 4 → Call the LLM with a safe prompt
Step 5 → OUTPUT filter: check the model response with the same or a stricter policy
Step 6 → Violation -> block, redact, or regenerate once with stricter instructions, else fallback message
Step 7 → Log category + score (not raw sensitive text), review samples, tune thresholds to balance false positives and negatives
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Policy तय करो: categories, severity levels, हर category की action (block / redact / flag / escalate)
Step 2 → INPUT filter: LLM से पहले user text check करो (rules + classifier / moderation API)
Step 3 → Violation हो तो safe refusal message दो, event log करो, LLM call skip करो (tokens बचते हैं)
Step 4 → Safe prompt के साथ LLM call करो
Step 5 → OUTPUT filter: model response को वही या सख़्त policy से check करो
Step 6 → Violation -> block, redact, या सख़्त instructions से एक बार regenerate, नहीं तो fallback message
Step 7 → Category + score log करो (raw sensitive text नहीं), samples review करो, false positives/negatives का balance tune करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importers paste free-text notes. The filter blocks abusive language to officers, redacts bank account numbers, and rejects requests that ask how to under-declare goods to evade duty (illegal advice). On output, it makes sure the model never reveals internal enforcement notes. Blocked inputs never reach the LLM, so no tokens are spent.

**Zomato AI**: Review summarisation filters slurs and personal phone numbers; the chatbot refuses to produce content that insults delivery partners.

## 🟡 Real Example Hindi mein
**Tariff System**: Importers free-text notes paste करते हैं। Filter officers के प्रति abusive भाषा block करता है, bank account numbers redact करता है और duty चोरी (under-declaration) सिखाने वाली requests reject करता है (illegal advice)। Output में model कभी internal enforcement notes reveal न करे, यह सुनिश्चित होता है। Blocked inputs LLM तक नहीं जाते, इसलिए tokens खर्च नहीं होते।

**Zomato AI**: Review summarisation slurs और personal phone numbers filter करती है; chatbot delivery partners का अपमान करने वाला content नहीं बनाता।

---

## 💻 Code Example — Basic
```python
# Pure-Python rule-based content filter (run directly; real systems add ML classifiers)
import re  # regular expressions
from dataclasses import dataclass  # result container


@dataclass
class FilterResult:
    allowed: bool  # may the text pass?
    category: str | None  # which rule fired
    cleaned: str  # text after redaction


BLOCK_PATTERNS = {
    "evasion": re.compile(r"\b(under[- ]?declare|evade (the )?(duty|tax)|fake invoice)\b", re.I),  # illegal advice
    "abuse": re.compile(r"\b(idiot|stupid|scum)\b", re.I),  # toy abuse list
}
REDACT_PATTERNS = {
    "account": re.compile(r"\b\d{9,18}\b"),  # long digit runs like bank accounts
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),  # email addresses
}


def filter_text(text: str) -> FilterResult:
    """Block policy violations, redact sensitive data, otherwise pass."""
    for name, pat in BLOCK_PATTERNS.items():  # check block rules first
        if pat.search(text):  # violation found
            return FilterResult(False, name, "")  # stop with category
    cleaned = text  # start from original
    for name, pat in REDACT_PATTERNS.items():  # then redact
        cleaned = pat.sub(f"[{name.upper()}]", cleaned)  # replace matches
    return FilterResult(True, None, cleaned)  # allowed with redactions


if __name__ == "__main__":
    print(filter_text("How do I under-declare my shipment?"))  # blocked: evasion
    print(filter_text("Send to a@b.com acct 123456789012"))  # allowed + redacted
```

## 💻 Code Example — Advanced
```python
# Layered async filter: fast rules first, then an optional moderation classifier; wraps the LLM call (production style)
import asyncio  # async
import logging  # logs
from typing import Awaitable, Callable  # types

logger = logging.getLogger("content-filter")  # logger
SAFE_REFUSAL = "I can't help with that request."  # user-facing message

Classifier = Callable[[str], Awaitable[dict[str, float]]]  # returns category -> score


class ContentGuard:
    def __init__(self, classifier: Classifier | None = None, thresholds: dict[str, float] | None = None) -> None:
        self.classifier = classifier  # e.g. wraps a moderation API or a local model
        self.thresholds = thresholds or {"hate": 0.7, "violence": 0.8, "self_harm": 0.5}  # per-category limits

    async def check(self, text: str) -> tuple[bool, str | None]:
        """Return (allowed, category)."""
        quick = filter_text(text)  # cheap rules (from the basic example)
        if not quick.allowed:  # rule violation
            return False, quick.category  # block immediately, no network call
        if self.classifier is None:  # no ML layer configured
            return True, None  # allow
        try:
            scores = await asyncio.wait_for(self.classifier(text), timeout=2.0)  # bounded latency
        except Exception as exc:  # classifier failed or timed out
            logger.error("classifier error: %s", exc)  # log
            return True, None  # fail open here; choose fail closed for high-risk apps
        for cat, limit in self.thresholds.items():  # compare scores with thresholds
            if scores.get(cat, 0.0) >= limit:  # over the limit
                return False, cat  # block
        return True, None  # clean

    async def guarded_call(self, user_text: str, llm: Callable[[str], Awaitable[str]]) -> str:
        ok, cat = await self.check(user_text)  # input filter
        if not ok:  # blocked
            logger.info("input blocked: %s", cat)  # log category only
            return SAFE_REFUSAL  # no LLM tokens spent
        answer = await llm(user_text)  # model call
        ok, cat = await self.check(answer)  # output filter
        if not ok:  # unsafe output
            logger.warning("output blocked: %s", cat)  # alert
            return SAFE_REFUSAL  # safe fallback
        return answer  # clean answer
```
Token usage: input blocks cost zero model tokens; a classifier (if LLM-based) adds tokens, so use cheap rules first and a small model or dedicated moderation endpoint for the rest.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app


class Req(BaseModel):
    note: str  # importer free-text


@app.post("/classify")
async def classify(req: Req) -> dict:
    result = filter_text(req.note)  # input filter (from the basic example)
    if not result.allowed:  # violation
        raise HTTPException(status_code=422, detail={"blocked": result.category})  # reject
    # answer = await llm.ainvoke(result.cleaned)  # call model with redacted text
    answer = "8518.30"  # placeholder
    out = filter_text(answer)  # output filter
    if not out.allowed:  # unsafe output
        raise HTTPException(status_code=502, detail="response blocked")  # server side block
    return {"hs_code": out.cleaned}  # safe response
```
A FastAPI dependency or middleware can apply the same guard to every route.

---

## 🔗 LangChain / LangGraph Connection
In LangGraph, put filters as nodes: `input_guard -> llm -> output_guard`, with conditional edges that route to a `refuse` node on violation. In LangChain, wrap the guard as a `RunnableLambda` in the chain.

```python
from langchain_core.runnables import RunnableLambda  # wrap plain functions


def guard(text: str) -> str:
    r = filter_text(text)  # reuse the basic filter
    if not r.allowed:  # violation
        raise ValueError(f"blocked: {r.category}")  # stop the chain
    return r.cleaned  # redacted text


chain = RunnableLambda(guard)  # | prompt | llm | RunnableLambda(guard)  (compose in a real chain)
print(chain.invoke("Please email a@b.com"))  # -> "Please email [EMAIL]"
```
OpenAI also offers a moderation endpoint and other vendors similar ones; check current docs for model names and categories.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Filtering only the input
✅ Correct: Filter the output too: models can generate unsafe text from innocent input, or leak retrieved private data.
```python
# Wrong
answer = await llm(user_text)
return answer
# Right
answer = await llm(user_text)
ok, _ = await guard.check(answer)
return answer if ok else SAFE_REFUSAL
```

❌ Mistake 2: Keyword lists only
✅ Correct: Keywords miss paraphrases and wrongly block innocent text ("kill the process"). Layer rules, classifiers and human review of samples.
```python
# Wrong: if "kill" in text: block
# Right: rules for clear cases + classifier score with a tuned threshold
```

---

## 🧠 Tricky Interview Question
**Q**: "Your filter blocks 2% of legitimate importer requests (false positives) but compliance wants zero harmful outputs. How do you balance this?"

**Answer**: You cannot reach zero on both; it is a threshold trade-off. Use severity tiers: hard block only on high-confidence, high-severity categories; for borderline scores, redact, add a warning, route to human review, or ask the user to rephrase. Measure precision and recall on a labelled set from your own traffic, set category-specific thresholds (stricter for self-harm or illegal advice), add an appeal or review path for false positives, and keep audit logs. Revisit thresholds regularly.

---

## ⚫ Interview Questions + Answers

Q1: What is content filtering in LLM apps?
A1: Checking inputs and outputs against a policy and blocking, redacting or flagging violations.

Q2: Why filter outputs as well as inputs?
A2: The model can still generate unsafe or leaked content; output checks are the last line of defence.

Q3: What is the trade-off between false positives and false negatives?
A3: Stricter filters block more bad content but also more good content. Tune thresholds per category and risk level.

Q4: Why run cheap rules before ML classifiers?
A4: Rules are fast and free; they remove obvious cases so the costlier classifier or LLM judge runs on fewer requests.

Q5: Design content filtering for a public multilingual tariff chatbot.
A5: Policy table per category with actions; input rules + multilingual moderation model; PII redaction; refusal templates in the user's language; the same checks on output; fail-closed for high-risk categories and fail-open with logging for low-risk when the classifier is down; per-request audit log without raw sensitive text; red-team test set run in CI; monitoring of block rate by category and language (to detect language bias); human review queue for borderline cases.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Public or customer-facing apps
- Regulated or brand-sensitive domains
- Users can paste arbitrary text

❌ Avoid heavy filtering when:
- Internal batch jobs on trusted, structured data (use lightweight checks)
- Filters add unacceptable latency and the risk is very low

---

## 📊 Visual Diagram
```
 User text
    |
 [INPUT FILTER] --violation--> safe refusal (0 LLM tokens) --> log
    | pass (redacted)
    v
   LLM
    |
 [OUTPUT FILTER] --violation--> block / regenerate / fallback --> log
    | pass
    v
 Response to user
```

---

## 💰 Cost Impact
Input blocks save tokens: no LLM call for blocked requests. Rule checks cost microseconds. Classifier layers add small cost: dedicated moderation endpoints are often free or very cheap (check current provider pricing), while LLM-as-judge filters add input and output tokens per request.

Optimise: rules first, small models for classification, run input and output checks in parallel with generation when latency matters (cancel generation if input is flagged), cache decisions for repeated texts, and sample (not check) very low-risk internal traffic.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Content filter | Policy check on text | Text पर policy check |
| Moderation | Classify harmful content | Harmful content की पहचान |
| Redaction | Mask sensitive parts | संवेदनशील हिस्से छुपाना |
| False positive | Safe text wrongly blocked | सुरक्षित text ग़लत block |
| False negative | Harmful text missed | Harmful text छूट गया |
| Threshold | Score limit to act | Action का score limit |
| Fail closed | Block if unsure or down | शक या failure पर block |

---

## ⚡ 3-Line Summary
English: Content filtering checks inputs and outputs against policy and blocks, redacts or flags violations. Layer cheap rules, classifiers and human review, and tune thresholds per category. Blocked inputs save LLM tokens.
Hindi: Content filtering inputs और outputs को policy से check करके violations block, redact या flag करता है। सस्ते rules, classifiers और human review को layer करो और हर category के लिए thresholds tune करो। Blocked inputs से LLM tokens बचते हैं।

---

## ➡️ Next Topic
**480. Safety Layer in FastAPI** — putting all guardrails (input, output, PII, injection) into one reusable FastAPI layer.
