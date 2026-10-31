---

# 374. Sliding Window Memory
# हिंदी में: Sliding Window Memory

---

## 🔵 Simple Definition (English)
Sliding window memory keeps only the **last N messages (or last N tokens)** of a conversation and drops everything older. As new messages arrive, the window slides forward. It is the simplest way to keep prompt size bounded.

## 🔵 सरल परिभाषा (Hindi)
Sliding window memory बातचीत के सिर्फ **आखिरी N messages (या आखिरी N tokens)** रखती है और उससे पुराना सब हटा देती है। नए messages आने पर window आगे खिसकती है। Prompt का आकार सीमित रखने का यह सबसे सरल तरीका है।

---

## 🔴 Problem it Solves
Sending the full chat history on every turn makes cost grow with each message, slows responses, and eventually overflows the context window. A fixed-size window gives predictable cost and latency with no extra LLM calls.

## 🔴 यह क्यों बना? (Hindi)
हर turn पर पूरी chat history भेजने से हर message के साथ cost बढ़ती है, response धीमा होता है और अंत में context window भर जाती है। निश्चित आकार की window अनुमानित cost और latency देती है, बिना किसी अतिरिक्त LLM call के।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Store every message in the full history (database), if you need it
Step 2 → Choose the window: last K messages OR last T tokens
Step 3 → On each request, take the newest messages that fit the window
Step 4 → Always keep the system prompt outside the window (never dropped)
Step 5 → Do not start the window mid-pair (start on a user message)
Step 6 → Send system prompt + windowed messages to the LLM
Step 7 → Append the reply; the window slides on the next turn
Step 8 → Old content is forgotten (or handled by summary memory)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → ज़रूरत हो तो हर message पूरी history (database) में रखो
Step 2 → Window चुनो: आखिरी K messages या आखिरी T tokens
Step 3 → हर request पर सबसे नए messages लो जो window में समाएँ
Step 4 → System prompt हमेशा window के बाहर रखो (कभी न हटे)
Step 5 → Window को जोड़े के बीच से शुरू मत करो (user message से शुरू करो)
Step 6 → System prompt + windowed messages LLM को भेजो
Step 7 → Reply जोड़ो; अगले turn पर window खिसकती है
Step 8 → पुरानी बातें भुला दी जाती हैं (या summary memory सँभालती है)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A chat assistant for importers keeps the last 6 messages. The user asks about headphones, then switches to duty rates. The assistant only needs the recent exchange. But when the user says 20 messages later "use the same origin as before", the window has forgotten the origin. The fix: store `origin` as a structured fact, outside the window.

**Zomato-style**: A food chatbot only needs the last few turns ("make it spicier"), not the whole chat.

## 🟡 Real Example Hindi mein
**Tariff System**: Importers के chat assistant में आखिरी 6 messages रखे जाते हैं। User headphones पूछता है, फिर duty rates पर आ जाता है। Assistant को सिर्फ हाल की बातचीत चाहिए। पर 20 messages बाद user कहे "वही origin इस्तेमाल करो जो पहले था", तो window origin भूल चुकी होती है। उपाय: `origin` को structured fact के रूप में window के बाहर रखो।

**Zomato-style**: Food chatbot को बस आखिरी कुछ turns चाहिए ("थोड़ा तीखा करो"), पूरी chat नहीं।

---

## 💻 Code Example — Basic
```python
# Message-count sliding window (runs offline)
from collections import deque  # deque(maxlen=N) auto-drops the oldest item

Message = dict[str, str]  # {"role": ..., "content": ...}

class SlidingWindowMemory:
    def __init__(self, k: int = 4) -> None:
        self.window: deque[Message] = deque(maxlen=k)  # only last k messages survive

    def add(self, role: str, content: str) -> None:
        self.window.append({"role": role, "content": content})  # oldest drops automatically

    def messages(self, system: str) -> list[Message]:
        return [{"role": "system", "content": system}] + list(self.window)  # system always included

if __name__ == "__main__":
    mem = SlidingWindowMemory(k=4)
    for i in range(1, 7):  # six messages
        mem.add("user" if i % 2 else "assistant", f"message {i}")
    for m in mem.messages("You are a tariff assistant."):
        print(m)  # system + messages 3..6 only
```

## 💻 Code Example — Advanced
```python
# Token-based window: keeps the system prompt, never splits a user/assistant pair, async-safe
import asyncio  # lock for concurrent requests
from dataclasses import dataclass, field  # container

Message = dict[str, str]

def count_tokens(text: str) -> int:
    return max(1, len(text) // 4)  # approximation; use tiktoken for real counts

@dataclass
class TokenWindow:
    max_tokens: int = 1000                                     # window budget (excluding system)
    history: list[Message] = field(default_factory=list)       # full history is kept
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)   # protects concurrent writes

    async def add(self, role: str, content: str) -> None:
        async with self.lock:
            self.history.append({"role": role, "content": content})

    async def window(self) -> list[Message]:
        async with self.lock:
            used, picked = 0, []
            for msg in reversed(self.history):                 # newest first
                cost = count_tokens(msg["content"]) + 4        # +4 per-message overhead
                if used + cost > self.max_tokens:
                    break
                picked.append(msg); used += cost
            picked.reverse()
            while picked and picked[0]["role"] != "user":      # window must start on a user turn
                picked.pop(0)
            return picked

async def main() -> None:
    w = TokenWindow(max_tokens=60)
    for i in range(10):
        await w.add("user" if i % 2 == 0 else "assistant", "x" * 80)
    win = await w.window()
    print(len(w.history), "stored ->", len(win), "sent")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Keep full history in a store keyed by `session_id`, and apply the window only when building the LLM prompt.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # models
from openai import AsyncOpenAI  # async client

app = FastAPI()
client = AsyncOpenAI()  # reads OPENAI_API_KEY
SESSIONS: dict[str, TokenWindow] = {}  # use Redis/Postgres in production

class ChatIn(BaseModel):
    session_id: str   # conversation id
    message: str      # user text

@app.post("/chat")
async def chat(body: ChatIn) -> dict:
    mem = SESSIONS.setdefault(body.session_id, TokenWindow(max_tokens=1500))
    await mem.add("user", body.message)
    msgs = [{"role": "system", "content": "You are a tariff assistant."}] + await mem.window()
    try:
        resp = await client.chat.completions.create(model="gpt-4o-mini", messages=msgs, max_tokens=300)
    except Exception as exc:
        raise HTTPException(502, str(exc))
    answer = resp.choices[0].message.content or ""
    await mem.add("assistant", answer)
    return {"answer": answer, "prompt_tokens": resp.usage.prompt_tokens}  # shows the window works
```

---

## 🔗 LangChain / LangGraph Connection
Modern LangChain uses `trim_messages` as the sliding window. (Older `ConversationBufferWindowMemory` is deprecated.)

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, trim_messages  # real utilities

trimmer = trim_messages(
    max_tokens=4,            # with token_counter=len this means "last 4 messages"
    strategy="last",         # keep the newest
    token_counter=len,       # count each message as 1
    include_system=True,     # keep the system message
    start_on="human",        # window begins on a human turn
)

msgs = [SystemMessage("You are a tariff bot.")] + [
    HumanMessage("q1"), AIMessage("a1"), HumanMessage("q2"), AIMessage("a2"), HumanMessage("q3"),
]
print(trimmer.invoke(msgs))  # system + last messages that fit

# In a LangGraph node: pass trimmer.invoke(state["messages"]) to the LLM,
# while the state still stores the full message list.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Cutting history in the middle of a user/assistant pair or dropping the system prompt
✅ Correct: keep the system prompt separate and start on a user turn.

```python
# Wrong
messages = history[-5:]
# Right
messages = [system] + trimmed_to_start_on_user(history[-5:])
```

❌ Mistake 2: Relying on the window for important facts
✅ Correct: store key facts in structured memory.

```python
# Wrong: origin mentioned 30 messages ago is gone
# Right
facts = {"origin": "VN", "importer": "ABC"}   # always included in the prompt
```

---

## 🧠 Tricky Interview Question
**Q**: "A user says 'what did I ask first?' and the bot answers wrongly. Is the model bad?"

**Answer**: No, the window dropped the first message, so the model never saw it. Sliding windows trade recall for cost. If such questions matter, add summary memory, store the whole history externally with retrieval, or keep pinned facts. Also tell the user (or design the UX) so the limits are understood.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is sliding window memory?
A1: Keeping only the latest N messages or tokens in the prompt and discarding older ones.

Q2: [Easy] Main benefit?
A2: Bounded and predictable cost and latency, and no overflow of the context window.

Q3: [Medium] Message-count window vs token window?
A3: Message count is simple but message sizes vary. A token window guarantees a size bound.

Q4: [Medium] What should never be inside the sliding part?
A4: System prompt, critical constraints and key facts; keep them pinned outside the window.

Q5: [Hard] How would you combine sliding window with other memories?
A5: Pinned system prompt + structured facts + rolling summary of dropped turns + the last K raw messages, optionally with vector retrieval of older relevant turns.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chat where recent context matters most
- Simple, cheap, predictable memory is enough

❌ Avoid when:
- Users refer to early conversation
- Long tasks with decisions that must be remembered (use summary or external memory)

---

## 📊 Visual Diagram
```
 History:  m1 m2 m3 m4 m5 m6 m7 m8
                         [ window k=4 ]
                         m5 m6 m7 m8   -> sent to LLM
 Next turn adds m9:
                            m6 m7 m8 m9   (m5 forgotten)

 Prompt = [system prompt] + [pinned facts] + [window]
```

---

## 💰 Cost Impact
- Without a window, turn n sends about n x 150 tokens; at 40 turns that is 6,000 tokens per call.
- With k=6, it stays near 900 tokens per call: about 85 percent cheaper at turn 40.
- No extra LLM calls are needed. Optimise: token window instead of count, cap `max_tokens` on replies, pin short facts, keep stable system prompt for prompt caching.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Window | Recent messages kept | रखे गए हाल के messages |
| Truncation | Dropping old content | पुराना हिस्सा हटाना |
| Pinned fact | Always-included fact | हमेशा शामिल रहने वाला fact |
| Context window | Model's max input size | Model की अधिकतम input सीमा |
| trim_messages | LangChain trimming helper | LangChain का trimming helper |

---

## ⚡ 3-Line Summary
English: Sliding window memory keeps only the latest messages or tokens, giving bounded cost with no extra calls. It forgets older details, so pin important facts outside it. Use token-based windows and start on a user turn.
Hindi: Sliding window memory सिर्फ नवीनतम messages या tokens रखती है, जिससे बिना अतिरिक्त calls के cost सीमित रहती है। यह पुरानी बातें भूल जाती है, इसलिए ज़रूरी facts बाहर pin करो। Token-आधारित window इस्तेमाल करो और user turn से शुरू करो।

---

## ➡️ Next Topic
**375. Summary Memory** — compressing the dropped messages instead of forgetting them.
