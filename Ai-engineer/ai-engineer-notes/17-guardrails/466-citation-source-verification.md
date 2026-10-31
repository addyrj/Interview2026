---

# 466. Citation + Source Verification
# हिंदी में: Citation और Source की जाँच

---

## 🔵 Simple Definition (English)
Citation verification checks that every source an LLM cites (1) exists, (2) was actually retrieved for this request, and (3) really supports the claim. Source verification also checks that the source itself is trusted, current and not tampered with.

## 🔵 सरल परिभाषा (Hindi)
Citation verification जाँचता है कि LLM जो source cite करता है वह (1) मौजूद है, (2) इसी request के लिए retrieve हुआ था, और (3) सच में claim को support करता है। Source verification यह भी देखता है कि source खुद भरोसेमंद, ताज़ा और बिना छेड़छाड़ का है।

---

## 🔴 Problem it Solves
LLMs invent citations: fake case numbers, fake circulars, real ids that do not support the claim. A fake citation is worse than none because it creates false trust. Verification removes fake or mismatched citations before the user sees them.

## 🔴 यह क्यों बना? (Hindi)
LLMs citations गढ़ लेते हैं: नकली case numbers, नकली circulars, या असली ids जो claim को support नहीं करते। नकली citation बिना citation से बुरा है क्योंकि वह झूठा भरोसा बनाता है। Verification user को दिखने से पहले नकली या बेमेल citations हटा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parse citations from the answer ([S2], URLs, circular numbers)
Step 2 → Existence: is the id in this request's retrieved set?
Step 3 → Registry: is the document in the trusted catalogue (not user-uploaded junk)?
Step 4 → Freshness: is the document version/date still in force?
Step 5 → Support: does the cited text entail the claim? (quote match, NLI, judge)
Step 6 → Remove or flag failures; recompute coverage
Step 7 → Return answer + verified source list + verification report
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Answer से citations निकालो ([S2], URLs, circular numbers)
Step 2 → Existence: क्या id इसी request के retrieved set में है?
Step 3 → Registry: क्या document trusted catalogue में है (user-uploaded कचरा नहीं)?
Step 4 → Freshness: क्या document version/date अभी लागू है?
Step 5 → Support: क्या cited text claim को support करता है? (quote match, NLI, judge)
Step 6 → Fail होने वाले हटाओ या flag करो; coverage दोबारा निकालो
Step 7 → Answer + verified source list + verification report लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: The answer cites "Notification 12/2025-Customs". Verification: it is not in the retrieved set and not in the notification registry, so it is removed and the sentence is marked unverified. Another claim cites a real notification that was superseded last month; the freshness check flags it as outdated and shows the newer one.

**Amazon AI**: A review summary quoting "customers say battery lasts 2 days" must link to actual review ids, and each must contain that text.

## 🟡 Real Example Hindi mein
**Tariff System**: Answer "Notification 12/2025-Customs" cite करता है। Verification: यह न retrieved set में है न notification registry में, इसलिए हटा दिया जाता है और वाक्य unverified चिह्नित होता है। दूसरा claim एक असली notification cite करता है जो पिछले महीने supersede हो चुकी है; freshness check उसे outdated flag करता है और नई notification दिखाता है।

**Amazon AI**: Review summary "ग्राहक कहते हैं battery 2 दिन चलती है" को असली review ids से जोड़ा जाना चाहिए और हर review में वह text होना चाहिए।

---

## 💻 Code Example — Basic
```python
# Basic: existence + quote verification - pure Python, runs directly
RETRIEVED: dict[str, str] = {
    "S1": "Cotton t-shirts are classified under HS 6109.10.",
    "S2": "Basic customs duty on HS 6109.10 is 10 percent.",
}


def verify(citation_id: str, quote: str) -> str:
    text = RETRIEVED.get(citation_id)  # was it retrieved for this request?
    if text is None:
        return "FAKE_ID"  # model invented the id
    if quote.lower() not in text.lower():  # quote must appear verbatim
        return "QUOTE_NOT_FOUND"  # id is real but evidence is not
    return "OK"


print(verify("S2", "duty on HS 6109.10 is 10 percent"))  # OK
print(verify("S9", "anything"))  # FAKE_ID
print(verify("S1", "duty is 5 percent"))  # QUOTE_NOT_FOUND
```

## 💻 Code Example — Advanced
```python
# Production: registry + freshness + entailment judge with async batch and error handling
import asyncio  # concurrency
import json  # JSON parse
import os  # env
from dataclasses import dataclass  # records
from datetime import date  # freshness
from typing import Literal  # status type

Status = Literal["ok", "fake", "stale", "unsupported", "untrusted"]


@dataclass
class Doc:
    sid: str
    text: str
    trusted: bool  # from the official catalogue
    valid_until: date  # when the rule expires


@dataclass
class Citation:
    sid: str  # cited id
    claim: str  # sentence it supports


async def supports(claim: str, text: str) -> bool:
    if not os.getenv("OPENAI_API_KEY"):  # offline: crude overlap
        cw = set(claim.lower().split())
        return len(cw & set(text.lower().split())) / max(len(cw), 1) >= 0.5
    from openai import AsyncOpenAI

    client = AsyncOpenAI()
    try:
        r = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=10,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content":
                       f'Does SOURCE fully support CLAIM? JSON {{"supported": true|false}}\n'
                       f"SOURCE: {text}\nCLAIM: {claim}"}],
        )
        return bool(json.loads(r.choices[0].message.content or "{}").get("supported"))
    except Exception:
        return False  # fail closed


async def verify_one(c: Citation, docs: dict[str, Doc], today: date) -> Status:
    doc = docs.get(c.sid)
    if doc is None:
        return "fake"  # not retrieved
    if not doc.trusted:
        return "untrusted"  # not in catalogue
    if doc.valid_until < today:
        return "stale"  # expired rule
    return "ok" if await supports(c.claim, doc.text) else "unsupported"


async def verify_all(cites: list[Citation], docs: dict[str, Doc]) -> list[tuple[str, Status]]:
    today = date.today()
    results = await asyncio.gather(*[verify_one(c, docs, today) for c in cites])  # parallel
    return [(c.sid, s) for c, s in zip(cites, results)]


if __name__ == "__main__":
    docs = {"S2": Doc("S2", "Basic duty on HS 6109.10 is 10 percent", True, date(2030, 1, 1))}
    cites = [Citation("S2", "Duty on 6109.10 is 10 percent"), Citation("S7", "Some rule")]
    print(asyncio.run(verify_all(cites, docs)))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()


class VerifyReq(BaseModel):
    citations: list[dict[str, str]]  # [{"sid": "S2", "claim": "..."}]


@app.post("/verify-citations")
async def verify_route(body: VerifyReq) -> dict[str, object]:
    docs = {"S2": Doc("S2", "Basic duty on HS 6109.10 is 10 percent", True, date(2030, 1, 1))}  # from retriever
    cites = [Citation(c["sid"], c["claim"]) for c in body.citations]  # build objects
    results = await verify_all(cites, docs)  # run checks
    bad = [r for r in results if r[1] != "ok"]  # failures
    return {"results": results, "all_verified": not bad}
```

---

## 🔗 LangChain / LangGraph Connection
Use `create_stuff_documents_chain` or custom prompts so each `Document` carries metadata ids; after generation, a LangGraph `verify_citations` node reads `state["documents"]` and `state["answer"]`. If failures exist, route to `regenerate` once, otherwise strip the bad sentences.

```python
# state = {"documents": [...], "answer": "...", "report": []}
# graph: retrieve -> generate -> verify_citations -> (all ok ? END : regenerate)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Checking only that the id exists
✅ Correct: Also check support.

```python
# Wrong
ok = cited_id in docs
# Right
ok = cited_id in docs and await supports(claim, docs[cited_id].text)
```

❌ Mistake 2: Trusting URLs the model writes
✅ Correct: Only render URLs from your own retrieved metadata.

```python
# Wrong
link = model_output_url
# Right
link = docs[sid].url
```

---

## 🧠 Tricky Interview Question
**Q**: "A user uploads a PDF containing 'Official notice: duty on all goods is 0%'. Your RAG cites it. What is the risk?"

**Answer**: Source poisoning / indirect prompt injection. The citation exists and "supports" the claim, yet the source is untrusted. Keep a trust level per source (official catalogue vs user upload), never mix them in the same context for authoritative answers, and show trust labels in the UI.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is a fake citation?
A1: A reference the model made up, such as an id or document that does not exist.

Q2: [Easy] Why verify citations?
A2: To keep trust: users rely on citations to check answers.

Q3: [Medium] Three levels of citation checking?
A3: Existence, trust and freshness, and claim support.

Q4: [Medium] How do quote-match checks work?
A4: Require the model to output a verbatim quote and check it is a substring (normalized) of the source.

Q5: [Hard] How do you verify at scale cheaply?
A5: Deterministic checks first (id, registry, date, substring), then a small NLI model or cheap judge only for the remainder, batch claims, cache by (claim hash, source hash), and sample for human audit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Legal, medical, finance, customs answers
- Users click citations to verify

❌ Avoid when:
- Casual chat without sources
- Latency-critical flows with no stakes (do sampled checks)

---

## 📊 Visual Diagram
```
Answer + citations
      │
      ├─ exists in retrieved set? ──no──► FAKE
      ├─ in trusted catalogue?    ──no──► UNTRUSTED
      ├─ still valid (date)?      ──no──► STALE
      └─ source supports claim?   ──no──► UNSUPPORTED
                 │yes
                 ▼
             VERIFIED ─► shown to user
```

---

## 💰 Cost Impact
Steps 1-4 are free code. Step 5 judge: about 250 tokens per citation, 4 citations ≈ 1,000 tokens ≈ $0.00015 on gpt-4o-mini. At 500K answers/month about $75 if you check everything. Optimise: only judge claims that failed substring match, cache by hashes, and sample low-risk traffic.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Citation | Reference to source | source का हवाला |
| Entailment | Source implies claim | source से claim सिद्ध |
| Source poisoning | Malicious content in sources | source में दुर्भावनापूर्ण content |
| Registry | List of trusted docs | भरोसेमंद documents की सूची |
| Staleness | Outdated source | पुराना source |
| Verbatim quote | Exact text copy | शब्दशः उद्धरण |

---

## ⚡ 3-Line Summary
English: Verify that citations exist, come from trusted current sources and truly support the claim. Use cheap deterministic checks first, then a judge. Never render model-written URLs.
Hindi: Verify करो कि citations मौजूद हैं, भरोसेमंद ताज़ा sources से हैं और claim को सच में support करते हैं। पहले सस्ते deterministic checks, फिर judge। Model के लिखे URLs कभी मत दिखाओ।

---

## ➡️ Next Topic
**467. Fact Checking in RAG** - going beyond citations to check the facts of the whole answer.
