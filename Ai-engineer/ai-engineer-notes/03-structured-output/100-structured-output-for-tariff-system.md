---

# 100. Structured Output for Tariff System
# हिंदी में: Tariff System के लिए Structured Output

---

## 🔵 Simple Definition (English)
This is the capstone for the structured-output section: designing the complete output contract of the Tariff Classification System. It combines a nested schema, enums, optional fields, evidence, confidence, validation against the official tariff table, retries and a routing decision (auto-approve, ask the user, human review).

## 🔵 सरल परिभाषा (Hindi)
यह structured-output section का capstone है: Tariff Classification System का पूरा output contract design करना। इसमें nested schema, enums, optional fields, evidence, confidence, official tariff table से validation, retries और routing decision (auto-approve, user से पूछो, human review) सब मिलते हैं।

---

## 🔴 Problem it Solves
Customs classification affects money and legal compliance. The pipeline needs: machine-readable results, no invented codes, honest "unknown" answers, an audit trail (why this code) and graceful handling of ambiguity. A single loose JSON blob cannot give these guarantees.

## 🔴 यह क्यों बना? (Hindi)
Customs classification पैसे और कानूनी compliance को प्रभावित करता है। Pipeline को चाहिए: machine-readable results, कोई बनावटी code नहीं, ईमानदार "पता नहीं" जवाब, audit trail (यह code क्यों) और अस्पष्टता की सुंदर handling। अकेला ढीला JSON blob ये guarantees नहीं दे सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request: {product_text, optional country}
Step 2 → Extraction call -> ProductFacts {name, material?, origin?, use?}
Step 3 → Retrieve top-K candidate HS codes from the tariff DB/vector store (RAG)
Step 4 → Decision call with Literal/enum = candidates + "none" -> {reasoning, evidence_quote, hs_code, confidence}
Step 5 → Validate: code exists in table; duty comes from table (not from the LLM)
Step 6 → Route: confidence >= 0.85 & no missing facts -> auto_approve; missing facts -> ask_user; else human_review
Step 7 → Return typed response + usage; log everything for audit
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Request: {product_text, optional country}
Step 2 → Extraction call -> ProductFacts {name, material?, origin?, use?}
Step 3 → Tariff DB/vector store से top-K candidate HS codes निकालो (RAG)
Step 4 → Decision call, enum = candidates + "none" -> {reasoning, evidence_quote, hs_code, confidence}
Step 5 → Validate: code table में है; duty table से आती है (LLM से नहीं)
Step 6 → Route: confidence >= 0.85 और कोई fact missing नहीं -> auto_approve; missing facts -> ask_user; वरना human_review
Step 7 → Typed response + usage लौटाओ; audit के लिए सब log करो
```

---

## 🟡 Real World Example
Input: "Wireless earbuds with charging case, made in Vietnam".
Stage 1 extracts `name=earbuds, origin=VN, material=null`.
Retrieval returns candidates `8518.30, 8517.62, 8518.21`. Stage 2 chooses `8518.30` with evidence quote "wireless earbuds" and confidence 0.91. The duty (0%) is read from the table, and the route is `auto_approve`. For "electronics" alone: facts are missing, so the route is `ask_user` with the question "Which electronic product?".

## 🟡 Real Example Hindi mein
Input: "Wireless earbuds with charging case, made in Vietnam"।
Stage 1 निकालता है `name=earbuds, origin=VN, material=null`।
Retrieval candidates देता है `8518.30, 8517.62, 8518.21`। Stage 2 `8518.30` चुनता है, evidence quote "wireless earbuds" और confidence 0.91 के साथ। Duty (0%) table से पढ़ी जाती है और route `auto_approve` होता है। सिर्फ "electronics" के लिए: facts missing हैं, इसलिए route `ask_user` और सवाल "कौन सा electronic product?"।

---

## 💻 Code Example — Basic
```python
# Basic: the complete output contract + validation + routing with a FAKE LLM (runs offline).
# Needs: pip install pydantic
from typing import Literal, Optional
from pydantic import BaseModel, Field, ValidationError

TARIFF_TABLE: dict[str, float] = {"8518.30": 0.0, "8517.62": 0.0, "8518.21": 2.5}   # code -> duty%

class ProductFacts(BaseModel):                          # stage 1 output (optional = honest unknown)
    name: str
    material: Optional[str]
    origin_country: Optional[str]

class HSDecision(BaseModel):                            # stage 2 output (reasoning first)
    reasoning: str
    evidence_quote: str
    hs_code: str
    confidence: float = Field(ge=0, le=1)

class FinalResult(BaseModel):                           # what the API returns
    hs_code: Optional[str]
    duty_percent: Optional[float]
    route: Literal["auto_approve", "ask_user", "human_review"]
    ask: list[str] = []

def decide_route(facts: ProductFacts, dec: HSDecision) -> FinalResult:
    """Validate against the table, take duty from the table, pick the route."""
    if dec.hs_code not in TARIFF_TABLE:                 # LLM invented a code
        return FinalResult(hs_code=None, duty_percent=None, route="human_review")
    missing = [f for f in ("material", "origin_country") if getattr(facts, f) is None]
    duty = TARIFF_TABLE[dec.hs_code]                    # truth from table, not from LLM
    if dec.confidence >= 0.85 and not missing:
        return FinalResult(hs_code=dec.hs_code, duty_percent=duty, route="auto_approve")
    if missing:
        return FinalResult(hs_code=dec.hs_code, duty_percent=duty, route="ask_user", ask=missing)
    return FinalResult(hs_code=dec.hs_code, duty_percent=duty, route="human_review")

facts = ProductFacts.model_validate_json('{"name": "earbuds", "material": "plastic", "origin_country": "VN"}')
good = HSDecision.model_validate_json(
    '{"reasoning": "wireless audio device", "evidence_quote": "wireless earbuds", "hs_code": "8518.30", "confidence": 0.91}')
fake = HSDecision(reasoning="guess", evidence_quote="?", hs_code="9999.99", confidence=0.99)
vague = ProductFacts(name="electronics", material=None, origin_country=None)

print(decide_route(facts, good))                        # auto_approve, duty 0.0
print(decide_route(facts, fake).route)                  # human_review (invented code)
print(decide_route(vague, good).route, decide_route(vague, good).ask)   # ask_user ['material', 'origin_country']
```

## 💻 Code Example — Advanced
```python
# Production: two-stage async pipeline with OpenAI parse(), retrieval-restricted enum, retries, usage.
import asyncio
from enum import Enum
from typing import Optional
from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field, ValidationError, create_model

client = AsyncOpenAI()
TARIFF_TABLE: dict[str, float] = {"8518.30": 0.0, "8517.62": 0.0, "8518.21": 2.5}

class ProductFacts(BaseModel):
    name: str
    material: Optional[str] = Field(description="Main material if stated, else null")
    origin_country: Optional[str] = Field(description="ISO-2 code if stated, else null")

async def retrieve_candidates(facts: ProductFacts, k: int = 3) -> list[str]:
    """Stand-in for vector search over the tariff DB."""
    await asyncio.sleep(0)
    return list(TARIFF_TABLE)[:k]

def decision_model(candidates: list[str]) -> type[BaseModel]:
    """Build the decision schema with a dynamic enum limited to retrieved candidates + NONE."""
    members = {"C_" + c.replace(".", "_"): c for c in candidates} | {"NONE": "none"}
    code_enum = Enum("Code", members, type=str)
    return create_model("HSDecision",
        reasoning=(str, Field(description="One sentence")),
        evidence_quote=(str, Field(description="Exact words from the input that justify the code")),
        hs_code=(code_enum, ...),
        confidence=(float, Field(description="0 to 1")))

async def parse(schema: type[BaseModel], system: str, user: str) -> Optional[BaseModel]:
    """One structured call with consistent error handling."""
    try:
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini", temperature=0, max_tokens=300, response_format=schema,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
    except (OpenAIError, ValidationError) as exc:
        print("stage failed:", exc.__class__.__name__)
        return None
    msg = completion.choices[0].message
    print("tokens:", completion.usage.total_tokens if completion.usage else "?")
    return None if msg.refusal else msg.parsed

async def classify(text: str) -> dict:
    facts = await parse(ProductFacts, "Extract facts. Use null if not stated. Never guess.", text)
    if facts is None:
        return {"route": "human_review", "reason": "extraction failed"}
    candidates = await retrieve_candidates(facts)
    Decision = decision_model(candidates)
    dec = await parse(Decision, f"Choose the HS code for the product. Options: {candidates} or none.", text)
    if dec is None or dec.hs_code.value == "none":
        return {"route": "human_review", "reason": "no suitable code"}
    code = dec.hs_code.value
    missing = [f for f in ("material", "origin_country") if getattr(facts, f) is None]
    route = ("ask_user" if missing else "auto_approve" if dec.confidence >= 0.85 else "human_review")
    return {"hs_code": code, "duty_percent": TARIFF_TABLE[code],        # duty from table
            "evidence": dec.evidence_quote, "confidence": dec.confidence,
            "route": route, "ask": missing}

if __name__ == "__main__":
    print(asyncio.run(classify("Wireless earbuds with charging case, made in Vietnam")))   # needs API key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Tariff Classification API")

class ClassifyRequest(BaseModel):
    product_text: str = Field(min_length=3, max_length=1000)

class ClassifyResponse(BaseModel):
    hs_code: Optional[str] = None
    duty_percent: Optional[float] = None
    evidence: Optional[str] = None
    confidence: Optional[float] = None
    route: str
    ask: list[str] = []
    reason: Optional[str] = None

@app.post("/v1/tariff/classify", response_model=ClassifyResponse)
async def classify_route(req: ClassifyRequest) -> ClassifyResponse:
    try:
        out = await classify(req.product_text)         # pipeline from above
    except Exception as exc:                           # last-resort guard: never leak internals
        raise HTTPException(status_code=502, detail="classification pipeline failed") from exc
    return ClassifyResponse(**out)
```

---

## 🔗 LangChain / LangGraph Connection
```python
from typing import Optional, TypedDict
from langgraph.graph import StateGraph, END

class State(TypedDict, total=False):
    text: str
    facts: dict
    result: dict

async def extract_node(state: State) -> State:
    return {"facts": {"name": state["text"]}}           # call with_structured_output(ProductFacts) here

async def decide_node(state: State) -> State:
    return {"result": await classify(state["text"])}    # reuse the pipeline or split into nodes

def after_decide(state: State) -> str:
    return END if state["result"].get("route") == "auto_approve" else "human_queue"

async def human_queue(state: State) -> State:
    return state                                         # push to review queue / interrupt()

g = StateGraph(State)
g.add_node("extract", extract_node)
g.add_node("decide", decide_node)
g.add_node("human_queue", human_queue)
g.set_entry_point("extract")
g.add_edge("extract", "decide")
g.add_conditional_edges("decide", after_decide, {END: END, "human_queue": "human_queue"})
g.add_edge("human_queue", END)
graph = g.compile()                                      # await graph.ainvoke({"text": "..."})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Letting the LLM provide the duty rate
✅ Correct: LLM picks the code; duty comes from the official table.

```python
# Wrong: duty = decision.duty_percent   # hallucination risk, legal risk
# Right: duty = TARIFF_TABLE[decision.hs_code]
```

❌ Mistake 2: Letting the model choose from all 5,000+ codes
✅ Correct: Retrieve candidates first, restrict the enum, add a "none" option.

```python
# Wrong: hs_code: str   # free text
# Right: hs_code: Enum of top-K candidates + "none"
```

---

## 🧠 Tricky Interview Question

**Q**: "Your pipeline reports 97% accuracy in testing but customs auditors find 8% wrong in production. What could explain the gap, and how do you fix it?"

**Answer**: (1) Test set too easy or leaked into prompts/few-shots; production has vaguer descriptions, other languages and rare items. (2) Retrieval misses: if the right code is not among the candidates, the model must pick a wrong one, so measure recall@K separately. (3) Confidence is not calibrated, so auto-approval lets mistakes through. (4) Tariff table updates not reflected. Fix: sample production traffic into a labelled eval set, measure per-stage metrics (retrieval recall, decision accuracy, routing precision), tune the auto-approve threshold for a target error rate, keep a human-review sample even for auto-approved items, and re-evaluate on every table, prompt or model change.

---

## ⚫ Interview Questions + Answers

Q1: Why two stages (extract then decide)?
A1: Extraction identifies facts and missing information; the decision stage works from clean facts and a restricted candidate list, which is more accurate and easier to audit.

Q2: Why take duty from the table?
A2: Facts like rates must come from a source of truth; the LLM only selects/extracts.

Q3: What is the purpose of the `evidence_quote`?
A3: Verifiability: you can check that the quote appears in the input and show it to auditors.

Q4: How do you decide the auto-approve threshold?
A4: Plot accuracy vs confidence on a labelled set and choose the threshold giving the acceptable error rate (e.g. <1%); recheck regularly.

Q5: How would you evolve this system to handle 1M classifications/day within a budget?
A5: Cache repeated products (normalised text hash), use a small model for extraction and a stronger one only when confidence is low (cascade), batch offline requests via Batch API, restrict candidates with embeddings, prompt-cache stable prefixes, queue non-interactive jobs, monitor cost per request and accuracy by segment, and fine-tune a small model on reviewed data if volume justifies.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Decisions have legal or financial impact
- You need audit trails and human-in-the-loop

❌ Avoid when:
- Low-stakes tagging (a single-call classification may be enough)

---

## 📊 Visual Diagram
```
 product text
     │
     ▼ [LLM #1] extract ─► ProductFacts {name, material?, origin?}
     │
     ▼ [Vector DB] top-K candidate HS codes
     │
     ▼ [LLM #2] decide (enum = candidates + none)
     │          {reasoning, evidence_quote, hs_code, confidence}
     ▼ validate ─► code in table? ─ no ─► human_review
     │ yes: duty := TABLE[code]
     ▼ route
   ├─ conf>=0.85 & facts complete ─► auto_approve ─► invoice
   ├─ facts missing ───────────────► ask_user
   └─ otherwise ───────────────────► human_review
```

---

## 💰 Cost Impact
Two calls per item: extraction (~300 input / 60 output tokens) and decision (~500 input / 80 output). With `gpt-4o-mini` this is roughly $0.0002 per item, about $200 per 1M items, plus embedding/retrieval costs. Retries and human review add cost.
Optimise: cache, merge stages for easy inputs, cascade models, short schemas, Batch API for offline loads, prompt caching, track cost per approved classification (not just per call).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HS code | Global product classification code | Product का वैश्विक classification code |
| Candidate list | Retrieved possible codes | संभावित codes की list |
| Evidence quote | Source words supporting answer | Answer का सबूत |
| Auto-approve | Accept without human | बिना human के स्वीकार |
| Human-in-the-loop | Human reviews uncertain cases | अनिश्चित मामलों में human |
| Cascade | Cheap model first, strong if needed | पहले सस्ता, ज़रूरत पर मज़बूत model |

---

## ⚡ 3-Line Summary
English: The Tariff output contract combines nested schema, enums, optional fields, evidence and confidence. The LLM selects the code from retrieved candidates while the duty comes from the official table. Routing sends uncertain cases to users or humans.
Hindi: Tariff output contract में nested schema, enums, optional fields, evidence और confidence सब मिलते हैं। LLM retrieved candidates में से code चुनता है और duty official table से आती है। Routing अनिश्चित मामलों को users या humans के पास भेजती है।

---

## ➡️ Next Topic
**101. What are Embeddings** (already covered) then **102. Why Embeddings Work** — the intuition behind turning text into vectors, which powers the retrieval step used here.
