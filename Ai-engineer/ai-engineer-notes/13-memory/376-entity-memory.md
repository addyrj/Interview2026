---

# 376. Entity Memory
# हिंदी में: Entity Memory (चीज़ों और लोगों की याद)

---

## 🔵 Simple Definition (English)
Entity memory stores facts about specific "entities" (people, products, companies, HS codes) as a key-value store: `entity -> list of facts`. Instead of replaying the whole chat, the app injects only the facts about entities mentioned in the current message.

## 🔵 सरल परिभाषा (Hindi)
Entity memory में specific entities (लोग, products, companies, HS codes) के बारे में facts `entity -> facts की list` के रूप में store होते हैं। पूरी chat दोबारा भेजने की जगह, current message में जो entities आई हैं सिर्फ़ उनके facts prompt में जाते हैं।

---

## 🔴 Problem it Solves
Raw chat history grows without limit and buries important facts ("my product is a lithium battery, made in China") under small talk. Summary memory loses exact details. Entity memory keeps exact facts per entity, small and searchable, so the model stays consistent over a long session.

## 🔴 यह क्यों बना? (Hindi)
Raw history बहुत बड़ी हो जाती है और ज़रूरी facts small talk में दब जाते हैं। Summary में exact details खो जाती हैं। Entity memory हर entity के exact facts छोटे और searchable रूप में रखती है, इसलिए लंबे session में भी model consistent रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User message arrives ("The battery pack is made in Vietnam")
Step 2 → Extract entities from the message (LLM or rules): "battery pack"
Step 3 → Extract new facts about each entity: "origin = Vietnam"
Step 4 → Merge facts into the entity store (dedupe, update conflicts)
Step 5 → On the next turn, find entities in the new message
Step 6 → Inject only those entities' facts into the prompt
Step 7 → LLM answers using exact, compact facts
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User message आता है ("Battery pack Vietnam में बना है")
Step 2 → Message से entities निकालो (LLM या rules): "battery pack"
Step 3 → हर entity के नए facts निकालो: "origin = Vietnam"
Step 4 → Facts को entity store में merge करो (duplicates हटाओ, conflicts update करो)
Step 5 → अगले turn में नए message की entities ढूँढो
Step 6 → सिर्फ़ उन्हीं entities के facts prompt में डालो
Step 7 → LLM compact और exact facts से जवाब देता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs broker says "Item A is a lithium-ion battery pack, 48V" then 20 messages later "what duty applies to Item A?". The entity store holds `Item A: [lithium-ion, 48V, origin Vietnam]`, so the prompt carries 3 facts (about 20 tokens) instead of 20 messages (about 1500 tokens). **Zomato-style**: a food assistant remembers `Priya: vegetarian, allergic to peanuts` and never suggests a peanut dish.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker कहता है "Item A lithium-ion battery pack है, 48V", 20 messages बाद पूछता है "Item A पर duty क्या लगेगी?"। Entity store में `Item A: [lithium-ion, 48V, origin Vietnam]` है, इसलिए prompt में सिर्फ़ 3 facts (लगभग 20 tokens) जाते हैं, 20 messages (लगभग 1500 tokens) नहीं। **Zomato-style**: assistant को याद है `Priya: vegetarian, peanut allergy`, इसलिए वो कभी peanut dish suggest नहीं करता।

---

## 💻 Code Example — Basic
```python
# Pure Python entity memory - no API key needed, runs directly
import re                                   # regex for simple fact extraction
from collections import defaultdict         # dict that auto-creates lists

class EntityMemory:
    """Stores facts per entity: {entity_name: [fact, fact, ...]}."""

    def __init__(self) -> None:
        self.store: dict[str, list[str]] = defaultdict(list)   # entity -> facts

    def extract(self, text: str) -> None:
        """Rule-based extraction for sentences like 'X is Y' / 'X is made in Y'."""
        for match in re.finditer(r"([A-Z][\w ]*?) is ([^.]+)", text):   # find 'Name is something'
            entity, fact = match.group(1).strip(), match.group(2).strip()   # split the match
            if fact not in self.store[entity]:                           # avoid duplicate facts
                self.store[entity].append(fact)                          # save the new fact

    def recall(self, text: str) -> str:
        """Return facts only for entities mentioned in `text`."""
        lines = []                                                       # collected lines
        for entity, facts in self.store.items():                         # check each known entity
            if entity.lower() in text.lower():                           # is it mentioned now?
                lines.append(f"{entity}: " + "; ".join(facts))           # format its facts
        return "\n".join(lines)                                          # prompt-ready string

memory = EntityMemory()                                                  # create the store
memory.extract("Item A is a lithium-ion battery pack. Item A is 48V.")   # learn facts
memory.extract("Item B is a cotton t-shirt.")                            # learn another entity
print(memory.recall("What duty applies to Item A?"))                     # only Item A returned
```

## 💻 Code Example — Advanced
```python
# Production: async LLM extraction + pydantic model + fallback + error handling
import asyncio                                         # async runtime
import json                                            # parse the LLM JSON
import logging                                         # log failures
from pydantic import BaseModel, Field                  # pydantic v2 data models
from openai import AsyncOpenAI, OpenAIError            # openai>=1 async client

logger = logging.getLogger("entity_memory")            # module logger

class Entity(BaseModel):
    """One entity and its facts."""
    name: str                                          # entity name
    facts: list[str] = Field(default_factory=list)     # known facts

class ExtractedFacts(BaseModel):
    """Shape we ask the LLM to return."""
    entities: list[Entity] = Field(default_factory=list)   # all entities found

class AsyncEntityMemory:
    """Per-session entity memory with LLM extraction."""

    def __init__(self, model: str = "gpt-4o-mini", max_facts: int = 10) -> None:
        self.client = AsyncOpenAI()                    # reads OPENAI_API_KEY from env
        self.model = model                             # cheap model for extraction
        self.max_facts = max_facts                     # cap facts per entity
        self.store: dict[str, list[str]] = {}          # the memory itself

    async def update(self, message: str) -> None:
        """Extract entities+facts from a message and merge them."""
        try:
            resp = await self.client.chat.completions.create(   # call the LLM
                model=self.model,                                # chosen model
                messages=[
                    {"role": "system", "content": 'Return JSON {"entities":[{"name":str,"facts":[str]}]}. Only facts stated by the user.'},
                    {"role": "user", "content": message},         # text to analyse
                ],
                response_format={"type": "json_object"},          # force valid JSON
                max_tokens=200,                                   # keep output small
                temperature=0,                                    # deterministic
            )
            data = ExtractedFacts.model_validate(json.loads(resp.choices[0].message.content or "{}"))   # validate shape
        except (OpenAIError, json.JSONDecodeError, ValueError) as exc:   # API or parse failure
            logger.warning("extraction failed: %s", exc)         # log and continue
            return                                               # memory stays unchanged
        for ent in data.entities:                                # merge each entity
            facts = self.store.setdefault(ent.name.lower(), [])  # get or create list
            for fact in ent.facts:                               # each new fact
                if fact not in facts:                            # dedupe
                    facts.append(fact)                           # add it
            self.store[ent.name.lower()] = facts[-self.max_facts:]   # keep newest facts only

    def recall(self, message: str) -> str:
        """Build the context block for entities present in `message`."""
        hits = [f"{k}: {'; '.join(v)}" for k, v in self.store.items() if k in message.lower()]   # matching entities
        return "\n".join(hits)                                   # prompt-ready text

async def main() -> None:
    mem = AsyncEntityMemory()                                    # needs an API key to extract
    await mem.update("Item A is a 48V lithium-ion battery from Vietnam.")   # learn
    print(mem.recall("Duty for item a?"))                        # recall

if __name__ == "__main__":
    asyncio.run(main())                                          # run the demo
```

---

## 🟠 FastAPI Integration
Keep one `AsyncEntityMemory` per session id. Update memory after answering (background task) so the user does not wait for extraction.

```python
from fastapi import FastAPI, BackgroundTasks            # FastAPI + background jobs
from pydantic import BaseModel                          # request body model

app = FastAPI()                                         # app instance
sessions: dict[str, "AsyncEntityMemory"] = {}           # session_id -> memory (use Redis in prod)

class ChatIn(BaseModel):
    session_id: str                                     # who is chatting
    message: str                                        # user text

@app.post("/chat")
async def chat(body: ChatIn, bg: BackgroundTasks) -> dict[str, str]:
    mem = sessions.setdefault(body.session_id, AsyncEntityMemory())   # get/create memory
    context = mem.recall(body.message)                  # facts for entities in this message
    answer = f"(LLM answer using context: {context or 'none'})"       # call your LLM here
    bg.add_task(mem.update, body.message)               # extract facts after responding
    return {"answer": answer}                           # reply immediately
```

---

## 🔗 LangChain / LangGraph Connection
Old `ConversationEntityMemory` is legacy. In LangGraph, keep entities in graph state and add a node that updates them; persist with a checkpointer or a `Store`.

```python
from typing import TypedDict                            # state schema
from langgraph.graph import StateGraph, START, END      # graph builder

class State(TypedDict):
    message: str                                        # latest user message
    entities: dict[str, list[str]]                      # entity memory in state
    answer: str                                         # final answer

def update_entities(state: State) -> dict:
    ents = dict(state["entities"])                      # copy so we do not mutate
    if "battery" in state["message"].lower():           # toy extraction rule
        ents.setdefault("battery", []).append("mentioned by user")   # add a fact
    return {"entities": ents}                           # partial state update

def respond(state: State) -> dict:
    return {"answer": f"Known entities: {state['entities']}"}   # replace with LLM call

g = StateGraph(State)                                   # create graph
g.add_node("update", update_entities)                   # memory-writing node
g.add_node("respond", respond)                          # answering node
g.add_edge(START, "update"); g.add_edge("update", "respond"); g.add_edge("respond", END)   # wire it
app_graph = g.compile()                                 # runnable graph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Injecting ALL entities every turn
✅ Correct: inject only entities present in the current message.

```python
# Wrong - whole store in every prompt, tokens grow forever
prompt = str(memory.store) + user_msg
# Right - only relevant entities
prompt = memory.recall(user_msg) + user_msg
```

❌ Mistake 2: Never resolving conflicts ("origin China" then "origin Vietnam")
✅ Correct: key facts by attribute so newer values overwrite older ones.

```python
# Wrong - both stay, LLM gets confused
facts.append("origin Vietnam")
# Right - attribute dict, latest wins
attrs["origin"] = "Vietnam"
```

---

## 🧠 Tricky Interview Question
**Q**: "Users say 'it' and 'that one' - how does entity memory know which entity?"

**Answer**: Plain string matching fails on pronouns. Use coreference: pass the last 2-3 turns to the extractor and ask it to resolve pronouns to canonical entity names, or keep a "current focus entity" in state that updates on every explicit mention. Also normalise names (lowercase, alias map "Item A" = "item-a") so one real thing has one key.

---

## ⚫ Interview Questions + Answers

Q1: What is entity memory? (Easy)
A1: A store of facts keyed by entity (person, product, code) that is queried by the entities in the current message.

Q2: How is it different from summary memory? (Easy)
A2: Summary memory is one blob of prose and can drop details. Entity memory keeps exact structured facts per entity and retrieves selectively.

Q3: How do you extract entities cheaply? (Medium)
A3: Use a small model (gpt-4o-mini) with JSON mode and `max_tokens` about 200, run in a background task, or use rules/NER (spaCy) for known patterns. Validate with pydantic.

Q4: How do you handle changing facts? (Medium)
A4: Store attributes as key-value pairs with timestamps so newer values overwrite older ones; optionally keep history for audit.

Q5: Design entity memory for 1M users. (Hard)
A5: Partition by `user_id`/`session_id` in Redis or Postgres (JSONB), cap facts per entity, add TTL for stale entities, extract asynchronously via a queue, encrypt PII, and use embeddings when entity names are fuzzy (alias matching). Monitor extraction cost per message.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long sessions with many named things (products, customers, cases)
- Exact facts matter (codes, allergies, preferences)
- You want small prompts

❌ Avoid when:
- Short chats - plain history is enough
- Facts are vague/narrative (use summary or vector memory)
- You cannot afford the extra extraction call

---

## 📊 Visual Diagram
```
 user msg ──► [Extractor LLM] ──► entities+facts
                                      │ merge
                                      ▼
                         ┌─────────────────────────┐
                         │ item a : 48V, Li-ion    │
                         │ priya  : vegetarian     │
                         └───────────┬─────────────┘
 next msg ("duty for Item A?") ──►   │ lookup by mention
                                     ▼
              prompt = system + "item a: 48V, Li-ion" + question
```

---

## 💰 Cost Impact
Extraction adds one small call per message: about 100 input + 60 output tokens on gpt-4o-mini = roughly $0.00005. Recall adds only 20-100 tokens versus 1000+ for full history. Optimise: extract only when the message contains new info (cheap heuristic), batch extraction every N turns, use rules for known fields, cap facts per entity.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Entity | A named thing (person, product) | नामित चीज़/व्यक्ति |
| Fact | A statement about an entity | entity के बारे में बात |
| Coreference | Resolving "it" to a name | "it" को नाम से जोड़ना |
| Canonical name | One standard key per entity | एक standard नाम |
| Extraction | Pulling facts out of text | text से facts निकालना |

---

## ⚡ 3-Line Summary
English: Entity memory keeps exact facts per entity in a key-value store. Only facts for entities in the current message go into the prompt. This keeps prompts small and answers consistent.
Hindi: Entity memory हर entity के exact facts key-value store में रखती है। Current message की entities के facts ही prompt में जाते हैं। इससे prompt छोटा रहता है और जवाब consistent रहते हैं।

---

## ➡️ Next Topic
**377. Vector Memory (MemoryVectorStore)** - when facts are fuzzy, store memories as embeddings and retrieve by similarity.
