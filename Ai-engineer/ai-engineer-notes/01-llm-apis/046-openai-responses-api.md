---

# 046. OpenAI Responses API (new)
# हिंदी में: OpenAI Responses API (नया)

---

## 🔵 Simple Definition (English)
The Responses API (`client.responses.create`) is OpenAI's newer, unified API for text generation. It takes an `input` (string or list of items), optional `instructions`, built-in tools (web search, file search) and your own function tools, and returns a response with `output_text`. It can also keep conversation state on the server with `previous_response_id`.

## 🔵 सरल परिभाषा (Hindi)
Responses API (`client.responses.create`) OpenAI का नया unified API है। इसमें `input` (string या list), optional `instructions`, built-in tools (web search, file search) और आपके अपने function tools दिए जा सकते हैं, और जवाब में `output_text` मिलता है। `previous_response_id` से conversation state server पर रखा जा सकता है।

---

## 🔴 Problem it Solves
- Chat Completions needs you to resend the whole history every turn and manage tool loops yourself.
- The Assistants API (threads, runs, polling) was heavy and is being replaced.
- Agent features (web search, file search, reasoning items) were spread across different APIs.
- One simpler, agent-friendly interface was needed.

## 🔴 यह क्यों बना? (Hindi)
- Chat Completions में हर turn पर पूरी history दोबारा भेजनी पड़ती है और tool loop खुद संभालना पड़ता है।
- Assistants API (threads, runs, polling) भारी था और उसे replace किया जा रहा है।
- Agent features (web search, file search, reasoning items) अलग-अलग APIs में बिखरे थे।
- एक आसान, agent-friendly interface चाहिए था।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create client: OpenAI() (reads OPENAI_API_KEY)
Step 2 → Call client.responses.create(model=..., input=..., instructions=...)
Step 3 → Optionally pass tools=[...] (function tools or built-in tools)
Step 4 → API returns a Response with output items (messages, tool calls, reasoning)
Step 5 → Read response.output_text for the final text
Step 6 → If a function call item appears: run your function, send back function_call_output
Step 7 → For follow-ups pass previous_response_id=response.id (server keeps history)
Step 8 → Read response.usage for input/output tokens
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Client बनाओ: OpenAI() (OPENAI_API_KEY पढ़ता है)
Step 2 → client.responses.create(model=..., input=..., instructions=...) call करो
Step 3 → ज़रूरत हो तो tools=[...] दो (function tools या built-in tools)
Step 4 → API Response देता है जिसमें output items होते हैं (messages, tool calls, reasoning)
Step 5 → अंतिम text के लिए response.output_text पढ़ो
Step 6 → Function call item आए तो अपना function चलाओ और function_call_output भेजो
Step 7 → Follow-up के लिए previous_response_id=response.id दो (server history रखता है)
Step 8 → Tokens के लिए response.usage पढ़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The assistant gets "classify: wireless earbuds". With the Responses API we send `instructions="You are a customs classification expert"` and `input` as the product text, plus a function tool `lookup_hs_code`. The model calls the tool, we return the result, and the model writes the final answer. A follow-up "what about the charging case?" uses `previous_response_id`, so we do not resend the earlier text ourselves.

**Amazon-style**: A shopping assistant uses the built-in web search tool for current prices and a function tool for the internal catalogue.

## 🟡 Real Example Hindi mein
**Tariff System**: Assistant को "classify: wireless earbuds" मिलता है। Responses API में हम `instructions="You are a customs classification expert"`, `input` में product text और एक function tool `lookup_hs_code` भेजते हैं। Model tool call करता है, हम result लौटाते हैं और model final जवाब लिखता है। Follow-up "charging case का क्या?" में `previous_response_id` इस्तेमाल होता है, इसलिए पुराना text दोबारा भेजना नहीं पड़ता।

**Amazon-style**: Shopping assistant current prices के लिए built-in web search और internal catalogue के लिए function tool इस्तेमाल करता है।

---

## 💻 Code Example — Basic
```python
# Basic: one Responses API call (needs: pip install openai, OPENAI_API_KEY)
from openai import OpenAI  # sync client from openai>=1

client = OpenAI()  # create client (reads key from environment)

response = client.responses.create(  # call the Responses API
    model="gpt-4o-mini",  # model name
    instructions="You are a customs classification expert. Be brief.",  # system-like rule
    input="Give the HS chapter for wireless earbuds.",  # user input as plain string
    max_output_tokens=100,  # cap output tokens (note: not max_tokens)
)

print(response.output_text)  # convenience property: final text
print(response.id)  # id usable as previous_response_id
print(response.usage.input_tokens, response.usage.output_tokens)  # token usage

# Follow-up turn, server remembers the previous turn:
follow = client.responses.create(  # second call
    model="gpt-4o-mini",  # same model
    previous_response_id=response.id,  # link to earlier response
    input="And for the charging case alone?",  # new user message only
)
print(follow.output_text)  # answer using earlier context
```

## 💻 Code Example — Advanced
```python
# Production-style: async Responses API with a function tool loop, errors and usage tracking
import asyncio  # async runtime
import json  # tool arguments are JSON strings
from typing import Any  # type hints
from openai import AsyncOpenAI, APIError, RateLimitError  # openai>=1

client = AsyncOpenAI()  # shared async client

TOOLS: list[dict[str, Any]] = [  # function tool definition (Responses format is flat)
    {
        "type": "function",
        "name": "lookup_hs_code",
        "description": "Look up HS codes for a product keyword.",
        "parameters": {
            "type": "object",
            "properties": {"keyword": {"type": "string"}},
            "required": ["keyword"],
            "additionalProperties": False,
        },
    }
]

def lookup_hs_code(keyword: str) -> dict[str, str]:
    # Fake database for the demo
    db = {"earbuds": "8518.30", "shirt": "6109.10"}
    return {"keyword": keyword, "hs_code": db.get(keyword.lower(), "unknown")}

async def classify(question: str, max_steps: int = 4) -> tuple[str, int]:
    tokens = 0  # total tokens used
    input_items: list[Any] = [{"role": "user", "content": question}]  # running input
    for _ in range(max_steps):  # bound the tool loop
        try:
            resp = await client.responses.create(
                model="gpt-4o-mini",
                instructions="Use tools when needed. Answer in one sentence.",
                input=input_items,
                tools=TOOLS,
            )
        except RateLimitError:  # wait and retry once
            await asyncio.sleep(2)
            continue
        except APIError as exc:  # other API failure
            raise RuntimeError(f"OpenAI error: {exc}") from exc
        tokens += resp.usage.total_tokens  # add usage
        calls = [item for item in resp.output if item.type == "function_call"]  # tool calls
        if not calls:  # no tool needed: done
            return resp.output_text, tokens
        input_items += resp.output  # keep model's output items in context
        for call in calls:  # run each requested tool
            args = json.loads(call.arguments)  # parse arguments
            result = lookup_hs_code(**args)  # run our function
            input_items.append({  # send tool result back
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),
            })
    raise RuntimeError("Tool loop did not finish")  # safety stop

# print(asyncio.run(classify("What is the HS code for earbuds?")))
```

---

## 🟠 FastAPI Integration
Each chat session stores the last `response.id`. The client sends only the new message; the server passes `previous_response_id`. (If you set `store=False`, state is not kept, so you must send history yourself.)

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # validation
from openai import AsyncOpenAI, APIError  # async client

app = FastAPI()  # app
client = AsyncOpenAI()  # shared client
LAST_ID: dict[str, str] = {}  # session_id -> last response id (use Redis in production)

class Msg(BaseModel):
    session_id: str  # chat session
    text: str  # new user text

@app.post("/chat")
async def chat(m: Msg) -> dict:
    try:
        resp = await client.responses.create(
            model="gpt-4o-mini",
            instructions="You are a tariff assistant.",
            input=m.text,  # only the new message
            previous_response_id=LAST_ID.get(m.session_id),  # None on first turn
        )
    except APIError as exc:  # map to 502
        raise HTTPException(status_code=502, detail=str(exc))
    LAST_ID[m.session_id] = resp.id  # remember for next turn
    return {"answer": resp.output_text, "tokens": resp.usage.total_tokens}
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-openai` can use the Responses API with `ChatOpenAI(model=..., use_responses_api=True)`. Built-in tools like web search can then be passed as tool dicts. LangGraph keeps its own state (checkpointer) so you normally manage history in LangGraph rather than on OpenAI's server.

```python
from langchain_openai import ChatOpenAI  # LangChain OpenAI wrapper

llm = ChatOpenAI(model="gpt-4o-mini", use_responses_api=True)  # route via Responses API
msg = llm.invoke("HS chapter for wireless earbuds?")  # normal LangChain call
print(msg.content)  # answer text or content blocks
print(msg.usage_metadata)  # token usage metadata
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using Chat Completions parameter names
✅ Correct: Use Responses names (`input`, `instructions`, `max_output_tokens`).

```python
# Wrong:
# client.responses.create(model="gpt-4o-mini", messages=[...], max_tokens=100)
# Right:
# client.responses.create(model="gpt-4o-mini", input=[...], max_output_tokens=100)
```

❌ Mistake 2: Reading `response.choices[0].message.content`
✅ Correct: Use `response.output_text` (or iterate `response.output`).

```python
# Wrong: text = response.choices[0].message.content   # AttributeError
# Right: text = response.output_text
```

---

## 🧠 Tricky Interview Question
**Q**: "You use `previous_response_id` for chat memory. Compliance says no user data may be stored by a third party. What now?"

**Answer**: Server-side state means OpenAI stores the response (the `store` parameter defaults to true). For strict privacy, set `store=False` and manage conversation history yourself (your DB or LangGraph checkpointer), sending the needed items in `input` each turn. Check data-retention and zero-data-retention options in your agreement. The trade-off: you pay for resending tokens and you must handle truncation.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which method calls the Responses API?
A1: `client.responses.create(...)`, and `response.output_text` gives the final text.

Q2: [Easy] What replaces `messages` and the system role?
A2: `input` (string or list of items) and `instructions` for high-level rules.

Q3: [Medium] How does the Responses API handle conversation state?
A3: Pass `previous_response_id` and OpenAI uses the stored earlier context, so you send only new input. You can also manage state manually by sending the full item list.

Q4: [Medium] Difference from Chat Completions?
A4: Responses returns typed output items (messages, function calls, reasoning), has built-in tools (web search, file search), simpler agent loops and server state. Chat Completions stays supported and is still widely used.

Q5: [Hard] How would you migrate a Chat Completions app with tools to Responses?
A5: Map `messages` to `input`/`instructions`; change tool schema to the flat function format; replace parsing of `choices[0]` with iterating `output` items; handle `function_call_output` items with `call_id`; rename `max_tokens` to `max_output_tokens`; decide on `store` and state strategy; run your golden set to compare quality, and roll out behind a feature flag.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building new agentic apps with tools
- You want built-in web or file search
- You want server-side conversation state

❌ Avoid when:
- You need provider-agnostic code (use LangChain or Chat Completions-compatible endpoints)
- Strict data-storage rules and you cannot manage `store` correctly

---

## 📊 Visual Diagram
```
 client.responses.create(input, instructions, tools, previous_response_id)
                    |
                    v
               +----------+
               |  OpenAI  |  (stores state if store=True)
               +----------+
                    |
                    v
   Response.output = [ reasoning?, function_call?, message ]
                    |
      function_call? --yes--> run tool -> function_call_output -> create() again
                    |
                    no
                    v
             response.output_text
```

---

## 💰 Cost Impact
- Token usage is read from `response.usage` (`input_tokens`, `output_tokens`, `total_tokens`).
- With `previous_response_id`, earlier turns are still processed as input tokens and billed, even though you do not resend them. History grows, so trim or summarise long chats.
- Built-in tools (web search, file search) have their own per-call fees; check the current pricing page.
- Optimise: set `max_output_tokens`, use small models, keep `instructions` short, rely on automatic prompt caching for repeated prefixes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Responses API | OpenAI's unified generation API | OpenAI का नया unified API |
| input | User content or items | User का input |
| instructions | High-level system rules | Model के लिए मुख्य निर्देश |
| output_text | Final text helper | अंतिम text |
| previous_response_id | Link to earlier turn | पिछले turn से जोड़ना |
| function_call_output | Tool result item | Tool का result |

---

## ⚡ 3-Line Summary
English: The Responses API is OpenAI's newer unified interface with `input`, `instructions`, tools and optional server-side state. Read answers from `output_text` and handle tool calls via output items. Decide on `store` for privacy.
Hindi: Responses API OpenAI का नया unified interface है जिसमें `input`, `instructions`, tools और optional server state है। जवाब `output_text` से पढ़ो और tool calls output items से संभालो। Privacy के लिए `store` तय करो।

---

## ➡️ Next Topic
**047. OpenAI Assistants API** — the older thread/run based API, and why it is being replaced.
