---

# 023. Context Window — What it Means
# हिंदी में: Context Window — इसका मतलब क्या है

---

## 🔵 Simple Definition (English)
The context window is the maximum number of tokens an LLM can "see" in one request. It covers the system prompt, chat history, retrieved documents, your question, AND the answer the model writes. If the total goes over the limit, the API returns an error or older text must be dropped.

## 🔵 सरल परिभाषा (Hindi)
Context window वो maximum tokens की limit है जो LLM एक request में "देख" सकता है। इसमें system prompt, chat history, retrieved documents, user का question और model का जवाब (output) सब शामिल होते हैं। Limit पार होने पर API error देती है या पुराना text हटाना पड़ता है।

---

## 🔴 Problem it Solves
Transformers compare every token with every other token, so memory and compute grow fast with length. A hard limit keeps latency and GPU memory under control. Developers must understand the limit, because "the model forgot my earlier message" or "400 context_length_exceeded" are the most common production bugs in chat and RAG apps.

## 🔴 यह क्यों बना? (Hindi)
Transformer हर token को बाकी सभी tokens से compare करता है, इसलिए length बढ़ने पर memory और compute तेज़ी से बढ़ते हैं। Hard limit से latency और GPU memory control में रहती है। Developer को limit समझनी ज़रूरी है, क्योंकि "model पुराना message भूल गया" या "400 context_length_exceeded" chat और RAG apps के सबसे common bugs हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect everything: system + history + retrieved chunks + user question
Step 2 → Count tokens of the whole input (input_tokens)
Step 3 → Reserve room for the answer (max_tokens / max_completion_tokens)
Step 4 → Check: input_tokens + reserved_output <= context_window
Step 5 → If it does not fit: trim history, summarise, or retrieve fewer chunks
Step 6 → Send request; model reads all tokens with attention
Step 7 → Generated tokens are appended to the window as it writes
Step 8 → You pay for input tokens + output tokens
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → सब कुछ जमा करो: system + history + retrieved chunks + user question
Step 2 → पूरे input के tokens count करो (input_tokens)
Step 3 → जवाब के लिए जगह reserve करो (max_tokens)
Step 4 → Check: input_tokens + reserved_output <= context_window
Step 5 → Fit न हो तो: history trim करो, summarise करो, कम chunks लाओ
Step 6 → Request भेजो; model सभी tokens पर attention लगाता है
Step 7 → Generate हुए tokens भी window में जुड़ते जाते हैं
Step 8 → Input + output tokens दोनों का पैसा लगता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer asks, "What is the HS code for a lithium power bank?" The prompt holds a 300-token system prompt, 5 retrieved tariff chunks of 600 tokens each (3,000), and 4 earlier chat turns (800). Total is about 4,100 tokens, which fits easily in a 128K window. But if someone pastes a full 200-page tariff schedule (about 150K tokens), the request fails. The fix is RAG: retrieve only the top chunks instead of stuffing the whole book.

**Zomato AI**: A food assistant keeps the full chat history. After 60 turns the window fills up. Good design keeps the last 6 turns verbatim and a short summary of the older ones.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer पूछता है, "Power bank का HS code क्या है?" Prompt में 300 tokens का system prompt, 5 retrieved chunks (हर एक 600 tokens = 3,000) और 4 पिछले turns (800) हैं। कुल लगभग 4,100 tokens, जो 128K window में आराम से fit है। लेकिन कोई पूरा 200-page tariff schedule (करीब 150K tokens) paste कर दे तो request fail होगी। Fix: RAG, यानी पूरी book की जगह सिर्फ top chunks लाओ।

**Zomato AI**: Food assistant पूरी chat history रखता है। 60 turns के बाद window भर जाती है। अच्छा design: आख़िरी 6 turns जस के तस और पुराने turns की छोटी summary।

---

## 💻 Code Example — Basic
```python
# Pure Python demo: a rough token budget check (no API key needed)
from typing import Dict, List  # type hints for clarity

# Rough rule: 1 token is about 4 characters of English text
def rough_tokens(text: str) -> int:
    # Divide characters by 4 and keep at least 1 token
    return max(1, len(text) // 4)

# Context window sizes (check provider docs; these change over time)
WINDOWS: Dict[str, int] = {"small-model": 8_000, "gpt-4o-class": 128_000}

def fits(messages: List[Dict[str, str]], window: int, reserve_output: int = 1_000) -> bool:
    # Sum the rough tokens of every message
    used = sum(rough_tokens(m["content"]) + 4 for m in messages)  # +4 per-message overhead
    # Input plus reserved output must stay under the window
    return used + reserve_output <= window

# Build a tiny conversation
msgs = [
    {"role": "system", "content": "You are a tariff assistant."},   # system prompt
    {"role": "user", "content": "HS code for a power bank?"},      # user question
]
print("fits in 8K:", fits(msgs, WINDOWS["small-model"]))           # expected True

# Simulate a huge pasted document
msgs.append({"role": "user", "content": "x" * 200_000})            # about 50,000 tokens
print("fits in 8K:", fits(msgs, WINDOWS["small-model"]))           # expected False
print("fits in 128K:", fits(msgs, WINDOWS["gpt-4o-class"]))        # expected True
```

## 💻 Code Example — Advanced
```python
# Production: trim chat history to fit a token budget (sync + async)
import asyncio                                   # for the async demo
import logging                                   # for warnings
from typing import Dict, List                    # type hints

import tiktoken                                  # pip install tiktoken

logger = logging.getLogger(__name__)             # module logger
Message = Dict[str, str]                         # alias for a chat message


class ContextManager:
    """Keeps a conversation inside a token budget."""

    def __init__(self, window: int = 128_000, reserve_output: int = 1_000) -> None:
        self.window = window                     # model context window
        self.reserve_output = reserve_output     # tokens kept free for the answer
        try:
            self.enc = tiktoken.encoding_for_model("gpt-4o")   # exact tokenizer
        except Exception:                        # offline or unknown model
            logger.warning("tiktoken unavailable, using rough estimate")
            self.enc = None                      # fall back later

    def count(self, text: str) -> int:
        if self.enc is None:                     # fallback path
            return max(1, len(text) // 4)        # rough estimate
        return len(self.enc.encode(text))        # exact count

    def total(self, messages: List[Message]) -> int:
        # 4 tokens overhead per message, 2 to prime the reply
        return sum(self.count(m["content"]) + 4 for m in messages) + 2

    def trim(self, messages: List[Message]) -> List[Message]:
        budget = self.window - self.reserve_output       # max input tokens
        system = [m for m in messages if m["role"] == "system"]   # always keep system
        rest = [m for m in messages if m["role"] != "system"]     # trimmable turns
        while rest and self.total(system + rest) > budget:        # too big?
            dropped = rest.pop(0)                                 # drop oldest turn
            logger.info("dropped old %s message", dropped["role"])
        if self.total(system + rest) > budget:                    # still too big
            raise ValueError("System prompt plus latest turn exceed window")
        return system + rest                                      # trimmed list

    async def atrim(self, messages: List[Message]) -> List[Message]:
        # CPU-bound work: run in a thread so the event loop stays free
        return await asyncio.to_thread(self.trim, messages)


if __name__ == "__main__":
    cm = ContextManager(window=60, reserve_output=10)   # tiny window to see trimming
    history = [{"role": "system", "content": "Tariff bot."}] + [
        {"role": "user", "content": f"Question number {i} about HS codes"} for i in range(10)
    ]
    kept = asyncio.run(cm.atrim(history))               # async trim
    print(f"kept {len(kept)} of {len(history)} messages")
```

---

## 🟠 FastAPI Integration
Check the window at the API edge so users get a clean 413 error instead of a failed LLM call (which still costs time).

```python
from fastapi import FastAPI, HTTPException      # web framework + error type
from pydantic import BaseModel, Field           # request validation (pydantic v2)
from openai import AsyncOpenAI                  # async OpenAI client

app = FastAPI()                                 # create app
client = AsyncOpenAI()                          # reads OPENAI_API_KEY from env
MAX_INPUT_TOKENS = 100_000                      # our own safe limit


class AskRequest(BaseModel):
    question: str = Field(min_length=1)         # user question
    context: str = ""                           # retrieved text


@app.post("/ask")
async def ask(req: AskRequest) -> dict:
    est = (len(req.question) + len(req.context)) // 4           # rough token estimate
    if est > MAX_INPUT_TOKENS:                                  # too large
        raise HTTPException(status_code=413, detail=f"~{est} tokens exceeds limit")
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",                                    # cheap, 128K window
        messages=[
            {"role": "system", "content": "Answer from the context only."},
            {"role": "user", "content": f"Context:\n{req.context}\n\nQ: {req.question}"},
        ],
        max_tokens=300,                                         # reserve output room
    )
    return {
        "answer": resp.choices[0].message.content,
        "prompt_tokens": resp.usage.prompt_tokens,              # real input usage
        "completion_tokens": resp.usage.completion_tokens,      # real output usage
    }
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `trim_messages` in `langchain_core.messages` to keep a history inside a token budget. In LangGraph, call it inside a node before the LLM node.

```python
from langchain_core.messages import (   # message classes and trimmer
    AIMessage, HumanMessage, SystemMessage, trim_messages,
)
from langchain_openai import ChatOpenAI  # LangChain wrapper for OpenAI

llm = ChatOpenAI(model="gpt-4o-mini")    # model used for counting and calling

trimmer = trim_messages(
    max_tokens=1000,          # budget for the history
    strategy="last",          # keep the most recent messages
    token_counter=llm,        # use the model to count tokens
    include_system=True,      # never drop the system message
    start_on="human",         # history must start with a human turn
)

history = [
    SystemMessage("You are a tariff assistant."),
    HumanMessage("Old question"), AIMessage("Old answer"),
    HumanMessage("HS code for a power bank?"),
]
chain = trimmer | llm                    # LCEL: trim first, then call the model
# result = chain.invoke(history)         # needs OPENAI_API_KEY
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting that output tokens also use the window
✅ Correct: Reserve room for the answer.

```python
# Wrong — input uses the full window, no room for output
used = 128_000
# Right — keep a reserve for the answer
used_ok = 128_000 - 4_000
```

❌ Mistake 2: Sending the whole chat history forever
✅ Correct: Trim or summarise old turns.

```python
# Wrong — history grows without limit, cost and errors grow too
history.append(new_message)
# Right — trim before every call
history = cm.trim(history)
```

❌ Mistake 3: Assuming a bigger window means better answers
✅ Correct: Long contexts cost more and models can miss details in the middle ("lost in the middle"). Retrieve only what is needed.

---

## 🧠 Tricky Interview Question

**Q**: "Your chatbot has a 128K window, but after a long chat it ignores a rule placed in the middle of the prompt, and the bill doubled. Why, and how do you fix it?"

**Answer**: Every turn re-sends the whole history, so cost grows with each turn (total cost across a chat grows roughly with the square of the number of turns). Also, models attend best to the beginning and end of the prompt, and details in the middle can be missed. Fix: put critical rules in the system prompt (start) and repeat key constraints near the end, trim or summarise history, use RAG for documents, and use prompt caching for the static prefix.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is a context window?
A1: The maximum number of tokens (input plus output) the model can handle in one request.

Q2: [Easy] What happens if you exceed it?
A2: The API returns an error such as `context_length_exceeded` (HTTP 400), or the app must truncate. Some frameworks silently cut text, which causes wrong answers.

Q3: [Medium] Does the output count toward the window?
A3: Yes. Input and output share the window. Some models also have a separate, smaller max output limit, so check both numbers.

Q4: [Medium] How do you handle long chat histories?
A4: Sliding window (keep last N turns), summarise older turns, store facts in a database, or use retrieval. Always keep the system prompt.

Q5: [Hard] Why not always use the largest window instead of RAG?
A5: Cost (you pay per input token every call), latency (long prompts are slower), and quality (lost in the middle). RAG sends only relevant chunks, so it is cheaper, faster, and usually more accurate. Large windows are good for tasks that really need the whole document, such as one-off contract review.

---

## 🔷 When to Use + When Not to Use
✅ Use large context when:
- You need to reason over a whole document at once
- Quick prototypes where RAG is not built yet
- Cached static prefixes make repeated cost low

❌ Avoid stuffing context when:
- Only a few facts are needed (use RAG)
- High-volume traffic where cost matters
- Latency-sensitive endpoints

---

## 📊 Visual Diagram
```
|<------------------- Context Window (e.g. 128K) ------------------->|
+--------+-----------+------------------+-----------+---------------+
| system |  history  | retrieved chunks | question  |  ANSWER room  |
|  300   |    800    |      3,000       |    50     |   max_tokens  |
+--------+-----------+------------------+-----------+---------------+
 \_____________ input_tokens ___________/             \_ output _/

Rule: input_tokens + max_tokens  <=  window
```

---

## 💰 Cost Impact
- You pay for every input token on every call, so a long history is paid again each turn.
- Example: 4,100 input tokens per call at an illustrative $0.15 per 1M = about $0.0006 per call; at 100K calls per day that is about $60 per day. Cutting input to 1,500 tokens saves roughly 60 percent.
- Optimise: trim history, retrieve fewer and better chunks, summarise, use prompt caching for static prefixes, and use a cheaper model for simple turns. Prices change, so confirm on the provider pricing page.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context window | Max tokens per request | एक request में max tokens |
| Input tokens | Tokens you send | जो tokens आप भेजते हैं |
| Output tokens | Tokens the model writes | Model जो tokens लिखता है |
| Truncation | Cutting text to fit | Text काटना |
| Sliding window | Keep only the latest turns | सिर्फ़ ताज़ा turns रखना |
| Lost in the middle | Details in the middle get missed | बीच की जानकारी छूट जाना |

---

## ⚡ 3-Line Summary
English: The context window is the total token limit for input plus output in one request. Count tokens, reserve room for the answer, and trim or retrieve instead of stuffing everything. Bigger windows cost more and do not guarantee better answers.
Hindi: Context window एक request में input + output tokens की कुल limit है। Tokens count करो, जवाब के लिए जगह रखो, और सब कुछ ठूसने की जगह trim या retrieve करो। बड़ी window महंगी है और बेहतर जवाब की गारंटी नहीं।

---

## ➡️ Next Topic
**024. Temperature + Top-p + Top-k** — the knobs that control how random or focused the model's output is.
