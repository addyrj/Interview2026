---

# 047. OpenAI Assistants API
# हिंदी में: OpenAI Assistants API

---

## 🔵 Simple Definition (English)
The Assistants API was OpenAI's stateful agent API built from four objects: an Assistant (model + instructions + tools), a Thread (conversation), Messages, and Runs (one execution of the assistant on a thread). It had built-in tools (code interpreter, file search). OpenAI has deprecated it in favour of the Responses API, so learn it mainly for legacy code and interviews. Check the official docs for the current sunset date.

## 🔵 सरल परिभाषा (Hindi)
Assistants API OpenAI का stateful agent API था जिसमें चार objects होते हैं: Assistant (model + instructions + tools), Thread (conversation), Messages और Run (thread पर assistant का एक execution)। इसमें built-in tools (code interpreter, file search) थे। OpenAI ने इसे deprecate करके Responses API की ओर बढ़ाया है, इसलिए इसे mainly legacy code और interviews के लिए समझो। Sunset date के लिए official docs देखो।

---

## 🔴 Problem it Solves
- Developers had to store chat history and re-send it on every call.
- Tool use (code execution, retrieval over files) had to be built by hand.
- Long conversations needed truncation logic.
- Assistants gave a hosted "agent" with memory, files and tools out of the box.

## 🔴 यह क्यों बना? (Hindi)
- Developers को chat history खुद store करके हर call में भेजनी पड़ती थी।
- Tool use (code execution, files पर retrieval) हाथ से बनाना पड़ता था।
- लंबी conversations के लिए truncation logic चाहिए था।
- Assistants ने memory, files और tools वाला hosted "agent" तैयार दिया।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create an Assistant once (model, instructions, tools)
Step 2 → Create a Thread per conversation/user
Step 3 → Add a Message (role=user) to the Thread
Step 4 → Create a Run (thread_id + assistant_id)
Step 5 → Poll the Run status: queued -> in_progress -> requires_action / completed / failed
Step 6 → If requires_action: execute your function tools, submit tool outputs
Step 7 → When completed: list the Thread messages and read the newest assistant message
Step 8 → Read run.usage for token counts
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → एक बार Assistant बनाओ (model, instructions, tools)
Step 2 → हर conversation/user के लिए Thread बनाओ
Step 3 → Thread में Message (role=user) जोड़ो
Step 4 → Run बनाओ (thread_id + assistant_id)
Step 5 → Run status poll करो: queued -> in_progress -> requires_action / completed / failed
Step 6 → requires_action हो तो अपने function tools चलाओ और outputs submit करो
Step 7 → completed पर Thread messages list करो और नया assistant message पढ़ो
Step 8 → Token counts के लिए run.usage पढ़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A legacy version used one Assistant "TariffBot" with file search over the HS code handbook. Each customs officer got a Thread. When the officer asked "classify wireless earbuds", we added a message and created a run; the assistant searched the handbook and answered. This worked but polling added latency, and retrieval cost was hard to predict, so the team is migrating to the Responses API plus its own vector store.

**Zomato-style**: A restaurant-owner helper that remembers each owner's menu in a Thread and uses the code interpreter to make sales charts.

## 🟡 Real Example Hindi mein
**Tariff System**: Legacy version में एक Assistant "TariffBot" था जो HS code handbook पर file search करता था। हर customs officer का एक Thread था। Officer "classify wireless earbuds" पूछता तो message जोड़कर run बनता; assistant handbook search करके जवाब देता। यह चलता था, पर polling से latency बढ़ती थी और retrieval cost का अंदाज़ा मुश्किल था, इसलिए team Responses API + अपने vector store पर migrate कर रही है।

**Zomato-style**: Restaurant-owner helper जो हर owner का menu Thread में याद रखता है और sales charts के लिए code interpreter इस्तेमाल करता है।

---

## 💻 Code Example — Basic
```python
# Basic: the Assistants API object flow (legacy; needs OPENAI_API_KEY and openai>=1)
# Note: on current SDK versions the Assistants API lives under client.beta.*
import time  # for polling sleep
from openai import OpenAI  # sync client

client = OpenAI()  # create client

assistant = client.beta.assistants.create(  # 1. create assistant (once)
    name="TariffBot",  # display name
    model="gpt-4o-mini",  # model
    instructions="You classify products into HS codes. Be brief.",  # behaviour
)

thread = client.beta.threads.create()  # 2. one thread per conversation

client.beta.threads.messages.create(  # 3. add user message
    thread_id=thread.id,  # which thread
    role="user",  # who is speaking
    content="HS chapter for wireless earbuds?",  # text
)

run = client.beta.threads.runs.create(  # 4. start a run
    thread_id=thread.id,  # thread to run on
    assistant_id=assistant.id,  # which assistant
)

while run.status in ("queued", "in_progress"):  # 5. poll until finished
    time.sleep(1)  # wait one second
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)  # refresh

if run.status == "completed":  # success
    msgs = client.beta.threads.messages.list(thread_id=thread.id, order="desc", limit=1)  # newest
    print(msgs.data[0].content[0].text.value)  # print assistant text
else:
    print("Run ended with status:", run.status)  # failed / expired / cancelled
```

## 💻 Code Example — Advanced
```python
# Production-style: async run with timeout, function tool outputs and error handling
import asyncio  # async runtime
import json  # parse tool args
from openai import AsyncOpenAI, APIError  # async client

client = AsyncOpenAI()  # shared client

def lookup_hs_code(keyword: str) -> dict[str, str]:
    db = {"earbuds": "8518.30"}  # fake data
    return {"hs_code": db.get(keyword.lower(), "unknown")}

async def ask(assistant_id: str, thread_id: str, text: str, timeout_s: float = 60.0) -> str:
    try:
        await client.beta.threads.messages.create(  # add user message
            thread_id=thread_id, role="user", content=text)
        run = await client.beta.threads.runs.create(  # start run
            thread_id=thread_id, assistant_id=assistant_id)
        loop = asyncio.get_running_loop()  # clock
        deadline = loop.time() + timeout_s  # absolute deadline
        while True:
            run = await client.beta.threads.runs.retrieve(  # refresh status
                thread_id=thread_id, run_id=run.id)
            if run.status == "completed":  # done
                break
            if run.status == "requires_action":  # model wants our tools
                outputs = []  # tool outputs to send
                for call in run.required_action.submit_tool_outputs.tool_calls:
                    args = json.loads(call.function.arguments)  # parse JSON args
                    result = lookup_hs_code(**args)  # run function
                    outputs.append({"tool_call_id": call.id, "output": json.dumps(result)})
                run = await client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id, run_id=run.id, tool_outputs=outputs)
                continue  # go back to polling
            if run.status in ("failed", "cancelled", "expired"):  # terminal errors
                raise RuntimeError(f"Run {run.status}: {run.last_error}")
            if loop.time() > deadline:  # too slow
                await client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run.id)
                raise TimeoutError("Assistant run timed out")
            await asyncio.sleep(0.7)  # polite polling interval
        msgs = await client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1)
        return msgs.data[0].content[0].text.value  # final text
    except APIError as exc:  # network / API errors
        raise RuntimeError(f"OpenAI API error: {exc}") from exc
```

---

## 🟠 FastAPI Integration
Map each logged-in user to a thread id (store it in a DB). The route sends the user's text to their thread and returns the answer.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app
ASSISTANT_ID = "asst_xxx"  # created once at deploy time
THREADS: dict[str, str] = {}  # user_id -> thread_id (use a DB in production)

class Q(BaseModel):
    user_id: str  # who is asking
    text: str  # question

@app.post("/assistant")
async def assistant(q: Q) -> dict:
    if q.user_id not in THREADS:  # first message from this user
        t = await client.beta.threads.create()  # new thread
        THREADS[q.user_id] = t.id
    try:
        answer = await ask(ASSISTANT_ID, THREADS[q.user_id], q.text)  # from advanced code
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Assistant timed out")
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"answer": answer}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `OpenAIAssistantRunnable` (in `langchain_community`/`langchain-openai` depending on version) to wrap an assistant as a Runnable. However, since Assistants is deprecated, new LangChain projects should use LangGraph, which keeps state in a checkpointer (thread_id in config) and gives full control of the tool loop.

```python
# LangGraph equivalent of "Thread": a checkpointer keyed by thread_id
from langgraph.checkpoint.memory import MemorySaver  # in-memory state store
from langgraph.prebuilt import create_react_agent  # ready-made tool agent
from langchain_openai import ChatOpenAI  # model

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools=[], checkpointer=MemorySaver())
cfg = {"configurable": {"thread_id": "officer-42"}}  # same idea as an Assistants thread
# agent.invoke({"messages": [("user", "HS chapter for earbuds?")]}, cfg)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Starting a new project on Assistants
✅ Correct: Use the Responses API (or LangGraph) for new work.

```python
# Wrong: client.beta.assistants.create(...)  # deprecated path for new apps
# Right: client.responses.create(...)  # recommended path
```

❌ Mistake 2: Polling forever or too fast
✅ Correct: Add timeout, sleep between polls, and cancel stuck runs.

```python
# Wrong:
# while run.status != "completed": run = client.beta.threads.runs.retrieve(...)
# Right: sleep 0.5-1s, deadline check, handle failed/expired/requires_action
```

---

## 🧠 Tricky Interview Question
**Q**: "Your Assistants thread has 2,000 messages and every reply costs more and more. Why, and what do you do?"

**Answer**: Each run sends thread context to the model, billed as input tokens. Long threads grow cost and latency, and old context is truncated automatically (by default, the system truncates to fit the context window). Fix: set `truncation_strategy` (for example last N messages) on the run, summarise old turns, start a new thread per task, or migrate to a design where you control the context (Responses API with your own memory or LangGraph).

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Name the four core objects of the Assistants API.
A1: Assistant, Thread, Message, Run.

Q2: [Easy] What does a Thread do?
A2: It stores the conversation messages server-side so you do not resend history manually.

Q3: [Medium] Why is a Run asynchronous and how do you get the result?
A3: A run may call tools and takes time, so it moves through statuses. You poll (or stream) until `completed`, then list thread messages. Handle `requires_action` by submitting tool outputs.

Q4: [Medium] What built-in tools exist?
A4: Code interpreter (runs Python in a sandbox), file search (retrieval over uploaded files in vector stores), and your own function tools.

Q5: [Hard] Why did OpenAI move to the Responses API, and how would you migrate?
A5: Assistants required polling, extra objects and gave less control. Responses is simpler, supports the same tool ideas, and returns items directly. Migration: convert Assistant config into `instructions` + `tools` per request, move vector stores to file search tool config, replace Threads with `previous_response_id` or Conversations/your DB, replace run polling with a direct call or streaming, and re-run evals.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Maintaining an existing legacy app (until migration)
- Answering interview questions about OpenAI's history

❌ Avoid when:
- Starting any new project (deprecated)
- You need provider-neutral code or tight control of cost and context

---

## 📊 Visual Diagram
```
 Assistant (model + instructions + tools)
        |
        |   Thread (conversation, stores Messages)
        |      |
        +------+--> Run -- status: queued -> in_progress
                         |
             requires_action? -- yes --> your function -> submit_tool_outputs
                         |
                      completed -> list Messages -> latest assistant message
```

---

## 💰 Cost Impact
- You pay for model tokens (input = thread context + instructions + tool results, output = reply). Tools add their own fees (code interpreter sessions, file search storage and calls); check the current pricing page.
- Long threads inflate input tokens on every run. Use `truncation_strategy`, new threads per task, and short instructions.
- Optimise by using small models, limiting retrieved chunks, and migrating to Responses/LangGraph where you control context size.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Assistant | Configured agent | Configured agent |
| Thread | Stored conversation | Saved conversation |
| Run | One execution on a thread | Thread पर एक execution |
| requires_action | Run waits for tool outputs | Tool outputs का इंतज़ार |
| File search | Retrieval over uploaded files | Files पर retrieval |
| Deprecated | Being phased out | हटाया जा रहा |

---

## ⚡ 3-Line Summary
English: Assistants API = Assistant + Thread + Message + Run with polling and built-in tools. It is deprecated in favour of the Responses API. Know it for legacy code and for migration questions.
Hindi: Assistants API = Assistant + Thread + Message + Run, polling और built-in tools के साथ। इसे Responses API के पक्ष में deprecate किया गया है। Legacy code और migration सवालों के लिए जानना ज़रूरी है।

---

## ➡️ Next Topic
**048. OpenAI Batch API** — run huge non-urgent jobs asynchronously at about half price.
