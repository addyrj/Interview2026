---

# 538. Design: Medical AI System
# हिंदी में: Medical AI System का Design

---

## 🔵 Simple Definition (English)
A medical AI system is a clinical decision-support assistant: it summarizes patient records, answers questions from medical guidelines with citations, and flags risks for a clinician. It supports doctors; it does not diagnose or prescribe on its own. Privacy, safety and traceability come before everything else.

## 🔵 सरल परिभाषा (Hindi)
Medical AI system एक clinical decision-support assistant है: यह patient records का summary बनाता है, medical guidelines से citations के साथ सवालों के जवाब देता है और clinician को जोखिम बताता है। यह खुद diagnose या prescribe नहीं करता। Privacy, safety और traceability सबसे ऊपर हैं।

---

## 🔴 Problem it Solves
Doctors lose hours on documentation and searching guidelines. Records are long and scattered. But a wrong or invented medical answer can harm a patient, and patient data is legally protected (HIPAA in the US, DPDP Act in India, GDPR in the EU). A generic chatbot is unsafe here.

## 🔴 यह क्यों बना? (Hindi)
Doctors का बहुत समय documentation और guidelines खोजने में जाता है। Records लंबे और बिखरे होते हैं। लेकिन गलत या गढ़ा हुआ medical जवाब मरीज को नुकसान पहुँचा सकता है, और patient data कानूनन सुरक्षित है (US में HIPAA, भारत में DPDP Act, EU में GDPR)। आम chatbot यहाँ असुरक्षित है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Clinician logs in (SSO + role); every request carries user, patient, purpose
Step 2 → Access check: is this clinician allowed to see THIS patient (consent, care team)?
Step 3 → De-identify / minimise data sent to the model (only needed fields)
Step 4 → Retrieve from approved sources only: hospital guidelines, drug database, patient notes
Step 5 → LLM drafts answer strictly from retrieved text, with citations
Step 6 → Safety layer: dosage/contraindication rule checks, emergency red flags, "not found" path
Step 7 → Show to clinician as a DRAFT with sources; clinician accepts/edits
Step 8 → Immutable audit log; model and prompt versions recorded; outcomes monitored
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Clinician login (SSO + role); हर request में user, patient, purpose
Step 2 → Access check: क्या इस clinician को इस patient का data देखने की अनुमति है?
Step 3 → Model को भेजा जाने वाला data de-identify / minimise करो
Step 4 → सिर्फ approved sources से retrieve: guidelines, drug database, patient notes
Step 5 → LLM सिर्फ retrieved text से, citations के साथ draft लिखता है
Step 6 → Safety layer: dosage/contraindication rules, emergency red flags, "not found" path
Step 7 → Clinician को DRAFT के रूप में sources के साथ दिखाओ; वह accept/edit करे
Step 8 → Immutable audit log; model और prompt versions दर्ज; outcomes की निगरानी
```

---

## 🟡 Real World Example
**Tariff Classification System**: The same pattern applies as for regulated decisions: grounded retrieval, validator, human review, audit log. Medical raises the bar; the "human review" is mandatory, not for low confidence only.
**Medical example**: A doctor asks "summarize this patient's last 5 visits and flag drug interactions with warfarin." The system lists visits with citations and a rule engine (not the LLM) checks interactions from a drug database. The doctor decides.

## 🟡 Real Example Hindi mein
**Tariff System**: Regulated फैसलों के लिए यही pattern: grounded retrieval, validator, human review, audit log। Medical में standard और ऊँचा है; यहाँ human review हमेशा ज़रूरी है, सिर्फ low confidence पर नहीं।
**Medical example**: Doctor पूछता है "इस patient की पिछली 5 visits का summary दो और warfarin के साथ drug interactions बताओ।" System visits को citations के साथ list करता है और interactions drug database से rule engine (LLM नहीं) जाँचता है। फैसला doctor लेता है।

---

## 💻 Code Example — Basic
```python
# Basic: mask personal identifiers before sending text to any model (pure Python)
import re                                              # regex for patterns

PATTERNS: dict[str, str] = {                           # simple illustrative patterns
    "PHONE": r"\b\d{10}\b",                            # 10 digit phone
    "EMAIL": r"[\w.+-]+@[\w-]+\.[\w.]+",               # email address
    "MRN": r"\bMRN-\d{6}\b",                           # medical record number format (example)
}


def deidentify(text: str) -> str:
    """Replace identifiers with placeholders."""
    for label, pat in PATTERNS.items():                # loop patterns
        text = re.sub(pat, f"[{label}]", text)         # replace each match
    return text                                        # cleaned text


note = "Patient MRN-123456, phone 9876543210, email a@b.com, on warfarin 5mg."   # sample note
print(deidentify(note))                                # show masked note
# Note: regex alone is NOT enough for real PHI; use a validated de-identification tool.
```

## 💻 Code Example — Advanced
```python
# Production style: authorised, grounded answer with rule check, draft status, audit
import asyncio                                         # async
import json                                            # audit serialisation
import time                                            # timestamps
from dataclasses import dataclass, field               # data classes

CARE_TEAM: dict[str, set[str]] = {"dr_rao": {"p1", "p2"}}   # who may see which patient (from IAM in prod)
INTERACTIONS: dict[frozenset, str] = {frozenset({"warfarin", "aspirin"}): "increased bleeding risk"}   # sample rule base


@dataclass
class Draft:
    text: str                                          # model draft
    sources: list[str]                                 # citations
    warnings: list[str] = field(default_factory=list)  # rule-engine warnings
    status: str = "DRAFT_FOR_CLINICIAN_REVIEW"         # never final


def authorised(user: str, patient: str) -> bool:
    return patient in CARE_TEAM.get(user, set())       # deny by default


def check_interactions(meds: list[str]) -> list[str]:
    """Deterministic safety rule, not LLM."""
    found: list[str] = []                              # warnings
    for i, a in enumerate(meds):                       # pairwise check
        for b in meds[i + 1:]:
            msg = INTERACTIONS.get(frozenset({a.lower(), b.lower()}))   # lookup
            if msg:
                found.append(f"{a}+{b}: {msg}")        # add warning
    return found


async def answer(user: str, patient: str, question: str, meds: list[str], llm, retriever) -> Draft:
    """Authorise, retrieve, draft, check, audit."""
    if not authorised(user, patient):                  # access control first
        raise PermissionError("not on care team")
    try:
        passages = await asyncio.wait_for(retriever(question, patient), timeout=5)   # approved sources only
        if not passages:                               # nothing to ground on
            return Draft("No supporting information found.", [])
        text = await asyncio.wait_for(llm(question, passages), timeout=30)   # grounded draft
    except asyncio.TimeoutError:
        return Draft("System timeout. Please use standard references.", [])
    d = Draft(text, [p["id"] for p in passages], check_interactions(meds))   # assemble
    print(json.dumps({"ts": time.time(), "user": user, "patient": patient, "sources": d.sources}))   # audit (use secure store)
    return d
```

---

## 🟠 FastAPI Integration
Use authentication, role-based dependencies, TLS, and never log raw PHI. Return the status "draft" in every response.

```python
from fastapi import FastAPI, Depends, HTTPException    # FastAPI
from pydantic import BaseModel                         # models

app = FastAPI()                                        # app


class Ask(BaseModel):
    patient_id: str                                    # patient reference
    question: str                                      # clinician question


async def clinician() -> str:
    return "dr_rao"                                    # stub: verify JWT + role in prod


@app.post("/clinical/ask")
async def ask(body: Ask, user: str = Depends(clinician)) -> dict:
    if body.patient_id not in {"p1", "p2"}:            # stub access rule
        raise HTTPException(403, "no access to this patient")   # deny
    return {"status": "DRAFT_FOR_CLINICIAN_REVIEW", "answer": "stub", "sources": []}   # stub
```

---

## 🔗 LangChain / LangGraph Connection
A LangGraph flow: `authorize` -> `retrieve` -> `draft` -> `safety_rules` -> `human_review` (using `interrupt`) -> `finalize`. Checkpointing gives a full trace of state per step, which helps audits. Use a self-hosted or compliant model endpoint if the policy forbids sending PHI to external providers.

```python
# LangGraph human-in-the-loop idea (illustrative; check current docs for interrupt API)
# graph.add_node("human_review", human_review_node)    # pauses until clinician approves
# app = graph.compile(checkpointer=checkpointer)       # persist state per thread
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sending identifiable records to an external API without agreements
✅ Correct: minimise or de-identify, use a provider with a signed business associate agreement or a self-hosted model.

```python
# Wrong: prompt = f"Patient {name}, phone {phone}: ..."
# Right: prompt = f"Patient [ID_1]: ..." with a secure mapping kept inside the hospital system
```

❌ Mistake 2: Using the LLM for dosage math or interaction checks
✅ Correct: deterministic rule engines and validated drug databases.

❌ Mistake 3: Presenting output as a final answer
✅ Correct: clearly mark as draft, show sources, require clinician sign-off.

---

## 🧠 Tricky Interview Question
**Q**: "The model summary omits a patient's penicillin allergy that was in an old scanned note. Who is responsible and how do you prevent it?"

**Answer**: The clinician stays responsible, but the system must reduce the risk. Allergies are critical structured data: do not rely on free-text summarisation. Pull them from the structured allergy list, run OCR on scans, always display an allergy banner from the source of truth outside the LLM summary, and test recall on safety-critical fields with a dedicated eval. Report such misses as incidents and add them to regression tests.

---

## ⚫ Interview Questions + Answers

Q1: Why is "human in the loop" mandatory here?
A1: Errors can harm patients and the law expects accountable clinicians. The AI is decision support.

Q2: What is PHI?
A2: Protected Health Information: any health data that identifies a person. It needs encryption, access control and auditing.

Q3: How do you reduce hallucination in medical answers?
A3: Retrieve from approved sources, force citations, allow "not found", use deterministic checks for critical facts, and evaluate with clinician-labelled sets.

Q4: How do you evaluate a medical assistant?
A4: Expert-reviewed test cases, faithfulness to sources, recall on critical fields (allergies, meds), harm-focused red teaming, and monitoring after launch.

Q5: (Hard) Design for compliance and data residency.
A5: Keep data in the required region, encrypt at rest and in transit, role-based and purpose-based access, consent tracking, minimal data to the model, no training on patient data without consent, immutable audit logs, vendor agreements, retention and deletion policies, and incident response. Consult legal and regulatory experts; software that influences treatment may count as a regulated medical device.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Summarising notes, drafting documents, searching guidelines with a clinician reviewing

❌ Avoid when:
- Autonomous diagnosis, prescribing or triage without clinician oversight
- No approved knowledge sources or compliant infrastructure

---

## 📊 Visual Diagram
```
 Clinician ─▶ SSO/RBAC ─▶ Access check (care team, consent)
                              │
                       minimise / de-identify
                              │
        Approved sources ─▶ Retrieval ─▶ LLM draft (cited)
                              │
                 Rule engine (interactions, dosage)
                              │
                    DRAFT ─▶ Clinician review ─▶ record
                              │
                      Immutable audit log
```

---

## 💰 Cost Impact
Costs rise because of mandatory extras: longer prompts (patient context), citations, safety checks, audit storage, and possibly self-hosted GPUs for privacy. A summary of five visits may be 5-15k input tokens (illustrative).
Optimize: summarise records once and cache (invalidate on new notes), retrieve only relevant sections, use small models for extraction and larger ones for drafting, and keep rule checks outside the LLM (cheap and deterministic).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PHI | Identifiable health data | पहचान वाला स्वास्थ्य data |
| De-identification | Removing identifiers | पहचान हटाना |
| Decision support | Helps, does not decide | निर्णय में सहायता |
| RBAC | Role-based access control | भूमिका आधारित access |
| Audit trail | Tamper-proof usage record | छेड़छाड़-रहित उपयोग रिकॉर्ड |
| Contraindication | Reason not to use a treatment | इलाज न करने का कारण |

---

## ⚡ 3-Line Summary
English: Medical AI is clinician decision support with strict access control and privacy. Ground every answer in approved sources and use rules for critical checks. Always keep a human sign-off and an audit log.
Hindi: Medical AI सख्त access control और privacy वाला clinician decision support है। हर जवाब approved sources पर आधारित हो और critical checks rules से हों। Human sign-off और audit log हमेशा रखो।

---

## ➡️ Next Topic
**539. Design: Legal AI System**: contracts and case law, where citations and clause-level accuracy matter most.
