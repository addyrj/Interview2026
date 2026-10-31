---

# 294. Tool Selection Strategy
# हिंदी में: Tool Selection Strategy (सही tool कैसे चुनें)

---

## 🔵 Simple Definition (English)
Tool selection strategy is how you make sure the LLM picks the right tool (or no tool). It covers clear names and descriptions, `tool_choice` settings, narrowing the tool list per request (retrieval or routing), and measuring selection accuracy with an eval set.

## 🔵 सरल परिभाषा (Hindi)
Tool selection strategy वह तरीका है जिससे LLM सही tool (या कोई भी नहीं) चुने। इसमें साफ़ names/descriptions, `tool_choice` settings, हर request के लिए tool list छोटी करना (retrieval या routing) और eval set से selection accuracy मापना शामिल है।

---

## 🔴 Problem it Solves
With 3 tools the model rarely errs. With 30+ tools it picks the wrong one, calls tools when no tool is needed, or never calls the tool it should. Every tool schema also costs input tokens on every request: 40 tools can be 6,000+ tokens before the user says a word.

## 🔴 यह क्यों बना? (Hindi)
3 tools में model शायद ही गलती करता है। 30+ tools में वह गलत tool चुनता है, ज़रूरत न होने पर भी tool call करता है, या ज़रूरी tool call ही नहीं करता। हर tool का schema हर request में input tokens खाता है: 40 tools = user के बोलने से पहले 6,000+ tokens।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write precise tool names + descriptions (what, when to use, when NOT to use)
Step 2 → Use distinct names and clear parameter docs; avoid overlapping tools
Step 3 → Narrow the list: retrieve top-k relevant tools or route by intent
Step 4 → Set tool_choice: "auto" (default), "required" (must call), {"type":"function",...} (force one), "none"
Step 5 → Model returns tool_call(s) or plain text
Step 6 → Evaluate: run labelled questions, measure correct-tool rate and false-call rate
Step 7 → Fix descriptions/overlaps, re-run eval; track in production logs
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Precise names + descriptions लिखो (क्या, कब use करें, कब नहीं)
Step 2 → अलग-अलग names, साफ़ parameter docs; overlapping tools मत रखो
Step 3 → List छोटी करो: top-k relevant tools retrieve करो या intent से route करो
Step 4 → tool_choice: "auto", "required", किसी एक को force, या "none"
Step 5 → Model tool_call(s) या plain text देता है
Step 6 → Evaluate: labelled सवाल चलाओ, सही-tool दर और false-call दर मापो
Step 7 → Descriptions ठीक करो, eval दोबारा चलाओ; production logs में track करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: tools are `search_hs_codes`, `get_tariff_rate`, `get_exchange_rate`, `calculator`, `search_trade_rules`, `file_declaration`. Question "Which HS code fits a cotton t-shirt?" must use `search_hs_codes`, not `get_tariff_rate`. Descriptions say: `get_tariff_rate`: "Use ONLY when you already have an HS code." That one line removes most mistakes.

**Amazon AI**: 200 internal tools are impossible in one prompt, so a tool retriever embeds tool descriptions and sends only the top 8 per query.

## 🟡 Real Example Hindi mein
**Tariff System**: Tools हैं `search_hs_codes`, `get_tariff_rate`, `calculator` आदि। "Cotton t-shirt का HS code?" पर `search_hs_codes` चलना चाहिए, `get_tariff_rate` नहीं। Description में लिखा: "`get_tariff_rate` तभी जब HS code पहले से हो।" यह एक line ज़्यादातर गलतियाँ हटा देती है।

**Amazon AI**: 200 tools एक prompt में नहीं आ सकते, इसलिए tool retriever descriptions को embed करता है और हर query पर सिर्फ़ top 8 भेजता है।

---

## 💻 Code Example — Basic
```python
# Tool selection by retrieval: pick top-k tools by keyword overlap (offline demo)
from dataclasses import dataclass

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str

TOOLS: list[ToolSpec] = [
    ToolSpec("search_hs_codes", "Find candidate HS codes from a product description. Use when HS code is unknown."),
    ToolSpec("get_tariff_rate", "Get duty percent for a known HS code like 8517.12. Do NOT use to find the code."),
    ToolSpec("get_exchange_rate", "Live currency exchange rate between two currencies."),
    ToolSpec("calculator", "Exact arithmetic for duty and tax calculations."),
    ToolSpec("file_declaration", "File a customs declaration. Irreversible."),
]

def words(text: str) -> set[str]:
    """Lowercase word set without punctuation."""
    return {w.strip(".,?!").lower() for w in text.split() if len(w) > 2}

def select_tools(question: str, k: int = 2) -> list[str]:
    """Score each tool by overlap between question words and its description."""
    q = words(question)
    scored = [(len(q & words(t.name.replace("_", " ") + " " + t.description)), t.name) for t in TOOLS]
    scored.sort(reverse=True)                              # best score first
    return [name for score, name in scored[:k] if score > 0]

print(select_tools("What is the exchange rate for dollar to rupee currency?"))   # exchange tool first
print(select_tools("Find the HS code for a cotton shirt"))                       # search_hs_codes
```

## 💻 Code Example — Advanced
```python
# Production: embedding-based tool retrieval + tool_choice policy + eval harness
import asyncio, json, math
from typing import Any
from openai import AsyncOpenAI

client = AsyncOpenAI()

TOOL_SCHEMAS: dict[str, dict[str, Any]] = {}      # name -> full OpenAI tool schema (fill from your registry)

def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0

async def embed(texts: list[str]) -> list[list[float]]:
    resp = await client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [d.embedding for d in resp.data]

class ToolRetriever:
    """Embeds tool descriptions once, then returns top-k per question."""
    def __init__(self) -> None:
        self.names: list[str] = []
        self.vectors: list[list[float]] = []

    async def build(self) -> None:
        self.names = list(TOOL_SCHEMAS)
        docs = [f"{n}: {TOOL_SCHEMAS[n]['function']['description']}" for n in self.names]
        self.vectors = await embed(docs)                   # one-time cost

    async def top_k(self, question: str, k: int = 5) -> list[dict[str, Any]]:
        qv = (await embed([question]))[0]
        ranked = sorted(zip(self.names, self.vectors), key=lambda p: cosine(qv, p[1]), reverse=True)
        return [TOOL_SCHEMAS[n] for n, _ in ranked[:k]]

async def ask(question: str, retriever: ToolRetriever, force_tool: str | None = None) -> Any:
    tools = await retriever.top_k(question)                # only send relevant schemas
    tool_choice: Any = "auto"                              # model may answer without tools
    if force_tool:                                         # e.g. extraction pipelines
        tool_choice = {"type": "function", "function": {"name": force_tool}}
    try:
        return await client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": question}],
            tools=tools, tool_choice=tool_choice,
        )
    except Exception as exc:
        raise RuntimeError(f"LLM call failed: {exc}") from exc

async def evaluate(cases: list[tuple[str, str | None]], retriever: ToolRetriever) -> dict[str, float]:
    """cases = (question, expected_tool or None). Returns selection accuracy."""
    correct = 0
    for question, expected in cases:
        resp = await ask(question, retriever)
        calls = resp.choices[0].message.tool_calls or []
        chosen = calls[0].function.name if calls else None
        correct += int(chosen == expected)
    return {"accuracy": correct / len(cases)}
```

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

retriever = ToolRetriever()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await retriever.build()                                # embed tools once at startup
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/ask")
async def ask_route(question: str) -> dict:
    resp = await ask(question, retriever)
    msg = resp.choices[0].message
    return {"tool_calls": [c.function.name for c in (msg.tool_calls or [])], "text": msg.content,
            "prompt_tokens": resp.usage.prompt_tokens}      # watch schema token cost
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_tariff_rate(hs_code: str) -> str:
    """Get duty percent for a KNOWN HS code like 8517.12. Do not use to find the code."""
    return "18.0"

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([get_tariff_rate], tool_choice="auto")   # or tool_choice="get_tariff_rate"
msg = llm_with_tools.invoke("Duty for 8517.12?")
print(msg.tool_calls)                                     # list of {name, args, id}
```
For many tools, LangGraph's "big tools" pattern stores tool descriptions in a vector store and binds only retrieved ones per turn. Multi-agent graphs also reduce selection errors: each sub-agent has 3-5 tools.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Vague or overlapping descriptions
✅ Correct: Say when to use and when not to.

```python
# Wrong:
"description": "Gets tariff info"        # for both search_hs_codes and get_tariff_rate
# Right:
"description": "Get duty percent for a KNOWN HS code. Do NOT use to find the code."
```

❌ Mistake 2: Sending all 40 tools on every request
✅ Correct: Retrieve or route to a small subset.

```python
# Wrong:
tools=ALL_TOOLS
# Right:
tools=await retriever.top_k(question, k=5)
```

❌ Mistake 3: Forcing `tool_choice="required"` for chat messages like "thanks". Use `auto`.

---

## 🧠 Tricky Interview Question

**Q**: "You added a new tool and accuracy on old tests dropped, even though the new tool is never needed in those tests. Why?"

**Answer**: The new tool's description overlaps semantically with an existing one, so the model sometimes picks it (distractor effect), and a bigger tool list dilutes attention. Fix: sharpen both descriptions with explicit boundaries, rename for clarity, narrow tools per request via retrieval/routing, and keep a regression eval suite that runs on every tool change.

---

## ⚫ Interview Questions + Answers

Q1: What does `tool_choice="auto"` do? (Easy)
A1: The model decides whether to call a tool or answer directly. Other values: `"required"` (must call some tool), `"none"` (no tools), or a specific function object to force one.

Q2: Why do tool descriptions matter? (Easy)
A2: The model chooses tools almost entirely from name, description and parameter docs. Good descriptions are the cheapest accuracy improvement.

Q3: How do you handle 100+ tools? (Medium)
A3: Do not send all. Use a retriever over tool descriptions (top-k), intent routing to a tool group, or multi-agent design where each agent has a small toolset.

Q4: How do you measure selection quality? (Medium)
A4: Build labelled cases (question, expected tool or none). Measure correct-tool rate, false-positive tool calls, missed calls, and argument correctness. Run on every change and track in production by logging tool choices.

Q5: When should you force a tool with `tool_choice`? (Hard)
A5: When you use the model as a structured extractor (always return the schema), in deterministic pipelines, or to guarantee a step like retrieval. Not for general chat, since it breaks natural conversation. Also, forcing a tool with extended reasoning/thinking modes may be restricted on some providers, so check docs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than ~8 tools
- Tools have similar purposes
- Token cost of schemas is high

❌ Avoid when:
- Only 2-3 distinct tools (extra retrieval adds latency for no gain)
- Forcing a tool when "no tool" is a valid answer

---

## 📊 Visual Diagram
```
 User question
      │
      ▼
 ┌────────────────┐   embeds     ┌───────────────────────┐
 │ Tool retriever │◄─────────────│ 40 tool descriptions  │
 └────────────────┘              └───────────────────────┘
      │ top-5 schemas
      ▼
 ┌──────────┐  tool_choice=auto  ┌───────────────────────┐
 │   LLM    │───────────────────►│ tool_call OR text     │
 └──────────┘                    └───────────────────────┘
      │
      ▼
 eval: correct tool? false call? -> improve descriptions
```

---

## 💰 Cost Impact
Each tool schema is roughly 100-200 tokens. 40 tools = about 6K tokens per request, re-sent in every agent round. At 100K requests/day on gpt-4o-mini, 6K tokens is about $90/day for schemas alone. Sending 5 retrieved tools cuts it to about $11/day. Retrieval costs a small embedding call (cache tool vectors; embed only the question).

Optimize: tool retrieval, shorter descriptions, prompt caching for stable tool lists, and multi-agent splits.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| tool_choice | Controls whether/which tool is called | Tool चुनाव नियंत्रण |
| Tool retrieval | Fetch relevant tools by similarity | Similarity से tools चुनना |
| Distractor | Similar tool that confuses the model | भ्रमित करने वाला tool |
| False call | Tool called when not needed | बेवजह tool call |
| Eval set | Labelled test questions | Labelled test सवाल |
| Intent routing | Pick toolset by user intent | Intent से tools चुनना |

---

## ⚡ 3-Line Summary
English: Good tool selection comes from sharp descriptions, a small relevant tool list, correct `tool_choice`, and an eval set. Retrieve or route tools when you have many. Fewer schemas also means fewer tokens.
Hindi: अच्छा tool selection तेज़ descriptions, छोटी relevant list, सही `tool_choice` और eval set से आता है। ज़्यादा tools हों तो retrieve या route करो। कम schemas = कम tokens।

---

## ➡️ Next Topic
**295. Tool Use Best Practices** — a production checklist that ties together everything in this section.
