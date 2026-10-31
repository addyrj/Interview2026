---

# 346. Multi-Agent — What + Why
# हिंदी में: Multi-Agent — क्या और क्यों

---

## 🔵 Simple Definition (English)
A multi-agent system is an application where several LLM-powered agents, each with its own role, prompt and tools, work together on one task. Instead of one giant prompt doing everything, the work is split between small focused agents. A coordinator (or a shared state) joins their results.

## 🔵 सरल परिभाषा (Hindi)
Multi-agent system वह application है जिसमें कई LLM agents, हर एक अपने role, prompt और tools के साथ, मिलकर एक task करते हैं। एक बड़े prompt की जगह काम छोटे focused agents में बँट जाता है। एक coordinator (या shared state) सबके results जोड़ता है।

---

## 🔴 Problem it Solves
- One agent with 30 tools and a 5,000-token prompt gets confused: it picks the wrong tool and forgets instructions.
- One long context mixes unrelated work (research + writing + validation), so quality drops and cost grows.
- A single agent cannot work in parallel, and one failure breaks the whole run.
- It is hard to test, debug or improve one huge prompt. A small agent with one job is easy to test.

## 🔴 यह क्यों बना? (Hindi)
- 30 tools और 5,000-token prompt वाला एक agent confuse हो जाता है, गलत tool चुनता है।
- एक लंबे context में research, writing, validation सब मिल जाते हैं, quality गिरती है और cost बढ़ती है।
- एक agent parallel काम नहीं कर सकता, और एक failure पूरा run तोड़ देती है।
- एक बड़े prompt को test/debug करना मुश्किल है; छोटा agent आसानी से test होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User sends a task (e.g. "Classify this product and write a customs note")
Step 2 → Coordinator decides which agents are needed
Step 3 → Each agent gets ONLY its own instructions + the slice of input it needs
Step 4 → Agents run (sequentially or in parallel), each may call its own tools
Step 5 → Outputs are written to shared state or passed as messages
Step 6 → Coordinator merges outputs, checks quality, may loop back
Step 7 → Final answer + token usage are returned to the user
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User task भेजता है (जैसे "इस product को classify करो और customs note लिखो")
Step 2 → Coordinator तय करता है कौन से agents चाहिए
Step 3 → हर agent को सिर्फ अपनी instructions + ज़रूरी input मिलता है
Step 4 → Agents चलते हैं (क्रम से या parallel), अपने tools call करते हैं
Step 5 → Output shared state में लिखा जाता है या message के रूप में जाता है
Step 6 → Coordinator outputs merge करता है, quality check करता है, ज़रूरत पर loop back
Step 7 → Final answer + token usage user को वापस
```

---

## 🟡 Real World Example
**Tariff Classification System**: One agent reads the product description and extracts attributes (material, use, chapter hints). A second agent searches the HS code database. A third agent validates the code against customs rules. A fourth writes the explanation for the importer. Each agent has a small prompt and 1-2 tools, so each is accurate and cheap to test.

**Zomato-style**: "Plan a birthday dinner for 10" splits into a restaurant-search agent, a menu/diet agent and a booking agent running in parallel. **Amazon-style**: a returns request goes to an order-lookup agent, a policy agent and a refund agent.

## 🟡 Real Example Hindi mein
**Tariff System**: पहला agent product description से attributes निकालता है। दूसरा HS code database search करता है। तीसरा customs rules से code validate करता है। चौथा importer के लिए explanation लिखता है। हर agent का prompt छोटा और 1-2 tools, इसलिए accurate और test करने में सस्ता।

**Zomato**: "10 लोगों की birthday dinner" restaurant-search, menu/diet और booking agents में parallel बँट जाती है। **Amazon**: return request order-lookup, policy और refund agents के पास जाती है।

---

## 💻 Code Example — Basic
```python
# Basic multi-agent idea with a fake LLM, so it runs offline with no API key
from dataclasses import dataclass  # dataclass gives a tiny, typed container


def fake_llm(role: str, task: str) -> str:  # stand-in for a real LLM call
    return f"[{role}] handled: {task}"  # echo so we can see who did what


@dataclass  # an agent is just a role + an instruction
class Agent:
    name: str  # agent name, used in logs
    instruction: str  # the system prompt for this agent

    def run(self, task: str) -> str:  # one agent step
        return fake_llm(self.name, f"{self.instruction} | {task}")  # call the LLM


extractor = Agent("extractor", "Extract product attributes")  # agent 1
searcher = Agent("searcher", "Find candidate HS codes")  # agent 2
validator = Agent("validator", "Validate HS code")  # agent 3

task = "cotton t-shirt, knitted"  # the user's input
attrs = extractor.run(task)  # step 1 output
codes = searcher.run(attrs)  # step 2 uses step 1 output
final = validator.run(codes)  # step 3 uses step 2 output
print(final)  # show the chain result
```

## 💻 Code Example — Advanced
```python
# Production-style: typed agents, parallel fan-out, error handling, token tracking
import asyncio  # async runtime
from dataclasses import dataclass, field  # typed containers
from typing import Awaitable, Callable  # type hints for callables

LLMFn = Callable[[str, str], Awaitable[tuple[str, int]]]  # returns (text, tokens)


async def mock_llm(role: str, prompt: str) -> tuple[str, int]:  # offline mock
    await asyncio.sleep(0.01)  # simulate network latency
    if "FAIL" in prompt:  # simulate a broken agent
        raise RuntimeError(f"{role} failed")  # raise like a real API error
    return f"{role}: ok({prompt[:30]})", len(prompt.split()) + 5  # fake text + tokens


@dataclass
class AgentResult:
    name: str  # which agent produced this
    text: str = ""  # output text
    tokens: int = 0  # tokens used
    error: str | None = None  # error message if any


@dataclass
class MultiAgentRunner:
    llm: LLMFn  # injected LLM function (real or mock)
    results: list[AgentResult] = field(default_factory=list)  # collected outputs

    async def run_agent(self, name: str, prompt: str) -> AgentResult:  # one agent
        try:  # protect the whole run from one failure
            text, tokens = await self.llm(name, prompt)  # call the model
            return AgentResult(name, text, tokens)  # success result
        except Exception as exc:  # any provider/network error
            return AgentResult(name, error=str(exc))  # keep the error, don't crash

    async def fan_out(self, prompt: str, names: list[str]) -> list[AgentResult]:
        tasks = [self.run_agent(n, prompt) for n in names]  # build coroutines
        self.results = await asyncio.gather(*tasks)  # run in parallel
        return self.results  # give results back

    def total_tokens(self) -> int:  # cost tracking
        return sum(r.tokens for r in self.results)  # add all agent tokens


async def main() -> None:
    runner = MultiAgentRunner(mock_llm)  # create runner with mock LLM
    out = await runner.fan_out("cotton t-shirt", ["attrs", "search", "legal"])
    for r in out:  # print every agent result
        print(r.name, r.error or r.text)  # show error or text
    print("tokens:", runner.total_tokens())  # total token usage


if __name__ == "__main__":
    asyncio.run(main())  # start the event loop
```

---

## 🟠 FastAPI Integration
Each request starts a fresh multi-agent run. Use `async` routes so the server is not blocked while agents wait for the LLM, and return token usage so you can see cost per request.

```python
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # request/response models

app = FastAPI()  # create app


class ClassifyRequest(BaseModel):
    description: str  # product description


class ClassifyResponse(BaseModel):
    answer: str  # final answer
    agents_used: list[str]  # which agents ran
    total_tokens: int  # cost visibility


async def run_pipeline(desc: str) -> tuple[str, list[str], int]:  # placeholder pipeline
    agents = ["extractor", "searcher", "validator"]  # the team
    return f"HS code candidate for: {desc}", agents, 180  # fake output


@app.post("/classify", response_model=ClassifyResponse)
async def classify(req: ClassifyRequest) -> ClassifyResponse:
    if not req.description.strip():  # validate input
        raise HTTPException(status_code=422, detail="empty description")
    try:  # protect against agent errors
        answer, agents, tokens = await run_pipeline(req.description)
    except Exception as exc:  # map to a clean API error
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ClassifyResponse(answer=answer, agents_used=agents, total_tokens=tokens)
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph models a multi-agent system as a graph: each node is an agent, edges decide who runs next, and a shared `State` carries data.

```python
from typing import TypedDict  # state schema
from langgraph.graph import StateGraph, START, END  # graph builder


class State(TypedDict):
    task: str  # user input
    attrs: str  # extractor output
    code: str  # searcher output


def extractor(state: State) -> dict:  # node 1 (would call an LLM)
    return {"attrs": f"attrs({state['task']})"}  # partial state update


def searcher(state: State) -> dict:  # node 2
    return {"code": f"6109.10 for {state['attrs']}"}  # partial update


g = StateGraph(State)  # create graph
g.add_node("extractor", extractor)  # register agent
g.add_node("searcher", searcher)  # register agent
g.add_edge(START, "extractor")  # entry point
g.add_edge("extractor", "searcher")  # order
g.add_edge("searcher", END)  # finish
app_graph = g.compile()  # build runnable
print(app_graph.invoke({"task": "cotton t-shirt", "attrs": "", "code": ""}))
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using multi-agent for a task one prompt can solve.
✅ Correct: Start with one agent; split only when you measure confusion, long context or a need for parallelism.

```python
# Wrong: 5 agents to answer "What is HS code 6109?"
# answer = planner(researcher(writer(critic(user_q))))  # 4 extra LLM calls for nothing

# Right: single call, add agents only if quality tests fail
def answer(q: str) -> str:
    return fake_llm("single", q)  # one call is enough
```

❌ Mistake 2: Passing the full conversation to every agent.
✅ Correct: Give each agent only the slice it needs.

```python
# Wrong: each agent receives everything
history = ["msg"] * 5000
# for a in agents: a.run(history)  # token cost multiplies by number of agents

# Right: pass a small, filtered input
needed = history[-5:]  # only the relevant recent items
```

---

## 🧠 Tricky Interview Question
**Q**: "You split a working single-agent bot into 4 agents. Accuracy did not improve but cost tripled. Why, and what do you do?"

**Answer**: Each agent adds an LLM call, repeated system prompts and handoff text, so tokens multiply. If the original task did not suffer from tool confusion or long context, splitting only adds overhead and new failure points (lost information at handoffs). Fix: measure per-agent contribution, merge agents that do trivial work back into code or one prompt, use a cheap model for simple agents, pass minimal context, and keep multi-agent only where it improves a metric.

---

## ⚫ Interview Questions + Answers

Q1: What is a multi-agent system?
A1: Several LLM agents with different roles/tools that cooperate on one goal, coordinated by a supervisor, a graph or a shared state.

Q2: Name two benefits of multi-agent design.
A2: Specialisation (small prompt, few tools, higher accuracy) and parallelism or modularity (test, replace or scale each agent separately).

Q3: What are the main costs of multi-agent systems?
A3: More LLM calls (cost, latency), handoff information loss, harder debugging, and more failure modes such as loops or conflicting outputs.

Q4: Single agent with tools versus multi-agent: how do you choose?
A4: Use a single agent when tools are few (under about 10) and context is short. Move to multi-agent when tool selection errors rise, prompts become huge, tasks are independent (parallel) or need different models/permissions.

Q5: How would you design a multi-agent tariff system to be reliable at scale?
A5: Typed state between agents (Pydantic), small agents with one tool each, a validator agent plus deterministic code checks, timeouts and retries per agent, a max-step limit to prevent loops, cheap models for extraction and a strong model only for final reasoning, tracing (LangSmith) and an offline evaluation set measuring accuracy, cost and latency per agent.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Task has clearly different sub-skills (search, reasoning, validation)
- Sub-tasks can run in parallel
- You need different tools, permissions or models per step
- One prompt has grown too big to maintain

❌ Avoid when:
- A single prompt or a simple chain solves it
- Latency and cost budgets are tight
- You cannot measure quality, so you cannot prove the split helps

---

## 📊 Visual Diagram
```
                 User task
                     │
              ┌──────▼──────┐
              │ Coordinator │
              └──┬───┬───┬──┘
        ┌────────┘   │   └────────┐
   ┌────▼───┐  ┌─────▼────┐  ┌────▼─────┐
   │Extractor│  │ Searcher │  │ Validator│
   │ (LLM)  │  │ (LLM+DB) │  │ (LLM+rules)│
   └────┬───┘  └─────┬────┘  └────┬─────┘
        └────────┐   │   ┌────────┘
              ┌──▼───▼───▼──┐
              │ Shared State │
              └──────┬──────┘
                     ▼
               Final answer
```

---

## 💰 Cost Impact
Total tokens ≈ sum over agents of (system prompt + input + output). Three agents with 500-token prompts and 300-token outputs cost about 3x one agent of the same size, plus handoff text.

Optimisation:
- Cheap model (gpt-4o-mini) for extraction/routing, strong model only where reasoning is needed
- Pass only needed fields, not the whole history
- Cache repeated system prompts (prompt caching) and repeated queries
- Cap steps and `max_tokens` per agent
- Replace deterministic agents with plain Python code

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Agent | LLM + prompt + tools with one role | एक role वाला LLM agent |
| Multi-agent | Several agents cooperating | कई agents का team |
| Coordinator | Decides who runs next | अगला agent तय करने वाला |
| Handoff | Passing work between agents | काम एक agent से दूसरे को देना |
| Shared state | Data all agents read/write | सभी agents का साझा data |
| Fan-out | Run agents in parallel | agents को parallel चलाना |

---

## ⚡ 3-Line Summary
English: Multi-agent splits one big job into small role-based LLM agents. It improves accuracy, modularity and parallelism, but adds cost, latency and complexity. Start with one agent and split only when measurements justify it.
Hindi: Multi-agent एक बड़े काम को छोटे role-based LLM agents में बाँटता है। इससे accuracy, modularity और parallelism मिलती है, पर cost, latency और complexity बढ़ती है। पहले एक agent से शुरू करो, measure करने के बाद ही split करो।

---

## ➡️ Next Topic
**347. Agent Types + Roles** — the common kinds of agents (router, researcher, executor, critic) and how to define a clear role for each.
