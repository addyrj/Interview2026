---

# 539. Design: Legal AI System
# हिंदी में: Legal AI System का Design

---

## 🔵 Simple Definition (English)
A legal AI system helps lawyers review contracts, extract clauses, compare them to a playbook, and research case law with exact citations. Accuracy at the clause level and verifiable sources matter more than fluent text. A lawyer reviews all output.

## 🔵 सरल परिभाषा (Hindi)
Legal AI system वकीलों को contracts review करने, clauses निकालने, उन्हें playbook से मिलाने और case law को exact citations के साथ खोजने में मदद करता है। यहाँ clause-level accuracy और जाँचे जा सकने वाले sources, सुंदर भाषा से ज़्यादा ज़रूरी हैं। हर output को वकील देखता है।

---

## 🔴 Problem it Solves
Contract review is slow and repetitive: finding termination, liability, and indemnity clauses across hundreds of pages. Mistakes are costly. LLMs have also been known to invent case citations that do not exist, which has embarrassed lawyers in court. So we need grounding, quotes, and verification.

## 🔴 यह क्यों बना? (Hindi)
Contract review धीमा और दोहराव वाला है: सैकड़ों पेज में termination, liability और indemnity clauses खोजना। गलतियाँ महँगी पड़ती हैं। LLMs ने ऐसे case citations भी गढ़े हैं जो मौजूद ही नहीं थे, जिससे वकील अदालत में शर्मिंदा हुए। इसलिए grounding, सटीक quotes और verification चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Upload contract (PDF/DOCX), OCR if scanned, keep page + paragraph offsets
Step 2 → Structure-aware parsing: split by section/clause numbering, not fixed size
Step 3 → Clause extraction: LLM returns {type, exact_quote, page} per clause
Step 4 → Quote verification: check that exact_quote appears verbatim in the source text
Step 5 → Playbook comparison: rules like "liability cap >= 12 months fees" -> risk flags
Step 6 → Research mode: retrieve from a trusted case-law index; cite id, court, year
Step 7 → Citation check: every cited case must exist in the index; else drop it
Step 8 → Lawyer reviews highlights and edits; matter-level access control and audit log
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Contract upload, scan हो तो OCR, page + paragraph offsets रखो
Step 2 → Structure-aware parsing: section/clause numbering से बाँटो, fixed size से नहीं
Step 3 → Clause extraction: LLM हर clause के लिए {type, exact_quote, page} देता है
Step 4 → Quote verification: exact_quote source text में शब्दशः है या नहीं जाँचो
Step 5 → Playbook comparison: "liability cap >= 12 महीने की fees" जैसे rules से risk flags
Step 6 → Research mode: भरोसेमंद case-law index से retrieve; id, court, year के साथ cite
Step 7 → Citation check: हर cited case index में होना चाहिए, वरना हटाओ
Step 8 → वकील highlights देखकर edit करता है; matter-level access control और audit log
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs law has binding rulings and appeals. When an importer disputes a code, a legal assistant retrieves prior rulings and chapter notes, quotes the exact wording, and drafts an argument, with each citation verified against the ruling database.
**Contract example**: An NDA review flags "no cap on liability" in clause 9.2 with the quoted text and page 7, and suggests the playbook's fallback wording.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs law में binding rulings और appeals होते हैं। Importer किसी code पर विवाद करे तो legal assistant पुराने rulings और chapter notes लाता है, exact शब्द quote करता है और argument का draft बनाता है, हर citation ruling database से verify होता है।
**Contract example**: NDA review में clause 9.2 का "liability पर कोई cap नहीं" quote और page 7 के साथ flag होता है, और playbook का fallback wording सुझाया जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: find clauses by heading and verify a quote exists verbatim (pure Python)
import re                                              # regex for clause numbers

CONTRACT = """1. Term. This agreement lasts two years.
2. Termination. Either party may terminate with 30 days written notice.
3. Liability. Liability is capped at fees paid in the prior 12 months."""   # sample text


def split_clauses(text: str) -> dict[str, str]:
    """Return {heading: body} using 'N. Heading.' pattern."""
    out: dict[str, str] = {}                           # result
    for m in re.finditer(r"(\d+)\.\s+([A-Za-z ]+)\.\s+(.*)", text):   # each clause line
        out[m.group(2).strip()] = m.group(3).strip()   # heading -> body
    return out                                         # done


def quote_is_verbatim(quote: str, source: str) -> bool:
    """Anti-hallucination check: quote must appear exactly."""
    return quote in source                             # exact substring test


clauses = split_clauses(CONTRACT)                      # parse
print(list(clauses))                                   # headings found
print(quote_is_verbatim("terminate with 30 days written notice", CONTRACT))   # True
print(quote_is_verbatim("terminate with 60 days notice", CONTRACT))           # False: model invention
```

## 💻 Code Example — Advanced
```python
# Production style: async clause extraction with verbatim verification and playbook rules
import asyncio                                         # async
import json                                            # parse model JSON
import re                                              # number extraction
from pydantic import BaseModel, ValidationError        # schema validation


class Clause(BaseModel):
    type: str                                          # e.g. "liability_cap"
    quote: str                                         # exact text from the contract
    page: int                                          # page number


def normalise(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()      # ignore whitespace/case differences


async def extract(contract_text: str, llm) -> list[Clause]:
    """Ask the LLM for clauses, keep only verified ones."""
    prompt = ('Extract termination and liability clauses. JSON list of {"type","quote","page"}. '
              "Quote text EXACTLY from the contract.\n\n" + contract_text)   # instruction
    try:
        raw = await asyncio.wait_for(llm(prompt), timeout=60)   # bounded call
        items = json.loads(raw)                        # parse JSON
    except (asyncio.TimeoutError, json.JSONDecodeError):
        return []                                      # fail closed
    src = normalise(contract_text)                     # normalised source
    verified: list[Clause] = []                        # accepted clauses
    for item in items:
        try:
            c = Clause(**item)                         # validate shape
        except ValidationError:
            continue                                   # skip malformed
        if normalise(c.quote) in src:                  # verbatim check
            verified.append(c)                         # keep
    return verified


def playbook_flags(clauses: list[Clause], max_notice_days: int = 60) -> list[str]:
    """Deterministic rules that produce risk flags."""
    flags: list[str] = []                              # output
    types = {c.type for c in clauses}                  # clause types found
    if "liability_cap" not in types:                   # missing cap
        flags.append("HIGH: no liability cap found")
    for c in clauses:
        if c.type == "termination":                    # check notice period
            m = re.search(r"(\d+)\s+days", c.quote)    # find days
            if m and int(m.group(1)) > max_notice_days:
                flags.append(f"MEDIUM: long notice ({m.group(1)} days), p.{c.page}")
    return flags
```

---

## 🟠 FastAPI Integration
Contracts are confidential. Use per-matter access control, encrypted storage, and no logging of contract text.

```python
from fastapi import FastAPI, UploadFile, HTTPException, Depends   # FastAPI

app = FastAPI()                                        # app


async def lawyer_on_matter(matter_id: str) -> str:
    if matter_id not in {"m1"}:                        # stub ACL
        raise HTTPException(403, "no access to matter")
    return "lawyer_1"                                  # stub user


@app.post("/matters/{matter_id}/review")
async def review(matter_id: str, file: UploadFile, user: str = Depends(lawyer_on_matter)) -> dict:
    if file.content_type != "application/pdf":         # validate type
        raise HTTPException(415, "PDF only")
    data = await file.read()                           # read bytes
    # clauses = await extract(parse(data), llm); flags = playbook_flags(clauses)   # real pipeline
    return {"matter": matter_id, "bytes": len(data), "clauses": [], "flags": []}   # stub response
```

---

## 🔗 LangChain / LangGraph Connection
Use LangChain loaders plus a structure-aware splitter, `with_structured_output` for clause extraction, and a retriever over case law. In LangGraph: `parse` -> `extract` -> `verify_quotes` -> `playbook` -> `lawyer_review`. A "citation verifier" node that checks each case id against the index is a key safety step.

```python
# LangChain structured extraction (needs API key)
from pydantic import BaseModel                         # schema
from langchain_openai import ChatOpenAI                # model


class ClauseOut(BaseModel):
    type: str                                          # clause type
    quote: str                                         # exact quote


class Out(BaseModel):
    clauses: list[ClauseOut]                           # wrapper


extractor = ChatOpenAI(model="gpt-4o-mini").with_structured_output(Out)   # illustrative model
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Trusting generated case citations
✅ Correct: verify each citation exists in your trusted database.

```python
# Wrong: return llm("Give me cases supporting X")
# Right: retrieve cases from the index, then let the LLM summarise only those; drop unknown ids
```

❌ Mistake 2: Fixed-size chunking that cuts clauses in half
✅ Correct: split by section numbering and keep headings with the text.

❌ Mistake 3: Paraphrased "quotes"
✅ Correct: require verbatim quotes and check them with string match.

---

## 🧠 Tricky Interview Question
**Q**: "The model's summary says the contract allows termination for convenience. The contract actually says 'except as provided in Schedule 3'. How do you catch this?"

**Answer**: Summaries lose qualifiers and cross-references. Extract with exact quotes, resolve cross-references (follow "Schedule 3" and definitions), include them in context, show the lawyer the quote next to the summary, and add evals for exceptions and negations. Use a second verification pass: "Does the quote support this claim?" for each claim.

---

## ⚫ Interview Questions + Answers

Q1: Why must quotes be verbatim?
A1: Lawyers rely on exact wording. Verbatim quotes can be verified automatically and expose hallucination.

Q2: Why not chunk legal documents by fixed size?
A2: Clauses, definitions and cross-references have structure. Splitting by section keeps meaning intact.

Q3: What is a playbook?
A3: A set of the organisation's preferred positions and fallback wording, for example maximum liability cap. Rules compare extracted clauses to it.

Q4: How do you handle very long contracts?
A4: Parse structure, extract per section in parallel (map), merge and deduplicate (reduce), retrieve for specific questions, and use long-context models where it helps.

Q5: (Hard) How do you build trust for a legal tool?
A5: Show evidence for every claim, verify quotes and citations automatically, measure recall of critical clauses on lawyer-labelled contracts (missed clause is worse than extra flag), keep a clear audit trail, protect confidentiality (matter-level access, encryption, no training on client data without consent), and keep lawyers as final reviewers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- First-pass review, clause extraction, comparison against standard terms

❌ Avoid when:
- Giving legal advice directly to the public without a lawyer
- Cited sources cannot be verified

---

## 📊 Visual Diagram
```
 Contract ─▶ OCR/parse ─▶ clause-aware split ─▶ LLM extract {type, quote, page}
                                                      │
                                          verbatim quote check ──✗──▶ drop
                                                      │✓
                                           playbook rules ─▶ risk flags
                                                      │
 Case-law index ─▶ retrieve ─▶ LLM summary ─▶ citation check ─▶ Lawyer review
```

---

## 💰 Cost Impact
Legal documents are long: a 60-page contract can be around 30-40k tokens (illustrative). Full-contract extraction per type multiplies cost.
Optimize: one extraction pass for many clause types, split by sections and use small models for classification, cache parsed text and results by file hash, only run deep analysis on flagged clauses, and use retrieval for Q&A rather than resending the whole contract.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Clause | A provision in a contract | Contract की एक धारा |
| Playbook | Preferred contract positions | पसंदीदा शर्तों की सूची |
| Verbatim | Exact same words | शब्दशः |
| Indemnity | Promise to cover losses | नुकसान की भरपाई का वादा |
| Case law | Past court decisions | पुराने अदालती फैसले |
| Cross-reference | Pointer to another section | दूसरी धारा का संदर्भ |

---

## ⚡ 3-Line Summary
English: Extract clauses with exact quotes and verify them by string match. Compare with a playbook and verify every citation against a trusted index. Lawyers review everything and data stays confidential.
Hindi: Clauses को exact quotes के साथ निकालो और string match से verify करो। Playbook से तुलना करो और हर citation को भरोसेमंद index से जाँचो। वकील सब कुछ review करता है और data गोपनीय रहता है।

---

## ➡️ Next Topic
**540. Design: Financial AI System**: numbers, compliance, and audit trails where wrong math is unacceptable.
