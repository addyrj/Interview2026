---

# 021. What is an LLM — How it Works
# हिंदी में: LLM क्या है — कैसे काम करता है

---

## 🔵 Simple Definition (English)
An LLM (Large Language Model) is a neural network trained on billions of text documents to predict the next word (token) given the previous words. It learns patterns, facts, reasoning, and coding by seeing them billions of times. When you send a prompt, it generates a response by predicting tokens one by one until it decides to stop.

## 🔵 सरल परिभाषा (Hindi)
LLM (Large Language Model) एक neural network है जो billions of text documents पर train होती है — अगला word (token) predict करने के लिए। Patterns, facts, reasoning सब कुछ billions of examples देखकर सीखती है। आप prompt भेजते हो → एक-एक token predict करके response generate होता है।

---

## 🔴 Problem it Solves
Before LLMs: you needed separate ML models for each task — one for translation, one for summarization, one for Q&A, one for code generation. Each needed its own training data and maintenance. LLMs are general-purpose — one model handles all text tasks with just a prompt change.

## 🔴 यह क्यों बना? (Hindi)
LLMs से पहले: हर task के लिए अलग ML model चाहिए था। LLM एक model से सब tasks handle करता है — बस prompt बदलो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Training: fed billions of text examples (books, web, code)
Step 2 → Learns to predict "next token" — optimized to minimize prediction error
Step 3 → Emergent abilities appear at scale: reasoning, coding, translation
Step 4 → RLHF (Reinforcement Learning from Human Feedback): humans rate outputs,
          model learns to give better, safer responses
Step 5 → At inference: you send prompt (input tokens)
Step 6 → Model runs forward pass → softmax over vocabulary → picks next token
Step 7 → Repeats until <stop> token or max_tokens reached
Step 8 → Output: sequence of predicted tokens → decoded to text
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Training: billions of text देखी
Step 2 → "अगला token predict करो" optimize किया
Step 3 → Scale पर: reasoning, coding अपने आप आई
Step 4 → RLHF: humans ने better responses चुने → safe model बना
Step 5 → Inference: आपका prompt = input tokens
Step 6 → Forward pass → vocabulary पर softmax → next token choose
Step 7 → <stop> token या max_tokens तक repeat
Step 8 → Tokens → text = आपका response
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "What is the HS code for iPhone 15?" The LLM doesn't look up a database — it generates an answer token by token based on patterns from training data. If documents are provided via RAG, it generates an answer grounded in those documents. The model doesn't "know" — it "predicts the most likely response given the context."

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "iPhone 15 का HS code क्या है?" LLM database lookup नहीं करता — training data के patterns से token-by-token answer generate करता है। RAG से documents दो → उन documents पर grounded answer आता है।

---

## 💻 Code Example — Basic
```python
# Basic LLM interaction — OpenAI API
from openai import OpenAI

client = OpenAI()   # reads OPENAI_API_KEY from env automatically

# Simplest possible LLM call:
response = client.chat.completions.create(
    model="gpt-4o-mini",                  # model name
    messages=[
        {
            "role": "system",             # system prompt: LLM's persona/instructions
            "content": "You are a helpful tariff classification assistant."
        },
        {
            "role": "user",               # user's message
            "content": "What is an LLM?"
        }
    ],
    max_tokens=500,        # max tokens in response
    temperature=0.7,       # randomness: 0=deterministic, 2=very random
)

# Extract the text response:
text = response.choices[0].message.content
print(text)

# Token usage (important for cost!):
print(f"Input tokens:  {response.usage.prompt_tokens}")
print(f"Output tokens: {response.usage.completion_tokens}")
print(f"Total tokens:  {response.usage.total_tokens}")
```

## 💻 Code Example — Advanced
```python
# Production: typed, async, with error handling
from openai import AsyncOpenAI
from pydantic import BaseModel
import os

# Response schema for structured access:
class LLMResponse(BaseModel):
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str

async def call_llm(
    system_prompt: str,
    user_message: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1000,
    temperature: float = 0.1,   # low temperature for factual tasks like tariff lookup
) -> LLMResponse:
    """Single LLM call with typing and token tracking."""
    client = AsyncOpenAI()   # async client for FastAPI

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return LLMResponse(
        content=response.choices[0].message.content,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        total_tokens=response.usage.total_tokens,
        model=response.model,    # actual model used (may differ from requested)
    )

# Usage:
import asyncio

async def main():
    result = await call_llm(
        system_prompt="You classify tariff codes. Answer concisely.",
        user_message="What HS code category covers smartphones?",
    )
    print(result.content)
    print(f"Cost estimate: ${result.total_tokens / 1_000_000 * 0.15:.6f}")  # gpt-4o-mini price

asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI, APIError, RateLimitError

app = FastAPI()
client = AsyncOpenAI()   # one client for the whole app

class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "You are a helpful tariff classification assistant."

class ChatResponse(BaseModel):
    response: str
    tokens_used: int

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user",   "content": request.message},
            ],
            max_tokens=500,
        )
        return ChatResponse(
            response=result.choices[0].message.content,
            tokens_used=result.usage.total_tokens,
        )
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
```

---

## 🔗 LangChain / LangGraph Connection
```python
# LangChain wraps LLM APIs into a unified interface:
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# LangChain uses the same concept — messages in, text out:
messages = [
    SystemMessage(content="You classify tariff codes."),
    HumanMessage(content="What HS code for smartphones?"),
]
response = await llm.ainvoke(messages)
print(response.content)

# LangGraph uses LLM as a "node" in a workflow graph:
# state → llm_node → next_node
# The LLM is just one step in a larger pipeline
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating LLM output as always correct
```python
# Wrong — trust LLM output blindly:
hs_code = llm_response   # might be hallucinated!
store_in_database(hs_code)

# Correct — validate against known data:
if hs_code not in valid_hs_codes_set:
    raise ValueError(f"Invalid HS code: {hs_code}")
```

❌ Mistake 2: Creating new client per request (expensive)
```python
# Wrong — creates connection overhead on every request:
@app.post("/chat")
async def chat(msg: str):
    client = AsyncOpenAI()   # new client each time!
    ...

# Correct — one client at module/app level:
client = AsyncOpenAI()   # module-level

@app.post("/chat")
async def chat(msg: str):
    response = await client.chat.completions.create(...)
```

---

## 🧠 Tricky Interview Question

**Q**: "If LLMs just predict the next token, how can they reason? Aren't they just autocomplete?"

**Answer**: The "just predicting next tokens" framing understates what happened at scale. Training on billions of documents that contain reasoning (math solutions, code with explanations, logical arguments) caused the model to learn latent representations of reasoning. Chain-of-Thought prompting works because asking the model to "think step by step" changes the distribution of tokens it generates — it generates reasoning-like intermediate tokens that steer toward correct final answers. It's not "just autocomplete" — it's a general-purpose pattern matcher trained on all human knowledge.

---

## ⚫ Interview Questions + Answers

Q1: What does "LLM" stand for and what makes it "large"?
A1: Large Language Model. "Large" refers to the number of parameters (weights) — GPT-3 had 175B parameters, GPT-4 is estimated at 1.8T. More parameters = more capacity to memorize patterns from training data. "Language" = it models the probability distribution of text (predicts likely next tokens).

Q2: What is the difference between a base model and an instruction-tuned model?
A2: Base model: trained only to predict next tokens — not useful directly (will continue your sentence, not answer your question). Instruction-tuned model: further fine-tuned using RLHF or DPO to follow instructions, answer questions, be helpful and safe. gpt-4o is instruction-tuned; most production use cases use instruction-tuned models.

Q3: What is the transformer architecture and why does it matter for LLMs?
A3: Transformers use self-attention — each token can "attend" to every other token in the context. This allows modeling long-range dependencies (a word at position 1000 can influence the word at position 1050). Before transformers, RNNs processed sequentially — transformers process all tokens in parallel, enabling training at scale. All modern LLMs (GPT, Claude, Gemini) are transformer-based.

Q4: What is RLHF and why is it important?
A4: Reinforcement Learning from Human Feedback. After base pre-training, humans rate model outputs for helpfulness and safety. A reward model is trained on these ratings. Then the LLM is fine-tuned using RL (PPO) to maximize the reward. Result: model learns to give helpful, harmless, honest responses. Without RLHF, models would happily generate harmful content or give confident wrong answers.

Q5: What is the difference between GPT-4o, GPT-4o-mini, and when would you use each?
A5: GPT-4o: highest quality, multimodal (text+vision+audio), high cost (~$5/M input tokens). GPT-4o-mini: 95% quality for most tasks, much cheaper (~$0.15/M input tokens), faster. For Tariff Classification: use gpt-4o-mini for most queries (cost-efficient), escalate to gpt-4o for complex cases where accuracy matters most. Never use a $5/M model when a $0.15/M model handles the task equally well.

---

## 🔷 When to Use + When Not to Use

✅ Use LLMs when:
- Natural language understanding or generation is needed
- Rules are too complex to hardcode (tariff classification has thousands of categories)
- Extracting structured info from unstructured text
- Summarization, Q&A, code generation

❌ Avoid LLMs when:
- Deterministic output required (use database lookups instead)
- Simple pattern matching (regex is faster and cheaper)
- Real-time requirements < 100ms (LLM latency is 500ms–5s)
- Sensitive/regulated output with no tolerance for errors

---

## 📊 Visual Diagram
```
Input Prompt
      │
      ▼
Tokenizer → [token_ids: 1234, 567, 891, ...]
      │
      ▼
Transformer (N layers)
  ┌─────────────────────────────┐
  │  Self-Attention: each token │
  │  attends to all other tokens│
  │  → context understanding    │
  │                             │
  │  Feed-Forward: transforms   │
  │  attended representation    │
  └─────────────────────────────┘
      │  (repeated N times)
      ▼
Output layer → softmax over 50,000+ vocabulary
      │
      ▼
Next token probabilities: {"the": 0.42, "a": 0.18, "an": 0.12, ...}
      │
      ▼
Sample based on temperature → pick token → append to context → repeat
```

---

## 💰 Cost Impact
- gpt-4o-mini: $0.15/1M input, $0.60/1M output tokens
- gpt-4o: $5.00/1M input, $15.00/1M output tokens
- Claude Haiku: $0.25/1M input, $1.25/1M output tokens
- Tariff query (avg 500 input + 200 output tokens) with gpt-4o-mini: ~$0.000195/query
- 100K queries/day = ~$19.50/day — highly affordable
- Rule: use the smallest model that gets the job done; benchmark first

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LLM | Large Language Model | बड़ा भाषा model |
| Token | Unit of text (~4 chars) | Text की छोटी unit |
| Context window | Max tokens LLM can see at once | एक साथ देख सकने वाले tokens |
| Temperature | Randomness of output | Output की randomness |
| RLHF | Human feedback training | Human feedback से training |
| Inference | Running the model to get output | Model से output निकालना |
| Hallucination | Confident but wrong output | गलत पर confident output |

---

## ⚡ 3-Line Summary
English: An LLM is a transformer neural network trained to predict the next token — scaled to billions of parameters, it develops emergent reasoning abilities. It generates responses token by token until a stop condition. Use gpt-4o-mini for cost-efficiency (33x cheaper than gpt-4o) and escalate only for complex tasks.
Hindi: LLM transformer neural network है — billions of parameters से emergent reasoning आती है। Token-by-token response generate होता है। Cost के लिए gpt-4o-mini (33x सस्ता), complex tasks के लिए gpt-4o।

---

## ➡️ Next Topic
**022. Tokens — Complete Guide** — what tokens are, why they matter for cost and context limits, how to count them, `tiktoken` library.
