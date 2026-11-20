---

# 189. Handoff Pattern
# हिंदी में: Handoff Pattern (काम सौंपने का तरीका)
# Framework: All (OpenAI SDK and Swarm-style teams make it first-class)
# Already Known: No

> Verified offline with fake agents (no API key). Python 3.13, fastapi 0.163.1, httpx 0.28.1, pydantic 2.14.3. Code is framework-free. Real LLM calls: not run, needs an LLM API key. Token figures are approximate formulas only.

---

## 🔵 Simple Definition (2-3 lines)
A handoff is the moment one agent transfers responsibility for the conversation to another agent, together with a small, explicit packet of information: why it is handing off, a summary, and the structured data the next agent needs. After a handoff the new agent owns the reply.

## 🔵 सरल परिभाषा (Hindi)
Handoff वह क्षण है जब एक agent बातचीत की ज़िम्मेदारी दूसरे agent को सौंपता है, साथ में एक छोटा, स्पष्ट packet: क्यों सौंप रहा है, सारांश, और अगले agent को चाहिए वह structured data। Handoff के बाद जवाब देने की ज़िम्मेदारी नए agent की होती है।

---

## 🔴 Problem it Solves
Naive transfers lose context (the user must repeat themselves), leak data (the next agent sees secrets it should not), or lose accountability (nobody knows who owns the reply). Dumping the full history is expensive and noisy. A well-defined handoff packet keeps the transfer cheap, safe and auditable.

## 🔴 यह क्यों बना? (Hindi)
कच्चे transfer में context खो जाता है (user को दोबारा बताना पड़ता है), data leak होता है (अगला agent वह देख लेता है जो नहीं देखना चाहिए), या जवाबदेही खो जाती है (पता नहीं जवाब किसका है)। पूरा history डालना महँगा और शोरभरा है। अच्छा handoff packet transfer को सस्ता, सुरक्षित और audit योग्य बनाता है।

---

## 🟢 How it Works

```
Step 1 → Source agent decides a peer is better (rule or LLM tool call "transfer_to_X")
Step 2 → Build the handoff packet: {to, reason, summary, data}
Step 3 → Validate: target allowed? required data present? sensitive fields removed?
Step 4 → Optionally filter/trim history (input filter) for the target
Step 5 → Target agent starts with its own instructions + the packet
Step 6 → Target owns the reply (handoff) OR returns a result to the caller (agent-as-tool)
Step 7 → Log the packet for audit and debugging
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Source agent तय करता है कि कोई साथी बेहतर है (rule या LLM tool call "transfer_to_X")
Step 2 → Handoff packet बनाओ: {to, reason, summary, data}
Step 3 → Validate: target अनुमत है? ज़रूरी data मौजूद है? संवेदनशील fields हटे?
Step 4 → ज़रूरत हो तो target के लिए history को filter/trim करो (input filter)
Step 5 → Target agent अपने instructions + packet के साथ शुरू होता है
Step 6 → Target जवाब का मालिक बनता है (handoff) या caller को result लौटाता है (agent-as-tool)
Step 7 → Audit और debug के लिए packet log करो
```

---

## 🟡 Real World Example
**Tariff Agent**: The Classification agent has found HS 8518.22 and the user asks about import restrictions. It hands off to the Compliance agent with packet: reason "user asks legality", summary "importing Bluetooth speakers from China, 100 units", data `{hs_code: 8518.22, country: CN}`. The user's email and API tokens are stripped. Compliance does not re-ask the product. Same idea: a Customer Support bot handing a billing dispute to the Billing agent with the order id.

## 🟡 Real Example Hindi mein
**Tariff Agent**: Classification agent को HS 8518.22 मिल चुका है और user import restrictions पूछता है। वह Compliance agent को packet के साथ handoff करता है: reason "user legality पूछ रहा है", summary "चीन से 100 Bluetooth speakers import", data `{hs_code: 8518.22, country: CN}`। User की email और API tokens हटा दिए जाते हैं। Compliance को product दोबारा नहीं पूछना पड़ता। यही तरीका: Customer Support bot billing विवाद को order id के साथ Billing agent को सौंपता है।

---

## 💻 Code Example — Basic
```python
# Basic handoff with an explicit packet and a required-data check. Runs offline.
from dataclasses import dataclass, field          # packet container


@dataclass
class HandoffPacket:                              # what travels between agents
    to: str                                       # target agent name
    reason: str                                   # why we hand off (audit + target prompt)
    summary: str                                  # short context, not the full chat
    data: dict[str, str] = field(default_factory=dict)  # structured fields


REQUIRED = {"compliance": {"hs_code", "country"}}  # what each target needs


def make_packet(hs_code: str, country: str) -> HandoffPacket:
    return HandoffPacket(
        to="compliance",
        reason="user asks about import legality",
        summary="Importing 100 Bluetooth speakers",
        data={"hs_code": hs_code, "country": country},
    )


def validate(p: HandoffPacket) -> None:           # raise instead of passing bad packets on
    missing = REQUIRED.get(p.to, set()) - set(p.data)
    if missing:                                   # target would have to re-ask the user
        raise ValueError(f"handoff to {p.to} missing {sorted(missing)}")


def compliance_agent(p: HandoffPacket) -> str:    # receiving agent (fake)
    return f"{p.data['hs_code']} from {p.data['country']}: BIS certificate needed"


if __name__ == "__main__":
    pkt = make_packet("8518.22", "CN")
    validate(pkt)                                 # ok
    print(compliance_agent(pkt))
    try:
        validate(HandoffPacket("compliance", "x", "y", {"hs_code": "8518.22"}))
    except ValueError as e:                       # missing country -> rejected
        print("rejected:", e)
```

## 💻 Code Example — Advanced
```python
# Advanced: pydantic handoff packet, PII redaction input-filter, allow-list,
# async target with timeout, FastAPI endpoint, audit log. Offline.
import asyncio                                    # async + timeout
import re                                         # simple PII redaction
from fastapi import FastAPI, HTTPException        # web framework
from fastapi.testclient import TestClient         # offline client
from pydantic import BaseModel, Field             # validation (pydantic v2)

AUDIT: list[dict] = []                            # in-memory audit log (use a DB in production)
ALLOWED = {("classification", "compliance"), ("triage", "classification")}


class Packet(BaseModel):                          # strict, typed handoff packet
    frm: str
    to: str
    reason: str = Field(min_length=3)
    summary: str
    data: dict[str, str] = {}


class Req(BaseModel):
    frm: str
    to: str
    reason: str
    history: list[str]                            # raw chat lines (may contain PII)
    data: dict[str, str] = {}


def redact(line: str) -> str:                     # input filter: strip emails before handoff
    return re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email]", line)


def summarize(history: list[str], keep: int = 2) -> str:  # cheap summary: last N redacted lines
    return " | ".join(redact(h) for h in history[-keep:])


async def compliance_agent(p: Packet) -> str:     # fake async target agent
    await asyncio.sleep(0)
    return f"[compliance] {p.data.get('hs_code', '?')}: BIS needed (context: {p.summary})"


app = FastAPI()


@app.post("/handoff")
async def handoff(req: Req) -> dict:
    if (req.frm, req.to) not in ALLOWED:          # validate target is allowed
        raise HTTPException(403, "handoff not allowed")
    packet = Packet(frm=req.frm, to=req.to, reason=req.reason,
                    summary=summarize(req.history), data=req.data)
    AUDIT.append(packet.model_dump())             # audit BEFORE running the target
    try:
        answer = await asyncio.wait_for(compliance_agent(packet), 5.0)
    except asyncio.TimeoutError:
        raise HTTPException(504, "target agent timed out")
    # approximate tokens saved: full history vs summary (chars/4 estimate)
    full, small = sum(len(h) for h in req.history) // 4, len(packet.summary) // 4
    return {"answer": answer, "packet": packet.model_dump(),
            "approx_tokens_full_history": full, "approx_tokens_summary": small}


if __name__ == "__main__":
    c = TestClient(app)
    body = {"frm": "classification", "to": "compliance", "reason": "legality question",
            "history": ["user: HS code for speaker?", "agent: 8518.22",
                        "user: mail me at a.b@x.com, is it restricted?"],
            "data": {"hs_code": "8518.22", "country": "CN"}}
    print(c.post("/handoff", json=body).json())
    print(c.post("/handoff", json={**body, "to": "triage"}).status_code)  # 403
```

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Handoff form | Edge or command moving to another node, state carries data | Delegation to another agent | First-class handoffs to other agents (the model sees them as transfer tools) | Handoff messages in swarm-style teams |
| Packet | Typed state fields | Task context | Run context + optional input filter on history | Message content |
| History filtering | You edit state | You choose context | Input filters supported (check SDK docs for exact API) | You choose messages |
| Handoff vs tool | Subgraph (return) or edge (transfer) | Delegation returns result | Handoff transfers ownership; agent-as-tool returns result | Handoff transfers; tool-call returns |
| Audit | Checkpoints, traces | Logs | Built-in tracing | Message log |

---

## ⚠️ Common Mistakes
❌ Mistake 1: Handoff with no reason or summary, so the target re-asks everything.
✅ Correct: Always include reason, summary and structured data.

❌ Mistake 2: Passing full raw history including PII and secrets.
✅ Correct: Filter, redact and summarize; apply least privilege.

❌ Mistake 3: Confusing handoff with agent-as-tool.
✅ Correct: Handoff = target takes over the conversation; agent-as-tool = caller stays in charge and gets a result back.

❌ Mistake 4: Trusting the model-produced target name.
✅ Correct: Validate against an allow-list.

---

## 🧠 Tricky Interview Question
After a handoff, the user says "go back to the previous agent". How do you support this safely, and what state must you keep?

Answer: Keep a stack or trail of agents and the packet for each transfer. A "return" is another handoff, validated by the same allow-list, whose packet carries what the second agent learned (for example the compliance result). Do not let the old agent restart from scratch: give it the updated shared state. Also guard against loops (A to B to A to B) using a cap, and decide who owns the conversation at all times (exactly one active agent). If the previous agent was only a helper, consider agent-as-tool instead, so control never left the caller.

---

## ⚫ Interview Questions + Answers

Q1: (Easy) What is a handoff?
A1: Transfer of conversation ownership from one agent to another with context.

Q2: (Medium) Handoff vs agent-as-tool?
A2: Handoff: the new agent talks to the user from now on. Agent-as-tool: the caller invokes a sub-agent for a result, then continues itself.

Q3: (Hard) What belongs in the packet and what must be excluded?
A3: Include reason, short summary, required structured fields, user intent. Exclude secrets, tokens, unrelated PII and bulky tool outputs.

Q4: (Hard) How do you test handoffs?
A4: A labelled set of conversations with the expected target agent, precision and recall per route, tests that illegal targets are rejected, and replay of production traces after each prompt change.

Q5: (System Design) Design handoff infrastructure for 10 agents owned by different teams.
A5: A registry with agent name, capabilities, allowed inbound edges; a versioned packet schema; validation and redaction middleware; audit log; timeouts and a fallback to a human; contract tests per agent pair; metrics: handoff rate, loop rate, re-ask rate after handoff.

---

## 💰 Cost Impact
- Token formula (approximate): `handoff_cost ≈ target_instructions + packet + (trimmed history)`. Full history transfer can multiply tokens, summary keeps it small. The demo above prints an approximate chars/4 comparison.
- Tips: summarize or trim history, pass structured data instead of prose, redact, keep target prompts short.
- Pricing: approximate, from public pricing at time of writing, verify.

---

## 🔷 When to Use
✅ Use when:
- Another agent has the right tools or permissions
- The conversation should continue with a specialist
- You want an auditable ownership change

❌ Avoid when:
- You only need a sub-result (use agent-as-tool)
- The target needs no extra expertise (one agent can do it)

---

## 📊 Visual Diagram
```
 [Classification]                          [Compliance]
  history (raw) --> redact + summarize --> Packet{to, reason, summary, data}
        |                                        |
        +-- validate allow-list (403 if not) ----+--> audit log
                                                 |
                                       new owner replies to user
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Handoff | Transfer of ownership | हस्तांतरण |
| Packet | Data sent with handoff | सूचना पैकेट |
| Input filter | Trims/redacts history | इनपुट फ़िल्टर |
| Agent-as-tool | Sub-agent returning a result | tool के रूप में agent |
| Allow-list | Permitted transfers | अनुमत सूची |
| Redaction | Removing sensitive data | संवेदनशील डेटा हटाना |

---

## ⚡ 3-Line Summary
English: A handoff moves ownership to another agent with a small typed packet.
Validate the target, redact data and log the packet.
Use agent-as-tool when you only need a result back.

Hindi: Handoff में एक छोटे typed packet के साथ ownership दूसरे agent को जाती है।
Target validate करो, data redact करो और packet log करो।
सिर्फ़ result चाहिए तो agent-as-tool इस्तेमाल करो।

---

## ➡️ Next Topic
190. Map-Reduce Pattern (Deep): split a big job into many parallel pieces, then combine the results.

---
