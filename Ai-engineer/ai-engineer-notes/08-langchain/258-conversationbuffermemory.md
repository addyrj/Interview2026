---

# 258. ConversationBufferMemory
# हिंदी में: ConversationBufferMemory (पूरी बातचीत का Buffer)

---

## 🔵 Simple Definition (English)
`ConversationBufferMemory` is the simplest LangChain memory class (now **legacy**). It stores **every** message of the conversation, unchanged, and pastes all of it into the prompt on each turn. Simple and accurate, but the prompt grows without limit.

## 🔵 सरल परिभाषा (Hindi)
`ConversationBufferMemory` LangChain की सबसे सरल memory class है (अब **legacy**)। ये बातचीत का **हर** message बिना बदले store करती है और हर turn में सब कुछ prompt में चिपकाती है। सरल और सटीक, पर prompt बिना सीमा बढ़ता है।

---

## 🔴 Problem it Solves
- Manually keeping a `history` string in each call was messy.
- Early chatbots needed an "it just works" way to remember everything.
- Short chats need no summarising or cleverness; the full transcript is best.

## 🔴 यह क्यों बना? (Hindi)
- हर call में हाथ से `history` string रखना गड़बड़ था।
- शुरुआती chatbots को "बस चल जाए" वाला तरीका चाहिए था जो सब याद रखे।
- छोटी chats में summary की ज़रूरत नहीं; पूरा transcript सबसे अच्छा है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → memory = ConversationBufferMemory(memory_key="history")
Step 2 → Chain asks memory: load_memory_variables({}) -> {"history": "Human: ... AI: ..."}
Step 3 → Prompt gets the whole transcript in {history}
Step 4 → LLM answers
Step 5 → memory.save_context({"input": q}, {"output": a}) appends the pair
Step 6 → Next turn repeats with a longer transcript
Step 7 → return_messages=True gives message objects instead of one string (for chat models)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → memory = ConversationBufferMemory(memory_key="history")
Step 2 → Chain memory से माँगती है: load_memory_variables({}) -> {"history": "Human: ... AI: ..."}
Step 3 → Prompt के {history} में पूरा transcript जाता है
Step 4 → LLM जवाब देता है
Step 5 → memory.save_context({"input": q}, {"output": a}) जोड़ी जोड़ता है
Step 6 → अगले turn में transcript और लंबा
Step 7 → return_messages=True से string की जगह message objects मिलते हैं (chat models के लिए)
```

---

## 🟡 Real World Example
**Tariff Classification System**: A 5-turn clarification chat ("Is the speaker battery powered? Does it have Wi-Fi?") before giving an HS code. Short, so the full buffer is fine and gives the model exact wording.
**Zomato AI**: a short support chat of 4-6 messages about a missing item.
For a 60-turn chat, the buffer becomes too expensive.

## 🟡 Real Example Hindi mein
**Tariff System**: HS code देने से पहले 5 turns का सवाल-जवाब ("Speaker battery से चलता है? Wi-Fi है?")। छोटा है, इसलिए पूरा buffer ठीक है और model को सटीक शब्द मिलते हैं।
**Zomato AI**: missing item पर 4-6 messages की छोटी support chat।
60 turns की chat में buffer बहुत महंगा हो जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny re-implementation of ConversationBufferMemory (pure Python, runnable)
from typing import Dict, List

class BufferMemory:
    """Stores every turn; returns them as one transcript string."""

    def __init__(self) -> None:
        self.turns: List[Dict[str, str]] = []            # all turns, never trimmed

    def save_context(self, inputs: Dict[str, str], outputs: Dict[str, str]) -> None:
        # Same method name and shape as LangChain's memory API
        self.turns.append({"human": inputs["input"], "ai": outputs["output"]})

    def load_memory_variables(self, _: Dict[str, str]) -> Dict[str, str]:
        lines: List[str] = []
        for t in self.turns:                              # rebuild the full transcript
            lines.append(f"Human: {t['human']}")
            lines.append(f"AI: {t['ai']}")
        return {"history": "\n".join(lines)}

if __name__ == "__main__":
    mem = BufferMemory()
    mem.save_context({"input": "HS code for speaker?"}, {"output": "8518.22"})
    mem.save_context({"input": "Duty on it?"}, {"output": "20%"})
    print(mem.load_memory_variables({})["history"])
    # Cost view: rough token estimate grows each turn (4 chars ~ 1 token)
    print("approx tokens:", len(mem.load_memory_variables({})["history"]) // 4)
    # Real class:
    #   from langchain.memory import ConversationBufferMemory   (legacy, deprecated)
```

## 💻 Code Example — Advanced
```python
# Legacy ConversationBufferMemory with LLMChain, plus the modern replacement
import asyncio
import warnings

from langchain.chains import LLMChain                       # legacy chain
from langchain.memory import ConversationBufferMemory       # legacy memory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

warnings.filterwarnings("ignore", category=DeprecationWarning)   # silence legacy warnings

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=300)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a tariff classification assistant."),
    MessagesPlaceholder("history"),                         # memory fills this
    ("human", "{input}"),
])

# return_messages=True is required with chat prompts + MessagesPlaceholder
memory = ConversationBufferMemory(memory_key="history", return_messages=True)
chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

async def ask(text: str) -> str:
    try:
        out = await chain.ainvoke({"input": text})          # memory loads and saves automatically
        return str(out["text"])
    except Exception as exc:                                # API/network failure
        return f"Error: {type(exc).__name__}"

def token_estimate() -> int:
    msgs = memory.load_memory_variables({})["history"]      # list of messages
    return sum(len(m.content) for m in msgs) // 4           # rough, chars/4

async def demo() -> None:
    print(await ask("HS code for a Bluetooth speaker?"))
    print(await ask("What duty on it?"))
    print("history tokens ~", token_estimate())

# Modern replacement (no legacy classes): RunnableWithMessageHistory, see topic 257.
if __name__ == "__main__":
    asyncio.run(demo())   # needs OPENAI_API_KEY and langchain<1 installed (legacy imports)
```

---

## 🟠 FastAPI Integration
Memory objects hold state, so create **one per session**, never a global one.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
sessions: dict[str, ConversationBufferMemory] = {}     # use Redis-backed history in production

class In(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(body: In) -> dict[str, str]:
    mem = sessions.setdefault(
        body.session_id, ConversationBufferMemory(memory_key="history", return_messages=True))
    session_chain = LLMChain(llm=llm, prompt=prompt, memory=mem)   # chain bound to this memory
    out = await session_chain.ainvoke({"input": body.message})
    return {"answer": str(out["text"])}
```

---

## 🔗 LangChain / LangGraph Connection
ConversationBufferMemory is legacy (deprecated since LangChain 0.3). The same behavior in modern code is `InMemoryChatMessageHistory` plus `RunnableWithMessageHistory`, or just the `messages` list in LangGraph state with a checkpointer. Interviewers like to ask for this migration.

```python
from langchain_core.chat_history import InMemoryChatMessageHistory

history = InMemoryChatMessageHistory()           # modern equivalent of the buffer
history.add_user_message("HS code for a speaker?")
history.add_ai_message("8518.22")
print(history.messages)                          # list of HumanMessage / AIMessage
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using it for long chats (the prompt grows until it errors).
✅ Correct: Use a window, token trimming, or summary memory.

```python
# Wrong: unbounded
memory = ConversationBufferMemory()
# Right (legacy): bounded to last 5 exchanges
from langchain.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=5)
```

❌ Mistake 2: A shared global memory for all users.
✅ Correct: One memory per session.

❌ Mistake 3: Forgetting `return_messages=True` with a chat prompt (history arrives as one string and `MessagesPlaceholder` fails).
✅ Correct: Set `return_messages=True`.

---

## 🧠 Tricky Interview Question
**Q**: "A chat that worked for 20 turns suddenly returns a context-length error at turn 35, with only short user messages. What happened?"

**Answer**: The buffer sends the full transcript every turn, including long AI replies. Total tokens (history + new input + output) crossed the model's context window. Fixes: window or token-trimmed memory, summary memory, shorter AI replies via `max_tokens`, or retrieval of relevant past turns. Also monitor tokens per turn to alert before hitting the limit.

---

## ⚫ Interview Questions + Answers

Q1: What does ConversationBufferMemory store?
A1: The complete, raw list of human and AI messages of the conversation.

Q2: What does `memory_key` do?
A2: It is the name of the prompt variable the memory fills (default `"history"`). It must match your prompt placeholder.

Q3: Buffer vs BufferWindow vs Summary memory?
A3: Buffer keeps everything. BufferWindow keeps the last k exchanges. Summary keeps an LLM-written summary. Trade-off: fidelity vs token cost.

Q4: Is it safe for production?
A4: Not by itself: it is unbounded, in-process, and deprecated. For production use persistent message history with trimming, or LangGraph persistence.

Q5: Compare cost of buffer memory for a 30-turn conversation with summary memory.
A5: With ~150 tokens per turn, buffer sends about 4,500 tokens on turn 30 and the total over 30 turns is ~70k input tokens (sum of growing history). Summary memory keeps history at maybe 300-500 tokens plus the last turn, so total is a fraction, but it adds a summarising LLM call each turn and loses exact wording. Choose buffer for short, precision-critical chats and summary for long ones.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Short conversations (under ~10 turns)
- You need exact wording of earlier turns
- Prototypes and tutorials

❌ Avoid when:
- Long or open-ended chats
- Multi-user production services
- New projects (it is legacy)

---

## 📊 Visual Diagram
```
 Turn 1: [H1 A1]                         → prompt size: small
 Turn 2: [H1 A1 H2 A2]                   → bigger
 Turn 3: [H1 A1 H2 A2 H3 A3]             → bigger
 ...
 Turn N: [ everything ever said ........ ] → may exceed context window!

 Prompt = system + FULL buffer + new input
```

---

## 💰 Cost Impact
- Input tokens per turn = system + all previous turns + new input. Total cost across a chat grows about quadratically.
- Example: 150 tokens per exchange, 20 exchanges: turn 20 sends ~3000 history tokens; the whole chat uses ~30k input tokens. At gpt-4o-mini rates ($0.15 per 1M input) this is about $0.0045 per chat; at gpt-4o-class prices it is many times more.
- Optimise: window memory, token trimming, summaries, prompt caching of the stable prefix, shorter assistant answers.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Buffer | Keeps all messages | सब messages रखने वाला |
| memory_key | Prompt variable name for history | History का variable नाम |
| return_messages | Return message objects, not a string | String की जगह message objects |
| save_context | Store one input/output pair | एक सवाल-जवाब जोड़ी save करना |
| Legacy | Old, deprecated API | पुराना, deprecated API |

---

## ⚡ 3-Line Summary
English: ConversationBufferMemory stores and replays the whole chat on every turn. It is perfect for short chats but grows without limit and is now legacy. Prefer message-history runnables or LangGraph persistence with trimming.
Hindi: ConversationBufferMemory पूरी chat store करके हर turn में दोहराती है। छोटी chats के लिए सही है पर बिना सीमा बढ़ती है और अब legacy है। Trimming के साथ message-history runnables या LangGraph persistence इस्तेमाल करो।

---

## ➡️ Next Topic
**259. ConversationSummaryMemory**: keep long chats cheap by summarising old turns.
