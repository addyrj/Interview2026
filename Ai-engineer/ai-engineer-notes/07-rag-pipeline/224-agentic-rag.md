---

# 224. Agentic RAG
# हिंदी में: Agentic RAG (फ़ैसला लेने वाला RAG)

---

## 🔵 Simple Definition (English)
Agentic RAG puts an LLM **agent** in charge of retrieval. Instead of always doing "retrieve once, then answer", the agent decides whether to search, which tool or index to use, what query to write, and whether the results are good enough, looping until it can answer.

## 🔵 सरल परिभाषा (Hindi)
Agentic RAG में retrieval का फ़ैसला LLM **agent** करता है। हर बार "एक बार retrieve करो, फिर जवाब दो" की जगह agent तय करता है कि search करना है या नहीं, कौन सा tool/index, कैसी query, और नतीजे काफ़ी अच्छे हैं या नहीं, और जब तक जवाब न बने तब तक loop चलाता है।

---

## 🔴 Problem it Solves
- Naive RAG always retrieves, even for "hello" (wasted tokens).
- One retrieval pass fails on multi-part questions ("compare duty on A and B").
- Data lives in many places (tariff PDFs, SQL, web); one vector index is not enough.
- Naive RAG cannot notice that retrieved chunks are irrelevant and try again.

## 🔴 यह क्यों बना? (Hindi)
- Naive RAG हमेशा retrieve करता है, "hello" पर भी (tokens बर्बाद)।
- एक बार का retrieval multi-part सवालों पर फ़ेल होता है ("A और B की duty compare करो")।
- Data कई जगह है (tariff PDFs, SQL, web); एक vector index काफ़ी नहीं।
- Naive RAG समझ नहीं पाता कि chunks बेकार हैं और दोबारा कोशिश नहीं करता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Give the agent tools: search_tariff_docs, query_sql, web_search
Step 2 → Agent reads the question and decides: answer directly or call a tool
Step 3 → It writes its own tool query (maybe splitting a hard question in parts)
Step 4 → Tool results come back as observations
Step 5 → Agent grades them: enough? If not, rewrite the query or pick another tool
Step 6 → Loop (with a max-step limit) until confident
Step 7 → Final grounded answer with sources
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Agent को tools दो: search_tariff_docs, query_sql, web_search
Step 2 → Agent सवाल पढ़कर तय करता है: सीधे जवाब दे या tool बुलाए
Step 3 → वो खुद tool query लिखता है (कठिन सवाल को हिस्सों में तोड़ सकता है)
Step 4 → Tool के नतीजे observation बनकर लौटते हैं
Step 5 → Agent जाँचता है: काफ़ी हैं? नहीं तो query बदलो या दूसरा tool चुनो
Step 6 → Max-step limit के साथ loop, जब तक भरोसा न हो
Step 7 → Sources के साथ final answer
```

---

## 🟡 Real World Example
**Tariff Classification System**: "Compare import duty on Bluetooth speakers and wired headphones, and tell me which HS chapter the speaker falls in." The agent (1) searches HS chapter rules for speakers, (2) searches duty for headphones, (3) sees one result is weak and rewrites the query, (4) combines both. A fixed pipeline would retrieve once and miss one half.
**Zomato AI**: "Cheap biryani near me that is open now": the agent uses a menu search, a location tool, and an opening-hours tool.

## 🟡 Real Example Hindi mein
**Tariff System**: "Bluetooth speaker और wired headphones की duty compare करो, और speaker किस HS chapter में आता है?" Agent (1) speaker के HS chapter rules खोजता है, (2) headphones की duty खोजता है, (3) एक नतीजा कमज़ोर दिखे तो query बदलता है, (4) दोनों जोड़ता है। Fixed pipeline एक बार retrieve करके एक हिस्सा छोड़ देता।
**Zomato AI**: "पास का सस्ता biryani जो अभी खुला हो": agent menu search, location और opening-hours tools इस्तेमाल करता है।

---

## 💻 Code Example — Basic
```python
# Pure Python agent loop with a rule-based "planner" standing in for the LLM (no API key)
from typing import Callable, Dict, List, Tuple

# Two tools the agent can use
DOCS = {"speaker": "Speakers: HS 8518.22, duty 20%.", "headphones": "Headphones: HS 8518.30, duty 10%."}

def search_docs(query: str) -> str:
    # Return every doc whose keyword appears in the query
    hits = [text for key, text in DOCS.items() if key in query.lower()]
    return " ".join(hits) if hits else "NO_RESULT"

def calculator(expr: str) -> str:
    # Tiny safe-ish calculator: digits and + - * / . ( ) only
    if not set(expr) <= set("0123456789+-*/.() "):
        return "ERROR"
    return str(eval(expr))  # demo only; never eval untrusted input in production

TOOLS: Dict[str, Callable[[str], str]] = {"search_docs": search_docs, "calculator": calculator}

def plan(question: str, observations: List[str]) -> Tuple[str, str]:
    """Mock LLM: decide next (tool, input) or ('final', answer)."""
    if not observations:                               # nothing known yet
        return ("search_docs", "speaker")              # first sub-question
    if len(observations) == 1:
        return ("search_docs", "headphones")           # second sub-question
    return ("final", " | ".join(observations))         # enough info: answer

def run_agent(question: str, max_steps: int = 5) -> str:
    obs: List[str] = []
    for step in range(max_steps):                      # hard limit prevents infinite loops
        action, arg = plan(question, obs)
        if action == "final":
            return arg
        result = TOOLS[action](arg)                    # call the chosen tool
        print(f"step {step}: {action}({arg!r}) -> {result}")
        obs.append(result)
    return "Stopped: step limit reached."

if __name__ == "__main__":
    print(run_agent("Compare duty on speakers and headphones"))
```

## 💻 Code Example — Advanced
```python
# Agentic RAG with OpenAI tool calling: async, typed, step limit, error handling
import asyncio
import json
from typing import Any

from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI()
MAX_STEPS = 5

TOOLS: list[dict[str, Any]] = [{
    "type": "function",
    "function": {
        "name": "search_tariff_docs",
        "description": "Search tariff documents for HS codes and duty rates.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Specific search query"}},
            "required": ["query"],
        },
    },
}]

async def search_tariff_docs(query: str) -> str:
    """Replace with a real vector search. Returns text or an explicit empty marker."""
    return f"[stub result for: {query}]"

async def agentic_rag(question: str) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "You answer tariff questions. Use search_tariff_docs when you "
                                       "need facts. Split multi-part questions into several searches. "
                                       "If results are weak, rewrite the query. Cite what you found."},
        {"role": "user", "content": question},
    ]
    tokens = 0
    for _ in range(MAX_STEPS):                                   # bounded loop
        try:
            resp = await client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, tools=TOOLS, temperature=0)
        except APIError as exc:
            return {"answer": "Service error.", "error": str(exc), "tokens": tokens}
        tokens += resp.usage.total_tokens if resp.usage else 0
        msg = resp.choices[0].message
        if not msg.tool_calls:                                   # agent decided to answer
            return {"answer": msg.content, "tokens": tokens}
        messages.append(msg.model_dump(exclude_none=True))       # keep assistant tool request
        results = await asyncio.gather(*[
            search_tariff_docs(**json.loads(tc.function.arguments)) for tc in msg.tool_calls
        ])                                                        # run searches in parallel
        for tc, out in zip(msg.tool_calls, results):
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": out})
    return {"answer": "Could not finish within the step limit.", "tokens": tokens}

if __name__ == "__main__":
    print(asyncio.run(agentic_rag("Compare duty on speakers and headphones")))  # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Expose the agent as one endpoint, add a timeout, and return the token count so you can monitor the cost of loops.

```python
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class Q(BaseModel):
    question: str = Field(min_length=3, max_length=1500)

@app.post("/agentic-ask")
async def agentic_ask(q: Q) -> dict:
    try:
        # Hard wall-clock limit: agents can loop slowly
        return await asyncio.wait_for(agentic_rag(q.question), timeout=30)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Agent timed out")
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph is the natural home: a graph with an `agent` node (LLM with tools) and a `tools` node, with a conditional edge looping back until no tool call is requested. The prebuilt `create_react_agent` does exactly this.

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

@tool
def search_tariff_docs(query: str) -> str:
    """Search tariff documents for HS codes and duty rates."""
    return "stub result"          # call your retriever here

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [search_tariff_docs])
result = agent.invoke(
    {"messages": [("user", "Compare duty on speakers and headphones")]},
    config={"recursion_limit": 10},      # caps loop steps
)
print(result["messages"][-1].content)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No step limit (infinite loop, runaway bill).
✅ Correct: Always cap steps and time.

```python
# Wrong
while True:
    step()
# Right
for _ in range(MAX_STEPS):
    step()
```

❌ Mistake 2: Vague tool descriptions, so the agent picks the wrong tool.
✅ Correct: Describe each tool's purpose, inputs, and when NOT to use it.

❌ Mistake 3: Using an agent when a fixed pipeline works (slower, costlier, less predictable).
✅ Correct: Start with naive or advanced RAG; add agency only for questions that need it.

---

## 🧠 Tricky Interview Question
**Q**: "Your agentic RAG has better accuracy than the fixed pipeline but 5x latency and cost. Leadership says keep accuracy. What do you do?"

**Answer**: Route instead of always using the agent. A cheap classifier (or rules) sends simple lookups to the fast pipeline and only complex or multi-part questions to the agent. Also use a smaller model for the agent, run tool calls in parallel, cache retrieval results, lower the step cap, and stream partial output. Measure accuracy per route, so you keep the gain where it matters.

---

## ⚫ Interview Questions + Answers

Q1: What makes RAG "agentic"?
A1: An LLM decides retrieval actions (whether, where, with which query, and when to stop) in a loop, instead of a fixed retrieve-then-generate pipeline.

Q2: Name two benefits over naive RAG.
A2: It skips retrieval when unnecessary, and it handles multi-hop or multi-source questions by issuing several targeted searches.

Q3: What are the main risks?
A3: Higher latency and cost, non-deterministic behaviour, loops, and wrong tool choices. Mitigate with step and time limits, clear tool descriptions, tracing, and evals.

Q4: How does agentic RAG relate to Self-RAG and Corrective RAG?
A4: They are specific patterns. Self-RAG has the model critique its own retrieval and answer. Corrective RAG grades retrieved docs and falls back to web search. Agentic RAG is the broader idea of tool-using control loops.

Q5: How would you evaluate and debug an agentic RAG system?
A5: Trace every step (LangSmith or OpenTelemetry). Evaluate final answer quality (faithfulness, correctness) AND trajectory quality (right tools, no wasted calls, steps used). Build a test set with simple, multi-hop, and unanswerable questions; track cost per question, and alert on step-limit hits.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Questions are multi-part or multi-hop
- Several data sources or tools exist
- Query quality varies and retries help

❌ Avoid when:
- Questions are simple FAQ lookups
- Latency or cost budget is tight
- You need fully predictable behaviour (compliance)

---

## 📊 Visual Diagram
```
        ┌──────────┐
 Q ───► │  AGENT   │◄─────────────┐ observations
        │  (LLM)   │              │
        └────┬─────┘              │
   needs info?│yes                │
        ┌────▼─────┐   ┌──────────┴───┐
        │ pick tool│──►│ vector search│
        │ + query  │──►│ SQL / web    │
        └────┬─────┘   └──────────────┘
             │no (enough info)
             ▼
        Final answer + sources      (max N steps)
```

---

## 💰 Cost Impact
- Each loop step re-sends the growing message list, so cost grows roughly quadratically with steps.
- Example: 4 steps with ~1500 input tokens each is ~6000 tokens + outputs, versus ~1500 for one-shot RAG (about 4x).
- Optimise: route simple questions away from the agent, small model for tools, parallel tool calls, trim tool outputs before returning them, cap steps, cache searches.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Agent | LLM that chooses actions | खुद फ़ैसले लेने वाला LLM |
| Tool | Function the agent can call | Agent का इस्तेमाल करने वाला function |
| Observation | Tool result fed back | Tool का नतीजा |
| ReAct | Reason + Act loop | सोचो और करो वाला loop |
| Multi-hop | Needs several linked lookups | कई जुड़े हुए खोजों वाला सवाल |
| Recursion limit | Max graph steps | अधिकतम steps की सीमा |

---

## ⚡ 3-Line Summary
English: Agentic RAG lets an LLM agent decide when, where and how to retrieve, looping until it has enough evidence. It beats fixed pipelines on complex questions but costs more and is less predictable. Always set step limits and route simple queries to cheaper paths.
Hindi: Agentic RAG में LLM agent तय करता है कि कब, कहाँ और कैसे retrieve करना है, और काफ़ी सबूत मिलने तक loop चलता है। जटिल सवालों पर ये fixed pipeline से बेहतर है पर महंगा और कम predictable है। हमेशा step limit लगाओ और आसान queries सस्ते रास्ते पर भेजो।

---

## ➡️ Next Topic
**225. Self-RAG**: the model critiques its own retrieval and answers, a specific agentic pattern.
