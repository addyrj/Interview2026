---

# 275. Parallel Tool Calls
# हिंदी में: Parallel Tool Calls (एक साथ कई Tool Calls)

---

## 🔵 Simple Definition (English)
Parallel tool calls means the model asks for **several tools in one reply** (for example 3 `get_duty` calls for 3 products). Your code then runs them at the same time (`asyncio.gather`), and sends all results back together. This saves round trips, time, and tokens compared with one tool call per model turn.

## 🔵 सरल परिभाषा (Hindi)
Parallel tool calls का मतलब है कि model **एक ही reply में कई tools** माँगता है (जैसे 3 products के लिए 3 `get_duty` calls)। आपका code उन्हें एक साथ (`asyncio.gather`) चलाता है और सारे results एक साथ वापस भेजता है। हर model turn में एक tool call की तुलना में round trips, समय और tokens बचते हैं।

---

## 🔴 Problem it Solves
- Sequential calls: model asks tool A, waits, asks tool B, waits, asks tool C = 3 model round trips.
- Each round trip re-sends the whole conversation (more input tokens) and adds latency.
- Independent lookups (three products) do not need to wait for each other.

## 🔴 यह क्यों बना? (Hindi)
- Sequential calls: model tool A माँगता है, रुकता है, फिर tool B, फिर tool C = 3 model round trips।
- हर round trip पूरी बातचीत दोबारा भेजता है (ज़्यादा input tokens) और latency बढ़ाता है।
- स्वतंत्र lookups (तीन products) को एक-दूसरे का इंतज़ार नहीं करना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Send messages + tools to the model (parallel_tool_calls=True is the default for OpenAI)
Step 2 → Model replies with ONE assistant message containing tool_calls: [call_1, call_2, call_3]
Step 3 → Append that assistant message to messages (exactly as received)
Step 4 → Run all calls concurrently: await asyncio.gather(*calls)
Step 5 → Append one {"role": "tool", "tool_call_id": id, "content": result} per call
Step 6 → Call the model again with all results
Step 7 → Model writes the final answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → messages + tools model को भेजो (OpenAI में parallel_tool_calls=True default है)
Step 2 → Model एक ही assistant message में tool_calls: [call_1, call_2, call_3] देता है
Step 3 → वो assistant message जस का तस messages में जोड़ो
Step 4 → सब calls एक साथ चलाओ: await asyncio.gather(*calls)
Step 5 → हर call के लिए एक {"role": "tool", "tool_call_id": id, "content": result} जोड़ो
Step 6 → सारे results के साथ model को फिर बुलाओ
Step 7 → Model final जवाब लिखता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A broker asks for duty on speakers, headphones and power banks. The model returns 3 `get_duty` tool calls in one message. They run concurrently against the tariff DB in ~200 ms instead of ~600 ms, and only one extra model call is needed.
**Zomato AI**: "Compare delivery time from 3 restaurants" triggers 3 simultaneous `get_eta` calls.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker speakers, headphones और power banks की duty पूछता है। Model एक message में 3 `get_duty` tool calls देता है। ये tariff DB पर एक साथ ~200 ms में चलती हैं (क्रम से ~600 ms लगते), और सिर्फ़ एक extra model call चाहिए।
**Zomato AI**: "3 restaurants का delivery time compare करो" पर 3 `get_eta` calls एक साथ चलती हैं।

---

## 💻 Code Example — Basic
```python
# Basic: run several tool calls concurrently vs sequentially (pure Python, runnable offline)
import asyncio
import time
from typing import Any, Dict, List

DUTY = {"speakers": 20, "headphones": 10, "power banks": 10}

async def get_duty(product: str) -> Dict[str, Any]:
    await asyncio.sleep(0.2)                                  # pretend a 200 ms database lookup
    return {"product": product, "duty_percent": DUTY.get(product, -1)}

async def sequential(products: List[str]) -> List[Dict[str, Any]]:
    return [await get_duty(p) for p in products]              # one after another

async def parallel(products: List[str]) -> List[Dict[str, Any]]:
    return list(await asyncio.gather(*(get_duty(p) for p in products)))   # all at once

async def main() -> None:
    products = ["speakers", "headphones", "power banks"]
    t = time.perf_counter(); await sequential(products)
    print(f"sequential: {time.perf_counter() - t:.2f}s")       # ~0.6 s
    t = time.perf_counter(); res = await parallel(products)
    print(f"parallel:   {time.perf_counter() - t:.2f}s")       # ~0.2 s
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
```python
# Production parallel tool loop with OpenAI: concurrency limit, per-tool errors, timeouts
import asyncio
import json
from typing import Any

from openai import AsyncOpenAI, APIError  # openai>=1

client = AsyncOpenAI()
MAX_CONCURRENCY = 5                                   # protect the downstream DB
TOOL_TIMEOUT_S = 5.0

TOOLS: list[dict[str, Any]] = [{
    "type": "function",
    "function": {
        "name": "get_duty",
        "description": "Get import duty percent for one product.",
        "parameters": {
            "type": "object",
            "properties": {"product": {"type": "string"}},
            "required": ["product"],
        },
    },
}]

async def get_duty(product: str) -> dict[str, Any]:
    await asyncio.sleep(0.1)                          # replace with a real DB call
    return {"product": product, "duty_percent": 10}

REGISTRY = {"get_duty": get_duty}
sem = asyncio.Semaphore(MAX_CONCURRENCY)

async def run_one(call: Any) -> dict[str, str]:
    """Run a single tool call; ALWAYS return a tool message (even on failure)."""
    try:
        args = json.loads(call.function.arguments)                    # model-provided JSON
        async with sem:                                               # limit concurrency
            result = await asyncio.wait_for(REGISTRY[call.function.name](**args), TOOL_TIMEOUT_S)
        content = json.dumps(result)
    except KeyError:
        content = json.dumps({"error": f"unknown tool {call.function.name}"})
    except asyncio.TimeoutError:
        content = json.dumps({"error": "tool timed out"})
    except (ValueError, TypeError) as exc:                            # bad JSON or bad arguments
        content = json.dumps({"error": f"bad arguments: {exc}"})
    return {"role": "tool", "tool_call_id": call.id, "content": content}

async def answer(question: str) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    try:
        first = await client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=TOOLS, parallel_tool_calls=True)
        msg = first.choices[0].message
        if not msg.tool_calls:
            return {"answer": msg.content}
        messages.append(msg.model_dump(exclude_none=True))            # keep the assistant tool request
        results = await asyncio.gather(*(run_one(c) for c in msg.tool_calls))   # parallel
        messages.extend(results)                                      # one tool message per call
        final = await client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return {"answer": final.choices[0].message.content, "tool_calls": len(msg.tool_calls)}
    except APIError as exc:
        return {"error": str(exc)}

if __name__ == "__main__":
    print(asyncio.run(answer("Duty on speakers, headphones and power banks?")))   # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
FastAPI is already async, so `gather` runs inside the request without extra threads. Add an overall timeout.

```python
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class Q(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

@app.post("/duty")
async def duty(q: Q) -> dict:
    try:
        result = await asyncio.wait_for(answer(q.question), timeout=30)   # whole request limit
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="timed out")
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return result
```

---

## 🔗 LangChain / LangGraph Connection
LangChain chat models with `bind_tools` return `AIMessage.tool_calls` (a list). LangGraph's prebuilt `ToolNode` executes all tool calls from the last AI message **concurrently** and returns one `ToolMessage` per call. `create_react_agent` uses it.

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

@tool
def get_duty(product: str) -> str:
    """Get import duty percent for one product."""
    return f"{product}: 10%"

llm = ChatOpenAI(model="gpt-4o-mini").bind_tools([get_duty])
ai = llm.invoke("Duty on speakers and power banks?")
print(len(ai.tool_calls))                       # often 2 (parallel)
tool_node = ToolNode([get_duty])
out = tool_node.invoke({"messages": [ai]})      # runs all calls, returns ToolMessages
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not answering every `tool_call_id` (API error).
✅ Correct: One tool message per call, even failures.

```python
# Wrong: only the first result sent back
messages.append({"role": "tool", "tool_call_id": calls[0].id, "content": r0})
# Right: all of them
for c, r in zip(calls, results):
    messages.append({"role": "tool", "tool_call_id": c.id, "content": r})
```

❌ Mistake 2: Running parallel calls that depend on each other (call B needs A's output).
✅ Correct: Dependent calls must be sequential; the model usually knows, but guard in code and prompt.

❌ Mistake 3: Unlimited concurrency (50 calls hammer your DB).
✅ Correct: Semaphore and a max number of tool calls per turn.

---

## 🧠 Tricky Interview Question
**Q**: "Two parallel tool calls both write to the same account balance. Sometimes the final balance is wrong. Why, and what do you do?"

**Answer**: Parallel calls are concurrent, so read-modify-write operations race (lost updates). Parallelism is safe for independent, read-only (idempotent) tools. For writes: disable parallel calls (`parallel_tool_calls=False`), or make tools transactional/idempotent (database transactions, optimistic locking, idempotency keys), or serialise writes with a lock. Also consider that the model may issue duplicate calls, so use idempotency keys.

---

## ⚫ Interview Questions + Answers

Q1: What are parallel tool calls?
A1: The model returns multiple tool calls in a single assistant message so they can be executed together.

Q2: How do you turn them off in the OpenAI API?
A2: Set `parallel_tool_calls=False` in the request. (In Anthropic, set `disable_parallel_tool_use=true` in `tool_choice`.)

Q3: What do you send back after running them?
A3: One tool-result message per call, each referencing its `tool_call_id` (OpenAI) or `tool_use_id` (Claude), in a single next request.

Q4: When should parallelism be avoided?
A4: Dependent calls, non-idempotent writes, strict ordering, or rate-limited downstream APIs.

Q5: How do parallel tool calls change cost and latency?
A5: Fewer model round trips: each saved round trip avoids re-sending the full context (input tokens) and the model's latency; tool latency becomes max(tool times) instead of the sum. But the arguments for N calls are generated in one output, so output tokens are roughly the same. Add concurrency limits so the downstream does not become the bottleneck.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Independent lookups (several products, cities, users)
- Read-only tools
- Latency matters

❌ Avoid when:
- Calls depend on each other
- Write operations that are not idempotent
- Downstream rate limits are tight

---

## 📊 Visual Diagram
```
 SEQUENTIAL                                PARALLEL
 model → call A → tool A → model           model → [call A, call B, call C]
 model → call B → tool B → model                     │       │       │
 model → call C → tool C → model                  tool A  tool B  tool C   (run together)
 model → final answer                                 └──────┬───────┘
 (3 round trips)                                           model → final answer
                                                           (1 round trip)
```

---

## 💰 Cost Impact
- Sequential: 3 tool rounds each re-send the conversation, e.g. 3 x ~800 input tokens = 2400 input tokens. Parallel: the first call (~600) + final call (~900) = ~1500 input tokens.
- Latency drops by about the number of saved model round trips (often 1-3 seconds each).
- Optimise: keep tool descriptions short (they are sent each call), return compact tool results (trim JSON), limit tools per turn, and cache repeated lookups.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parallel tool calls | Many tool calls in one reply | एक reply में कई tool calls |
| tool_call_id | Id linking result to call | Result को call से जोड़ने वाली id |
| asyncio.gather | Run coroutines concurrently | Coroutines एक साथ चलाना |
| Idempotent | Safe to repeat | दोहराने पर भी वही असर |
| Semaphore | Concurrency limiter | एक साथ चलने वालों की सीमा |
| ToolNode | LangGraph tool executor | LangGraph का tool चलाने वाला node |

---

## ⚡ 3-Line Summary
English: Parallel tool calls let the model request many independent tools in one message so you run them together. You must return one result per call id. Use for independent reads, avoid for dependent or non-idempotent writes.
Hindi: Parallel tool calls में model एक message में कई स्वतंत्र tools माँगता है और आप उन्हें साथ चलाते हैं। हर call id के लिए एक result लौटाना ज़रूरी है। स्वतंत्र reads के लिए इस्तेमाल करो; dependent या non-idempotent writes के लिए नहीं।

---

## ➡️ Next Topic
**276. Tool Results Handling**: how to format, trim, and validate what you send back to the model.
