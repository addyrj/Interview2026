---

# 358. Agent Context Management
# हिंदी में: Agent Context Management

---

## 🔵 Simple Definition (English)
Agent context management is deciding **what each agent sees** in its prompt: which messages, facts, tool results and documents, and how much. The goal is the smallest context that still lets the agent do its job. It uses filtering, trimming, summarising and offloading to external storage.

## 🔵 सरल परिभाषा (Hindi)
Agent context management का मतलब है तय करना कि **हर agent को prompt में क्या दिखे**: कौन से messages, facts, tool results और documents, और कितने। लक्ष्य है सबसे छोटा context जिसमें agent अपना काम कर सके। इसमें filtering, trimming, summarising और बाहरी storage में रखना शामिल है।

---

## 🔴 Problem it Solves
In multi-agent systems, context grows with every step: tool outputs, other agents' chatter, retrieved documents. Large contexts cost money, slow responses, hit the context window limit and hurt accuracy ("lost in the middle", distraction by irrelevant text). Also, some agents should not see sensitive data at all.

## 🔴 यह क्यों बना? (Hindi)
Multi-agent systems में हर step के साथ context बढ़ता है: tool outputs, दूसरे agents की बातचीत, retrieved documents। बड़ा context पैसे खर्च करता है, response धीमा करता है, context window की सीमा छूता है और accuracy घटाता है ("lost in the middle", बेकार text से भटकना)। कुछ agents को संवेदनशील data दिखना ही नहीं चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List what each agent truly needs (role + current task)
Step 2 → Keep full data in state/store, not in the prompt
Step 3 → Build a context for each call: system prompt + task + selected fields
Step 4 → Trim long message history to a token budget (keep latest + important)
Step 5 → Summarise old turns into a short memory note
Step 6 → Replace big tool outputs with a short result + a reference id
Step 7 → Redact secrets/PII before the call
Step 8 → Measure tokens per agent and enforce a budget
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → लिखो कि हर agent को सच में क्या चाहिए (role + मौजूदा task)
Step 2 → पूरा data state/store में रखो, prompt में नहीं
Step 3 → हर call के लिए context बनाओ: system prompt + task + चुने fields
Step 4 → लंबी message history को token budget तक trim करो (नए + ज़रूरी रखो)
Step 5 → पुरानी बातों को छोटे memory note में summarise करो
Step 6 → बड़े tool output की जगह छोटा result + reference id रखो
Step 7 → Call से पहले secrets/PII हटाओ
Step 8 → हर agent के tokens नापो और budget लागू करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The Classifier needs the product description and 5 candidate headings. The DutyAgent needs only `hs_code` and `origin`. The Reporter needs the final fields, not the 40-page tariff retrieval results. The raw retrieved text stays in a vector store; state keeps chunk ids. The importer's phone and company tax id are redacted from every LLM prompt.

**Amazon-style**: A support agent sees the last 5 messages plus an order summary, not the full 200-message history.

## 🟡 Real Example Hindi mein
**Tariff System**: Classifier को product description और 5 candidate headings चाहिए। DutyAgent को सिर्फ `hs_code` और `origin`। Reporter को final fields चाहिए, 40 पन्नों के retrieval results नहीं। Raw retrieved text vector store में रहता है; state में chunk ids रहते हैं। Importer का फ़ोन और company tax id हर LLM prompt से हटा दिए जाते हैं।

**Amazon-style**: Support agent को आखिरी 5 messages और order summary दिखती है, 200 messages का पूरा इतिहास नहीं।

---

## 💻 Code Example — Basic
```python
# Build a small per-agent context from big shared state (runs offline)
import re  # for simple redaction

STATE: dict[str, object] = {
    "description": "Bluetooth headphones, contact 9876543210",  # contains a phone number
    "origin": "VN",
    "hs_code": "8518.30",
    "retrieved_chunks": ["x" * 500] * 40,  # big payload we must NOT send everywhere
}

# What each agent is allowed to see (allow-list)
VIEWS: dict[str, list[str]] = {
    "classifier": ["description"],
    "duty": ["hs_code", "origin"],
}

def redact(text: str) -> str:
    return re.sub(r"\b\d{10}\b", "[PHONE]", text)  # hide 10 digit numbers

def build_context(agent: str, state: dict[str, object]) -> str:
    fields = VIEWS[agent]  # allowed fields only
    lines = [f"{f}: {redact(str(state[f]))}" for f in fields]  # redact each value
    return "\n".join(lines)

def approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)  # rough rule: 4 characters per token

if __name__ == "__main__":
    for agent in VIEWS:
        ctx = build_context(agent, STATE)  # small, safe context
        print(agent, approx_tokens(ctx), "tokens ->", ctx)
    print("naive full state tokens:", approx_tokens(str(STATE)))  # much bigger
```

## 💻 Code Example — Advanced
```python
# Token-budgeted history trimming + summarisation, async, with error handling
import asyncio  # async runtime

Message = dict[str, str]  # {"role": ..., "content": ...}

def tokens(text: str) -> int:
    return max(1, len(text) // 4)  # approximate; use tiktoken in production

async def summarise(old: list[Message]) -> str:
    await asyncio.sleep(0)  # a real version calls a cheap LLM here
    return f"Summary of {len(old)} earlier messages."  # placeholder summary

async def fit_to_budget(history: list[Message], budget: int) -> list[Message]:
    """Keep the newest messages within budget; summarise the rest."""
    kept: list[Message] = []  # newest first while collecting
    used = 0
    for msg in reversed(history):  # walk from latest to oldest
        cost = tokens(msg["content"])
        if used + cost > budget:  # budget exceeded
            break
        kept.append(msg)
        used += cost
    kept.reverse()  # restore order
    dropped = history[: len(history) - len(kept)]  # older part
    if dropped:
        try:
            note = await summarise(dropped)  # compress what we drop
        except Exception:  # summariser failed: continue without it
            note = "Earlier conversation omitted."
        kept.insert(0, {"role": "system", "content": note})  # prepend memory note
    return kept

async def main() -> None:
    history = [{"role": "user", "content": "msg " * 200} for _ in range(10)]  # long chat
    trimmed = await fit_to_budget(history, budget=500)
    print(len(history), "->", len(trimmed), "messages")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Enforce the context budget at the API boundary and return token usage so you can monitor it.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()
MAX_CONTEXT_TOKENS = 3000  # per-agent budget

class AgentIn(BaseModel):
    agent: str             # which agent to run
    history: list[dict]    # prior messages

@app.post("/agent/run")
async def run_agent(body: AgentIn) -> dict:
    if body.agent not in VIEWS:
        raise HTTPException(404, "unknown agent")  # validate input
    trimmed = await fit_to_budget(body.history, MAX_CONTEXT_TOKENS)  # enforce budget
    used = sum(tokens(m["content"]) for m in trimmed)  # measure
    return {"messages_used": len(trimmed), "approx_tokens": used}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.messages import SystemMessage, trim_messages  # real LangChain utilities
from langchain_openai import ChatOpenAI  # llm

llm = ChatOpenAI(model="gpt-4o-mini")

# trim_messages keeps the last messages that fit the token budget
trimmer = trim_messages(
    max_tokens=1000,          # budget
    strategy="last",          # keep newest
    token_counter=llm,        # count tokens with the model
    include_system=True,      # keep the system prompt
    start_on="human",         # history must start on a human turn
)

def agent_node(state: dict) -> dict:
    msgs = trimmer.invoke(state["messages"])  # trimmed view for this agent only
    reply = llm.invoke([SystemMessage(content="You are the duty agent.")] + msgs)
    return {"messages": [reply]}  # state keeps full history, the prompt used only a slice
```
In LangGraph, the state holds the full data while each node builds its own small view. Subgraphs can also have their own private state schema, which isolates context between agents.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing the entire shared state to every agent
✅ Correct: per-agent allow-list view.

```python
# Wrong
prompt = str(state)
# Right
prompt = build_context("duty", state)
```

❌ Mistake 2: Putting raw tool outputs (huge JSON, PDFs) into the message history
✅ Correct: store the output elsewhere, keep a short summary and an id.

```python
# Wrong
messages.append({"role": "tool", "content": giant_json})
# Right
doc_id = store.save(giant_json)
messages.append({"role": "tool", "content": f"Saved as {doc_id}. 42 rows, top: ..."})
```

---

## 🧠 Tricky Interview Question
**Q**: "After you trimmed context, the agent became cheaper but started making wrong tariff decisions. What happened?"

**Answer**: Trimming removed information the agent needed (for example a customer constraint stated early or a prior decision). Fixes: separate "must-keep" facts into structured state (constraints, decisions) that is always included; trim only chatter; summarise instead of dropping; evaluate with regression tests before and after the trimming change; pick budgets from measured accuracy, not guesses.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why not give every agent the whole conversation?
A1: It costs more, is slower, may exceed the window, and distracts the model. It may also leak sensitive data.

Q2: [Easy] What is context trimming?
A2: Keeping only the most recent or most important messages that fit a token budget.

Q3: [Medium] Trimming vs summarising?
A3: Trimming drops old content (cheap, loses info). Summarising compresses it (costs an LLM call, keeps the gist). Often combine both.

Q4: [Medium] How do you handle huge tool outputs?
A4: Offload to storage, return a compact summary plus a reference id, and let the agent fetch details with a tool only if needed.

Q5: [Hard] Design context policy for 5 agents sharing a workflow.
A5: Define a per-role view of state (allow-list), a per-agent token budget, must-keep structured memory, rolling summary for chat, redaction layer for PII, and monitoring of tokens per agent per run with alerts when a budget is exceeded.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Workflows with many steps, tools or agents
- Long chats, large retrieved documents
- Privacy needs between agents

❌ Avoid over-engineering when:
- Short single-turn calls under 1K tokens
- Prototype stage, measure first

---

## 📊 Visual Diagram
```
        FULL STATE / STORE (big, durable)
   +--------------------------------------------+
   | messages | docs | tool outputs | facts | ids|
   +--------------------------------------------+
        |filter+trim        |filter       |filter
        v                   v             v
   [Classifier ctx]   [Duty ctx]    [Reporter ctx]
     ~800 tokens       ~150 tokens    ~400 tokens
```

---

## 💰 Cost Impact
- Input tokens usually dominate multi-agent cost. Cutting a 6,000-token context to 1,000 saves 83 percent of input cost for that call.
- At gpt-4o-mini input price of $0.15 per 1M tokens, 1M calls x 5,000 saved tokens saves about $750.
- Optimise: allow-list views, trimming to a budget, rolling summaries, offload big outputs, stable prefixes for prompt caching.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context budget | Max tokens per call | प्रति call tokens की सीमा |
| Trimming | Dropping old messages | पुराने messages हटाना |
| Summarisation | Compressing history | इतिहास को छोटा करना |
| Offloading | Keeping data outside the prompt | Data को prompt के बाहर रखना |
| Redaction | Removing sensitive text | संवेदनशील text हटाना |
| Allow-list view | Fields an agent may see | Agent को दिखने वाले fields |

---

## ⚡ 3-Line Summary
English: Give each agent only the context it needs. Trim, summarise, offload and redact, and keep must-keep facts in structured state. Measure tokens per agent and test accuracy after every change.
Hindi: हर agent को सिर्फ उतना context दो जितना चाहिए। Trim, summarise, offload और redact करो, और ज़रूरी facts structured state में रखो। हर agent के tokens नापो और हर बदलाव के बाद accuracy test करो।

---

## ➡️ Next Topic
**359. Agent Conflict Resolution** — what to do when two agents disagree.
