---

# 472. PII Detection + Redaction
# हिंदी में: PII की पहचान और Redaction

---

## 🔵 Simple Definition (English)
PII (Personally Identifiable Information) is data that identifies a person: name, phone, email, address, Aadhaar, PAN, passport, card number. PII detection finds it in text; redaction replaces it with placeholders (like `[PHONE]`) or reversible tokens so the LLM, logs and caches never store the real value.

## 🔵 सरल परिभाषा (Hindi)
PII (Personally Identifiable Information) वह data है जो किसी इंसान की पहचान कराता है: नाम, फोन, email, पता, Aadhaar, PAN, passport, card number। PII detection उसे text में खोजता है; redaction उसे placeholders (जैसे `[PHONE]`) या reversible tokens से बदलता है ताकि LLM, logs और caches में असली value न जाए।

---

## 🔴 Problem it Solves
Sending raw PII to third-party LLM APIs, logs, vector stores and caches creates legal risk (DPDP Act, GDPR), breach impact and trust loss. Redaction lets you still use the LLM on the useful part of the text.

## 🔴 यह क्यों बना? (Hindi)
Raw PII को third-party LLM APIs, logs, vector stores और caches में भेजना कानूनी जोखिम (DPDP Act, GDPR), breach का असर और भरोसे का नुकसान पैदा करता है। Redaction से text के काम के हिस्से पर LLM फिर भी चल सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Detect: regex for structured PII (phone, email, PAN, Aadhaar, card + Luhn)
Step 2 → Detect: NER model (Microsoft Presidio, spaCy) for names, addresses, orgs
Step 3 → Resolve overlaps, assign entity types and scores
Step 4 → Replace: mask ([PHONE]) or tokenise (<PHONE_1>) with a private mapping
Step 5 → Send redacted text to the LLM
Step 6 → (Optional) Re-hydrate placeholders in the answer for the authorised user
Step 7 → Log counts of entities, never the values
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Detect: structured PII के लिए regex (phone, email, PAN, Aadhaar, card + Luhn)
Step 2 → Detect: नाम, पते, orgs के लिए NER model (Microsoft Presidio, spaCy)
Step 3 → Overlaps सुलझाओ, entity types और scores दो
Step 4 → बदलो: mask ([PHONE]) या tokenise (<PHONE_1>) private mapping के साथ
Step 5 → Redacted text LLM को भेजो
Step 6 → (Optional) अधिकृत user के लिए answer में placeholders वापस भरो
Step 7 → Entities की गिनती log करो, values कभी नहीं
```

---

## 🟡 Real World Example
**Tariff Classification System**: An importer pastes "Invoice for Rahul Verma, PAN ABCDE1234F, phone 9876543210, 500 cotton t-shirts". The guard turns it into "Invoice for <PERSON_1>, PAN <PAN_1>, phone <PHONE_1>, 500 cotton t-shirts". The LLM classifies the goods; the final report restores the real values only in the importer's own PDF.

**Zomato AI**: Chat logs saved for analytics replace delivery addresses and phone numbers with tokens.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer paste करता है "Invoice for Rahul Verma, PAN ABCDE1234F, phone 9876543210, 500 cotton t-shirts"। Guard इसे बनाता है "Invoice for <PERSON_1>, PAN <PAN_1>, phone <PHONE_1>, 500 cotton t-shirts"। LLM माल को classify करता है; final report में असली values सिर्फ importer के अपने PDF में वापस भरी जाती हैं।

**Zomato AI**: Analytics के लिए सेव chat logs में delivery addresses और फोन नंबर tokens से बदल दिए जाते हैं।

---

## 💻 Code Example — Basic
```python
# Basic PII redaction with regex - pure Python, runs directly
import re  # regex

PATTERNS: dict[str, re.Pattern[str]] = {
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    "PHONE": re.compile(r"\b(?:\+91[- ]?)?[6-9]\d{9}\b"),  # Indian mobile
    "PAN": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),  # Indian PAN
    "AADHAAR": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),  # 12 digits
}


def redact(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    for label, pat in PATTERNS.items():  # apply each pattern
        text, n = pat.subn(f"[{label}]", text)  # replace and count
        if n:
            counts[label] = n
    return text, counts


msg = "Mail rahul@example.com, phone 9876543210, PAN ABCDE1234F for 500 t-shirts"
print(redact(msg))
```

## 💻 Code Example — Advanced
```python
# Production: reversible tokenisation with Presidio-style flow, async wrapper, error handling.
# Regex part runs anywhere; the optional Presidio part needs: pip install presidio-analyzer
# presidio-anonymizer spacy (and a spaCy model). It is guarded by try/except import.
import asyncio  # async runtime
import logging  # logs
import re  # regex
from dataclasses import dataclass, field  # records

log = logging.getLogger("pii")

try:  # optional dependency
    from presidio_analyzer import AnalyzerEngine  # NER + patterns

    _analyzer: "AnalyzerEngine | None" = AnalyzerEngine()
except Exception:  # not installed or model missing
    _analyzer = None

REGEX = {
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    "PHONE": re.compile(r"\b[6-9]\d{9}\b"),
    "PAN": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
}


@dataclass
class Redacted:
    text: str  # safe text for the LLM
    mapping: dict[str, str] = field(default_factory=dict)  # token -> original (keep server side)


def tokenise(text: str) -> Redacted:
    mapping: dict[str, str] = {}
    counters: dict[str, int] = {}
    spans: list[tuple[int, int, str]] = []  # (start, end, label)
    for label, pat in REGEX.items():
        spans += [(m.start(), m.end(), label) for m in pat.finditer(text)]
    if _analyzer is not None:  # add names and locations
        for r in _analyzer.analyze(text=text, language="en", entities=["PERSON", "LOCATION"]):
            spans.append((r.start, r.end, r.entity_type))
    spans.sort(key=lambda s: (s[0], -s[1]))  # earliest first, longest first
    out: list[str] = []
    pos = 0
    for start, end, label in spans:
        if start < pos:
            continue  # overlapping span already handled
        counters[label] = counters.get(label, 0) + 1
        token = f"<{label}_{counters[label]}>"
        mapping[token] = text[start:end]
        out.append(text[pos:start])
        out.append(token)
        pos = end
    out.append(text[pos:])
    return Redacted("".join(out), mapping)


def rehydrate(answer: str, mapping: dict[str, str]) -> str:
    for token, original in mapping.items():
        answer = answer.replace(token, original)  # restore for authorised viewer
    return answer


async def safe_llm_call(text: str) -> str:
    try:
        red = await asyncio.to_thread(tokenise, text)  # CPU work off the event loop
    except Exception as exc:
        log.exception("redaction failed")  # fail closed: do not send raw text
        raise RuntimeError("redaction failed") from exc
    answer = f"Classified goods for {red.text}"  # replace with the real LLM call
    return rehydrate(answer, red.mapping)


if __name__ == "__main__":
    print(asyncio.run(safe_llm_call("PAN ABCDE1234F phone 9876543210 buys t-shirts")))
```

---

## 🟠 FastAPI Integration
```python
import asyncio  # to_thread
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()


class Req(BaseModel):
    text: str  # user text possibly with PII


@app.post("/classify")
async def classify(body: Req) -> dict[str, object]:
    red = await asyncio.to_thread(tokenise, body.text)  # redact before anything else
    log.info("pii_tokens=%d", len(red.mapping))  # log counts only
    llm_answer = f"HS 6109.10 for: {red.text}"  # LLM call with red.text
    return {"answer": rehydrate(llm_answer, red.mapping)}
```

---

## 🔗 LangChain / LangGraph Connection
Add redaction as the first step: `RunnableLambda(lambda t: tokenise(t).text)`. LangChain also ships PII middleware in recent versions; check your installed version's docs. In LangGraph keep the `mapping` in state (server side only) and rehydrate in the final node.

```python
from langchain_core.runnables import RunnableLambda  # wrapper

redact_step = RunnableLambda(lambda t: tokenise(t).text)  # text -> redacted text
# chain = redact_step | prompt | llm | parser
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Redacting only the prompt but logging raw input
✅ Correct: Redact at the edge before logs, caches and vector stores.

```python
# Wrong
log.info(raw_text)
# Right
log.info(redact(raw_text)[0])
```

❌ Mistake 2: Regex only for names and addresses
✅ Correct: Use an NER model (Presidio/spaCy) for free-form entities.

```python
# Wrong
re.sub(r"[A-Z][a-z]+ [A-Z][a-z]+", "[NAME]", text)   # also hits "Cotton Shirts"
# Right
analyzer.analyze(text=text, entities=["PERSON"], language="en")
```

---

## 🧠 Tricky Interview Question
**Q**: "You redact names, but the LLM answer needs the customer's name in the email draft. How?"

**Answer**: Use reversible tokenisation. The LLM sees `<PERSON_1>` and writes "Dear <PERSON_1>"; your server swaps the token back after the call. The mapping never leaves your system. Do not put the mapping in the prompt, cache or third-party logs.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is PII?
A1: Information that can identify a person, like phone, email, PAN or address.

Q2: [Easy] Mask vs tokenise?
A2: Mask replaces with a fixed label ([PHONE]) and is irreversible. Tokenise uses unique tokens with a private mapping, so it can be reversed.

Q3: [Medium] Why is regex not enough?
A3: It handles structured IDs well but misses names, addresses and context-dependent data. Combine with NER.

Q4: [Medium] What is Luhn check used for?
A4: Validating card numbers to cut false positives for 16-digit strings.

Q5: [Hard] How do you measure PII detection quality?
A5: Build a labelled dataset in your languages (English, Hindi, Hinglish), measure recall first (missed PII is the risk) and precision (over-redaction hurts usefulness), per entity type, and re-test after every rule or model change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Sending user data to third-party LLMs
- Logging, caching or indexing conversations

❌ Avoid when:
- Fully on-prem model with strict access controls and no logging (still minimise)

---

## 📊 Visual Diagram
```
"Rahul, PAN ABCDE1234F, 9876543210"
        │ detect (regex + NER)
        ▼
"<PERSON_1>, PAN <PAN_1>, <PHONE_1>"  ──► LLM / logs / cache
        │
 mapping (server only) ──► rehydrate final answer for authorised user
```

---

## 💰 Cost Impact
Regex and Presidio run locally: no token cost, small CPU cost (a few ms per message). Placeholders are short, so tokens are similar or slightly fewer than raw values. Avoid using an LLM to find PII on every message: a 500-token pass costs about $0.00008 on gpt-4o-mini, i.e. about $80 per 1M messages. Optimise with local detection first, and LLM detection only for uncertain text.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PII | Personal identifying data | व्यक्तिगत पहचान वाला डेटा |
| Redaction | Hide sensitive text | संवेदनशील text छुपाना |
| Tokenisation | Reversible replacement | उलटा जा सकने वाला बदलाव |
| NER | Named entity recognition | नाम/स्थान पहचानना |
| Presidio | Microsoft PII toolkit | Microsoft का PII toolkit |
| DPDP Act | India data protection law | भारत का डेटा संरक्षण कानून |

---

## ⚡ 3-Line Summary
English: Detect PII with regex plus NER, then mask or tokenise it before the LLM, logs and caches. Keep the mapping on your server and restore values only for authorised users. Measure recall.
Hindi: Regex और NER से PII खोजो, फिर LLM, logs और caches से पहले उसे mask या tokenise करो। Mapping अपने server पर रखो और values सिर्फ अधिकृत users के लिए वापस भरो। Recall मापो।

---

## ➡️ Next Topic
**473. Toxic Content Detection** - the other content-safety check: harmful or abusive language.
