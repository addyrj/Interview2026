---

# 367. In-Context Memory
# हिंदी में: In-Context Memory (Prompt के अंदर की Memory)

---

## 🔵 Simple Definition (English)
In-context memory means keeping past messages directly inside the prompt (the `messages` list). The model "remembers" only because you resend the history on every call. It is the simplest, fastest memory, but limited by the context window and cost.

## 🔵 सरल परिभाषा (Hindi)
In-context memory मतलब पुराने messages को सीधे prompt (`messages` list) में रखना। Model तभी "याद" रखता है जब आप हर call में history दोबारा भेजें। यह सबसे simple और fast memory है, पर context window और cost से सीमित है।

---

## 🔴 Problem it Solves
- Follow-up questions need earlier turns ("what about its duty?").
- No database needed: zero setup, zero extra latency.
- But: history grows each turn; eventually it exceeds the window or becomes expensive.

## 🔴 यह क्यों बना? (Hindi)
- Follow-up सवालों को पिछले turns चाहिए।
- Database की ज़रूरत नहीं: setup शून्य, extra latency शून्य।
- पर history हर turn बढ़ती है; आखिर में window पार हो जाती है या महँगी हो जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keep a list: [system, user1, assistant1, user2, assistant2, ...]
Step 2 → New user message appended to the list
Step 3 → WHOLE list sent to the LLM
Step 4 → Assistant reply appended to the list
Step 5 → Check token count; if over budget -> trim/summarise (next topics)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → List रखो: [system, user1, assistant1, user2, ...]
Step 2 → नया user message list में जोड़ो
Step 3 → पूरी list LLM को भेजो
Step 4 → Assistant का reply list में जोड़ो
Step 5 → Token count देखो; ज़्यादा हो तो trim/summarise करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: User: "Cotton t-shirt from Bangladesh." Bot: "HS 6109." User: "What is the duty on it?" Because the earlier two messages are in the prompt, "it" resolves to HS 6109 cotton t-shirts. Without them the bot asks "duty on what?".
**Amazon AI (Rufus-style)**: "Show running shoes" then "only under 3000" — works via in-context history.

## 🟡 Real Example Hindi mein
**Tariff System**: User: "Bangladesh से cotton t-shirt।" Bot: "HS 6109।" User: "इस पर duty कितनी?" पिछले दो messages prompt में हैं, इसलिए "इस" = HS 6109। वरना bot पूछेगा "किस पर duty?"।
**Amazon AI**: "running shoes दिखाओ" फिर "सिर्फ 3000 से कम" — in-context history से काम करता है।

---

## 💻 Code Example — Basic
```python
# Pure Python (offline): in-context memory = a growing messages list
messages: list[dict[str, str]] = [                                  # start with the system message
    {"role": "system", "content": "You are a tariff assistant."}    # rules live at index 0
]

def fake_llm(msgs: list[dict[str, str]]) -> str:                    # offline stand-in for the API
    last_user = [m for m in msgs if m["role"] == "user"][-1]        # find latest user message
    seen = len([m for m in msgs if m["role"] == "user"])            # how many user turns exist
    return f"[turn {seen}] saw {len(msgs)} messages; you said: {last_user['content']}"  # echo

def ask(text: str) -> str:                                          # one chat turn
    messages.append({"role": "user", "content": text})              # add user turn
    reply = fake_llm(messages)                                      # send whole history
    messages.append({"role": "assistant", "content": reply})        # remember the reply
    return reply                                                    # return answer

print(ask("Cotton t-shirt from Bangladesh"))                        # turn 1
print(ask("What is the duty on it?"))                               # turn 2 sees turn 1
approx_tokens = sum(len(m["content"]) for m in messages) // 4       # rough token estimate
print("approx tokens in prompt:", approx_tokens)                    # watch it grow
```

## 💻 Code Example — Advanced
```python
# Async in-context memory with a hard token budget and safe trimming
import asyncio                                                       # async runtime
from dataclasses import dataclass, field                             # simple state holder


def approx_tokens(text: str) -> int:                                 # cheap estimator (use tiktoken in prod)
    return max(1, len(text) // 4)                                    # ~4 chars per token


@dataclass
class ContextMemory:                                                 # per-session memory
    system: str                                                      # system prompt (never trimmed)
    max_tokens: int = 1500                                           # budget for history
    turns: list[dict[str, str]] = field(default_factory=list)        # user/assistant messages

    def add(self, role: str, content: str) -> None:                  # append one message
        if role not in {"user", "assistant"}:                        # validate input
            raise ValueError(f"bad role: {role}")                    # fail loudly
        self.turns.append({"role": role, "content": content})        # store it
        self._trim()                                                 # enforce the budget

    def _trim(self) -> None:                                         # drop oldest turns first
        while self.turns and self._size() > self.max_tokens:         # while over budget
            self.turns.pop(0)                                        # remove oldest message
        while self.turns and self.turns[0]["role"] == "assistant":   # never start with assistant
            self.turns.pop(0)                                        # keep a valid conversation

    def _size(self) -> int:                                          # total tokens in history
        return sum(approx_tokens(t["content"]) for t in self.turns)  # sum per message

    def to_messages(self) -> list[dict[str, str]]:                   # final list for the API
        return [{"role": "system", "content": self.system}, *self.turns]  # system + history


async def fake_llm(messages: list[dict[str, str]]) -> str:           # offline async model
    await asyncio.sleep(0)                                           # yield control like real IO
    return f"ok ({len(messages)} msgs)"                              # tiny reply


async def main() -> None:                                            # demo
    mem = ContextMemory(system="Tariff assistant", max_tokens=30)    # tiny budget to see trimming
    for q in ["Cotton t-shirt from Bangladesh please", "Duty on it?", "And in INR?"]:  # 3 turns
        mem.add("user", q)                                           # remember question
        try:                                                         # protect LLM call
            answer = await fake_llm(mem.to_messages())               # call model
        except Exception as exc:                                     # network error etc.
            answer = f"error: {exc}"                                 # degrade gracefully
        mem.add("assistant", answer)                                 # remember answer
        print(len(mem.turns), "turns kept")                          # show trimming effect


if __name__ == "__main__":                                           # entry point
    asyncio.run(main())                                              # run demo
```

---

## 🟠 FastAPI Integration
The client may send the full history (stateless server) or only a `session_id` (server keeps it). The second is safer: clients cannot inject fake "assistant" messages.

```python
# FastAPI: server-side sessions holding ContextMemory (use Redis for multi-worker)
from fastapi import FastAPI, HTTPException        # framework + errors
from pydantic import BaseModel, Field             # validation

app = FastAPI()                                   # app instance
sessions: dict[str, ContextMemory] = {}           # dev only: lost on restart / not shared

class In(BaseModel):                              # request body
    session_id: str                               # which conversation
    message: str = Field(max_length=2000)         # cap input size

@app.post("/chat")                                # route
async def chat(body: In) -> dict[str, object]:    # typed return
    mem = sessions.setdefault(body.session_id, ContextMemory(system="Tariff assistant"))  # get/create
    mem.add("user", body.message)                 # remember question
    try:
        answer = await fake_llm(mem.to_messages())  # call model
    except Exception as exc:                      # upstream failure
        raise HTTPException(502, "LLM failed") from exc
    mem.add("assistant", answer)                  # remember answer
    return {"answer": answer, "history_tokens": mem._size()}  # expose size for monitoring
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `InMemoryChatMessageHistory` + `RunnableWithMessageHistory` is exactly this pattern. LangGraph's `MessagesState` (the `messages` key with `add_messages` reducer) is in-context memory; the checkpointer persists it per `thread_id`.

```python
# LCEL chain with in-context memory per session
from langchain_core.chat_history import InMemoryChatMessageHistory   # history store
from langchain_core.runnables.history import RunnableWithMessageHistory  # wrapper
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # prompt parts
from langchain_openai import ChatOpenAI                              # model

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a tariff assistant."),                       # rules
    MessagesPlaceholder("history"),                                  # history injected here
    ("human", "{input}"),                                            # new question
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini")                     # LCEL pipe
stores: dict[str, InMemoryChatMessageHistory] = {}                   # session_id -> history

def get_history(session_id: str) -> InMemoryChatMessageHistory:     # factory per session
    return stores.setdefault(session_id, InMemoryChatMessageHistory())

with_memory = RunnableWithMessageHistory(
    chain, get_history, input_messages_key="input", history_messages_key="history")
# with_memory.invoke({"input": "Duty on it?"}, config={"configurable": {"session_id": "s1"}})
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Unlimited history
✅ Correct: enforce a token budget.

```python
# Wrong
messages.append(new)            # grows forever -> context_length_exceeded
# Right
mem.add("user", text)           # trims oldest turns automatically
```

❌ Mistake 2: Trimming the system prompt or leaving an orphan assistant message
✅ Correct: keep the system prompt outside the trimmed list and start history with a user turn.

```python
# Wrong: messages = messages[-5:]    # may drop the system prompt!
# Right: [system] + turns[-5:]
```

---

## 🧠 Tricky Interview Question
**Q**: "A chat works for 20 turns, then answers get worse but no error occurs. Why?"

**Answer**: History grew near the limit and either the provider/your trimmer dropped early turns (including key facts like the product), or the "lost in the middle" effect made the model ignore mid-prompt info. Fix: pin important facts in a separate "facts" block, summarise old turns, and monitor prompt tokens per call.

---

## ⚫ Interview Questions + Answers

Q1: What is in-context memory?
A1: Past messages kept inside the prompt and resent on every call.

Q2: Why does it get expensive?
A2: Input tokens are billed on every call, so cost grows roughly quadratically over a long chat (turn n resends n-1 turns).

Q3: What happens when history exceeds the context window?
A3: The API returns a context-length error (OpenAI) or you must trim. Never rely on silent truncation.

Q4: Should the client send history or the server store it?
A4: Server-side by `session_id` is safer and lets you apply trimming, auth and auditing centrally.

Q5: How would you keep key facts while dropping old turns?
A5: Split memory: a pinned facts block (extracted, always included) + a sliding window of recent turns + optional running summary. Facts are updated by a cheap extraction step.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Short chats (under ~10-20 turns)
- Prototypes, simple bots
- Follow-up question resolution

❌ Avoid when:
- Cross-session memory is needed
- Very long agent runs / huge tool outputs
- Cost-sensitive high volume without trimming

---

## 📊 Visual Diagram
```
Turn 1: [S][U1]                    -> LLM -> A1
Turn 2: [S][U1][A1][U2]            -> LLM -> A2
Turn 3: [S][U1][A1][U2][A2][U3]    -> LLM -> A3
         ^ resent every time: cost grows each turn
```

---

## 💰 Cost Impact
- If each turn adds 200 tokens, turn 20 sends ~4,000 history tokens. Total input over 20 turns ~ 200 x (1+2+...+20) = 42,000 tokens vs 4,000 if stateless.
- Optimise: cap with a token budget, summarise, put static text first and use prompt caching, set `max_tokens` on outputs, and log `usage.prompt_tokens` every call.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Messages list | History sent to the API | API को भेजी जाने वाली history |
| Context window | Max tokens per call | एक call में max tokens |
| Trimming | Dropping old turns | पुराने turns हटाना |
| Session ID | Conversation key | बातचीत की पहचान |
| Prompt tokens | Billed input tokens | Input tokens |

---

## ⚡ 3-Line Summary
English: In-context memory is the history you resend inside the prompt. It is simple and fast but grows cost every turn and is capped by the context window. Always enforce a token budget.
Hindi: In-context memory वह history है जो आप prompt में दोबारा भेजते हैं। Simple और fast है, पर हर turn cost बढ़ाती है और context window से सीमित है। हमेशा token budget लगाओ।

---

## ➡️ Next Topic
**368. External Memory** — storing memory outside the prompt (Redis, Postgres, vector DB) so it survives restarts and sessions.
