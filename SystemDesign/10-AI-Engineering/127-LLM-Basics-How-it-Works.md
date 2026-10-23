# 127. LLM Basics — How it Works
# हिंदी में: LLM (Large Language Model) की बुनियाद — बहुत बड़ा neural network जो अरबों शब्दों से सीखकर अगला token (शब्द का टुकड़ा) अनुमान लगाता है; tokens, context window, temperature, training और inference कैसे काम करते हैं

---

## 🔵 Simple Definition (English)
A **Large Language Model (LLM)** is a neural network, usually a **Transformer**, trained on massive amounts of text (and often code and images) to **predict the next token** given the previous tokens. By repeatedly predicting the next token, it generates text: answers, code, summaries, translations, JSON.
Key concepts:
- **Token**: a chunk of text (a word, part of a word or punctuation). Models read and write tokens, and pricing and limits are in tokens. In English, roughly 1 token ≈ ¾ of a word; **Hindi/Devanagari text usually needs more tokens** per word.
- **Context window**: the maximum number of tokens (input + output) the model can consider at once.
- **Training stages**: **pretraining** (next-token prediction on huge corpora) → **instruction tuning / SFT** (learn to follow instructions) → **preference tuning** (RLHF/RLAIF/DPO: helpful, honest, harmless) → optional domain fine-tuning.
- **Inference**: **prefill** (process the prompt) + **decode** (generate tokens one by one). Key metrics are latency (TTFT = time to first token), throughput (tokens/sec) and cost per token.
- **Sampling controls**: temperature, top-p and max tokens.
- **Limitations**: hallucinations, a knowledge cutoff, sensitivity to prompts, no built-in memory between calls (stateless), and imperfect arithmetic without tools.

## 🔵 सरल परिभाषा (Hindi)
LLM एक बहुत बड़ा neural network (आम तौर पर Transformer) है जो भारी मात्रा में text पढ़कर यह सीखता है कि पिछले tokens के बाद अगला token क्या होगा; बार-बार अगला token चुनकर वो जवाब, code, सारांश, अनुवाद बनाता है।
मुख्य बातें: token = text का टुकड़ा (क़ीमत और सीमा tokens में; हिंदी में अंग्रेज़ी से ज़्यादा tokens लगते हैं); context window = एक बार में कितने tokens देख सके; training = pretraining → instruction tuning → preference tuning (RLHF); inference = prompt पढ़ना (prefill) + एक-एक token बनाना (decode); temperature से randomness; कमियाँ — गढ़ी हुई बातें (hallucination), ज्ञान की cutoff तारीख़, कोई याददाश्त नहीं (हर call अलग)।

---

## 🔴 Problem it Solves
Before LLMs, every language task needed a **separate model and a labelled dataset**: one for sentiment, one for translation, one for intent classification in a chatbot, plus hand-written rules. That was expensive, brittle and slow to build.
LLMs are **general-purpose**: one model can summarize, translate, classify, extract structured data, write code, answer questions over documents and plan multi-step actions, guided only by **instructions (prompts)** and a few examples.
For engineers, an LLM is like a new kind of **probabilistic API**: powerful and flexible, but with latency, cost, non-determinism and correctness risks. You must understand how it works to design reliable systems (RAG, tools, guardrails, evals) around it.

## 🔴 यह क्यों बना? (Hindi)
LLMs से पहले हर भाषा वाले काम के लिए अलग model और अलग labelled डेटा चाहिए था — sentiment, अनुवाद, chatbot के intent, ऊपर से हाथ के नियम; महँगा, नाज़ुक और धीमा।
LLM एक ही model से सारांश, अनुवाद, वर्गीकरण, डेटा निकालना, code, documents पर सवाल-जवाब, योजना — सब सिर्फ़ निर्देश (prompt) और कुछ उदाहरणों से। Engineer के लिए यह नई तरह का "probabilistic API" है — ताक़तवर, पर latency, ख़र्च, हर बार अलग जवाब और ग़लती का जोखिम; इसलिए अंदर की समझ ज़रूरी।

---

## 🟢 How it Works — Step by Step

### From text to tokens to text

```
"Paneer tikka recipe in 3 steps" ──tokenizer (BPE)──► [P, aneer, ▁t, ikka, ▁recipe, ▁in, ▁3, ▁steps]
                                                     → token IDs [ 47, 8812, 259, ... ]
→ embeddings (vectors) → N Transformer layers (self-attention + feed-forward) → probability over
  vocabulary for NEXT token: { "1": 0.31, "Step": 0.22, "Here": 0.12, ... }
→ sample a token (temperature/top-p) → append → repeat until stop token / max_tokens
```

### Transformer & attention (intuition)

```
Self-attention: each token looks at all previous tokens and decides which matter
  "The order was late because the rider ... he"  → "he" attends strongly to "rider"
Layers stack: early layers capture syntax, later layers capture meaning, facts, reasoning patterns
Causal (decoder-only) models: token i can only attend to tokens ≤ i → enables generation
Parameters (weights) = learned numbers; billions of them store "knowledge" & skills
```

### Training pipeline

```
1. PRETRAINING: next-token prediction over trillions of tokens (web, books, code) → "base model"
   (knows language & facts, but doesn't follow instructions well)
2. SUPERVISED FINE-TUNING (SFT / instruction tuning): curated prompt → ideal answer pairs
3. PREFERENCE TUNING: RLHF / RLAIF / DPO — humans or AI rank responses; model learns helpful,
   honest, harmless behaviour (and when to refuse)
4. (Optional) reasoning training: reward correct multi-step solutions (math/code) → "reasoning models"
   that think longer before answering
Knowledge cutoff: model knows little about events after its training data ends → use tools/RAG
```

### Inference: what costs time and money

```
PREFILL: process all prompt tokens in parallel → fast per token, grows with prompt length
DECODE: generate output tokens ONE AT A TIME (each needs a forward pass) → output tokens dominate latency
KV cache: stores attention keys/values of previous tokens so each new token doesn't recompute everything
Metrics: TTFT (time to first token), TPOT / tokens per second, total latency ≈ TTFT + output_tokens / speed
Pricing: per input token (cheaper) + per output token (more expensive); cached input tokens cheaper
Rule of thumb: long outputs = slow & costly → ask for concise answers, structured output
```

### Sampling parameters

```
temperature: 0–0.3 → focused, repeatable (extraction, classification, code)
             0.7–1.0 → more creative/variable (marketing copy, brainstorming)
top_p: nucleus sampling (choose from smallest set of tokens covering p probability mass)
max_tokens: hard cap on output length (cost & latency control)
stop sequences: stop generation at a marker
Even at temperature 0, outputs aren't guaranteed identical across runs/versions → design for variance
```

### Roles & statelessness

```
messages: system (instructions, persona, rules) → user → assistant → user …
The API is STATELESS: each call must include the conversation history you want the model to see
→ long chats grow the prompt (cost/latency) → summarize/trim history, store memory externally (Topic 145)
```

### Tokens & Indian languages

```
Tokenizers trained mostly on English → Devanagari/Tamil/Bengali words split into more tokens
→ same sentence in Hindi may cost 2–4× tokens vs English (varies by model)
→ affects cost, latency and context usage for vernacular apps; measure with the provider's token counter
→ Indic-focused models (e.g., from Sarvam AI, AI4Bharat research) use tokenizers optimized for Indian scripts
```

### Limitations to design around

```
Hallucination (confident wrong facts) → grounding/RAG, citations, verification (Topic 152)
No real-time knowledge → tools/web search/RAG
Weak exact arithmetic/counting → calculator/code tools
Prompt sensitivity & non-determinism → evals, structured outputs, temperature control
Context limits & "lost in the middle" → retrieval, chunking, put key info at start/end
Safety & prompt injection → guardrails (Topic 149)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Text को tokenizer tokens में तोड़ता है → हर token का vector → कई Transformer layers (self-attention: हर token पिछले tokens में से ज़रूरी वाले देखता है) → अगले token की संभावनाएँ → एक token चुनो, जोड़ो, दोहराओ।
2. Training: पहले अरबों-ख़रबों tokens पर अगला token अनुमान (base model) → instruction tuning (निर्देश मानना) → RLHF/DPO (मददगार, ईमानदार, सुरक्षित) → कभी-कभी reasoning training; एक cutoff तारीख़ के बाद की बातें नहीं पता।
3. Inference: prompt एक साथ पढ़ा जाता है (prefill), जवाब एक-एक token (decode) — इसलिए लंबा जवाब = धीमा और महँगा; KV cache पुराने tokens का हिसाब दोबारा नहीं करवाता; नाप: TTFT और tokens/सेकंड।
4. Temperature कम (0–0.3) = स्थिर जवाब (extraction, code), ज़्यादा = रचनात्मक; max_tokens से सीमा; API stateless है — हर call में ज़रूरी इतिहास भेजो।
5. हिंदी/तमिल जैसी भाषाओं में अक्सर 2–4 गुना tokens — ख़र्च और latency पर असर; कमियाँ (hallucination, पुराना ज्ञान, गणित) RAG, tools, guardrails और evals से संभालो।

---

## 🟡 Real World Example

**"Attention Is All You Need" (Google, 2017)** — introduced the Transformer architecture behind GPT, Claude, Gemini and Llama.

**ChatGPT (Nov 2022)** — instruction-tuned plus RLHF on top of GPT-3.5. It reached an estimated 100M users in about two months, showing the power of the instruction and preference tuning stage on top of pretraining.

**Claude (Anthropic)** — trained with RLHF and Constitutional AI (a set of principles used to guide AI feedback), and now offered as a family of models at different capability, speed and cost points (Opus, Sonnet, Haiku), which is why model selection and routing matter in system design.

**Indian context** — Sarvam AI and research groups like AI4Bharat build models, tokenizers and datasets for Indian languages, and the Government's **Bhashini** mission provides language AI (translation, speech) for 22 scheduled languages. Token efficiency and Indic quality are key concerns for apps serving Bharat.

## 🟡 Real Example Hindi में
Google के 2017 के paper "Attention Is All You Need" से Transformer आया — GPT, Claude, Gemini, Llama सबकी नींव। ChatGPT (नवंबर 2022) GPT-3.5 पर instruction tuning + RLHF था और ~2 महीने में अनुमानित 10 करोड़ यूज़र्स तक पहुँचा।
Claude (Anthropic) RLHF और Constitutional AI से बना और Opus/Sonnet/Haiku जैसे अलग क्षमता-गति-क़ीमत वाले models देता है; भारत में Sarvam AI, AI4Bharat भारतीय भाषाओं के models/tokenizers बनाते हैं और सरकार का **Bhashini** 22 भाषाओं के लिए अनुवाद/speech देता है।

---

## 🟠 My Stack Example

### First call to Claude (Python) + token counting
```python
# pip install anthropic
import anthropic
client = anthropic.Anthropic()                       # reads ANTHROPIC_API_KEY from env

messages = [{"role": "user", "content": "Explain in 3 bullet points why my Swiggy order might be late."}]

# Count tokens BEFORE sending (cost/latency planning)
count = client.messages.count_tokens(model="claude-sonnet-5-5", messages=messages)
print("input tokens:", count.input_tokens)

resp = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=300,                                  # cap output → controls cost & latency
    temperature=0.3,                                 # focused answer
    system="You are a concise customer-support assistant for a food delivery app.",
    messages=messages,
)
print(resp.content[0].text)
print(resp.usage)                                    # input_tokens, output_tokens → log for cost tracking
```

### Same in Node (Express endpoint)
```js
import Anthropic from '@anthropic-ai/sdk';
const anthropic = new Anthropic();                   // ANTHROPIC_API_KEY from env

app.post('/api/explain', async (req, res) => {
  const msg = await anthropic.messages.create({
    model: 'claude-haiku-5-5',                       // fast & cheap for simple tasks
    max_tokens: 200,
    messages: [{ role: 'user', content: `Explain simply: ${req.body.topic}` }],
  });
  res.json({ text: msg.content.find((b) => b.type === 'text')?.text, usage: msg.usage });
});
```

### Compare token usage: English vs Hindi (measure, don't guess)
```python
for text in ["Where is my order? It is 30 minutes late.",
             "मेरा ऑर्डर कहाँ है? यह 30 मिनट लेट है।"]:
    n = client.messages.count_tokens(model="claude-sonnet-5-5",
                                     messages=[{"role": "user", "content": text}]).input_tokens
    print(n, "tokens →", text)
# Use results to budget costs for vernacular features
```

### Stateless chat: you send the history every time
```python
history = [
    {"role": "user", "content": "I ordered biryani at 8 pm."},
    {"role": "assistant", "content": "Got it. How can I help with your biryani order?"},
    {"role": "user", "content": "It's 9 pm now and not delivered."},     # model only "remembers" what you send
]
resp = client.messages.create(model="claude-sonnet-5-5", max_tokens=200, messages=history)
```

### Temperature effect (quick experiment)
```python
for t in (0.0, 1.0):
    out = client.messages.create(model="claude-haiku-5-5", max_tokens=40, temperature=t,
            messages=[{"role": "user", "content": "Give a catchy name for a Diwali sweets sale."}])
    print(t, out.content[0].text)
```

---

## ⚫ Interview Questions + Answers

**Q1: How does an LLM generate text?**
A1: The input text is split into tokens and converted to embeddings. They pass through stacked Transformer layers where self-attention lets each position weigh relevant earlier tokens, and the model outputs a probability distribution over the vocabulary for the next token. A decoding strategy (temperature, top-p) picks a token, which is appended to the sequence, and the process repeats autoregressively until a stop condition or max tokens is reached. A KV cache stores intermediate attention state so each new token is computed efficiently.

**Q2: What are pretraining, instruction tuning and RLHF?**
A2: Pretraining teaches a base model language, facts and patterns via next-token prediction on enormous text and code corpora, but it doesn't reliably follow instructions. Instruction tuning (supervised fine-tuning) trains it on curated prompt-response pairs so it answers requests helpfully and in the expected format. Preference tuning (RLHF, RLAIF or DPO) uses human or AI comparisons of responses to optimize for helpfulness, honesty and harmlessness, including appropriate refusals. Some models add reinforcement learning on verifiable tasks to improve multi-step reasoning.

**Q3: What drives LLM latency and cost?**
A3: Cost is per token, with output tokens typically priced higher than input and cached input tokens discounted. Latency is time to first token (queueing plus prefill, which grows with prompt length) plus output tokens divided by generation speed, since decoding is sequential. Long prompts (big context, long histories), long outputs and larger models increase both. Reduce them with concise prompts, retrieval of only relevant context, output caps, structured outputs, prompt caching, smaller models for simple tasks and streaming to improve perceived latency.

**Q4: What is a context window and why does it matter?**
A4: It's the maximum number of tokens (input plus output) a model can process in one call. It limits how much conversation history, retrieved documents or files you can include. Even within the limit, very long contexts raise cost and latency, and models can miss details buried in the middle. So systems use retrieval (RAG), chunking, summarization of history and careful ordering of instructions and key facts, rather than stuffing everything into the prompt.

**Q5: Why do LLMs hallucinate, and what does that mean for system design?**
A5: LLMs generate statistically plausible continuations, not verified facts. Without grounding they may produce fluent but false statements, especially about niche, recent or numeric information, or when prompted to answer anyway. System design must treat outputs as untrusted: ground answers in retrieved sources with citations, use tools for facts and calculations, constrain outputs (schemas), allow "I don't know", validate and verify critical outputs, add human review for high-stakes decisions and continuously evaluate quality.

---

## 🔷 Trade-offs
✅ General-purpose, fast to build features, multilingual — ❌ non-deterministic, can hallucinate, needs evals.
✅ Larger models: better reasoning — ❌ higher cost & latency (route by task).
✅ Long context: fewer retrieval steps — ❌ cost, latency, "lost in the middle".
✅ Hosted APIs: no infra — ❌ data governance, vendor dependency; self-hosted open models: control — ❌ GPU ops.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LLM | Large language model | बड़ा भाषा model |
| Token | Unit of text for models | text का टुकड़ा |
| Transformer | Attention-based architecture | attention वाला ढाँचा |
| Self-attention | Tokens weighing other tokens | tokens का आपसी ध्यान |
| Context window | Max tokens per call | एक बार में अधिकतम tokens |
| Pretraining | Next-token learning on big data | बड़े डेटा पर सीखना |
| RLHF | Reinforcement learning from human feedback | इंसानी feedback से सुधार |
| Temperature | Randomness of sampling | जवाब की randomness |
| TTFT | Time to first token | पहला token आने का समय |
| Hallucination | Fluent but false output | गढ़ी हुई ग़लत बात |

---

## ⚡ 3-Line Summary
**English:**
1. LLMs are Transformers trained to predict the next token; pretraining + instruction tuning + preference tuning make them helpful assistants.
2. Everything is tokens: context window, cost (input/output), latency (TTFT + sequential decode); temperature controls variability; APIs are stateless.
3. Design around limits: hallucinations, knowledge cutoff, arithmetic, prompt sensitivity, token-heavy Indian languages — with RAG, tools, guardrails and evals.

**Hindi:**
1. LLM Transformer है जो अगला token अनुमान लगाता है; pretraining + instruction + preference tuning से सहायक बनता है।
2. सब कुछ tokens में: context window, ख़र्च, latency; temperature से randomness; API stateless।
3. कमियों के हिसाब से design: hallucination, पुराना ज्ञान, गणित, हिंदी में ज़्यादा tokens — RAG, tools, guardrails, evals।

---

## ➡️ Next Topic Suggestion
**128. OpenAI API + Claude API** — Next: how to actually call LLM providers from your backend: messages, system prompts, streaming, tool calls, errors, rate limits, retries and choosing between providers and models.
