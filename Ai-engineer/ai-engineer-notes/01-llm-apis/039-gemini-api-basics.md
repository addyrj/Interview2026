---

# 039. Gemini API Basics
# हिंदी में: Gemini API की बुनियादी बातें

---

## 🔵 Simple Definition (English)
Gemini is Google's family of multimodal LLMs, available through the Gemini Developer API (API key from Google AI Studio) and through Vertex AI on Google Cloud. In Python you use the `google-genai` SDK: create a `genai.Client`, then call `client.models.generate_content(model=..., contents=...)`. The text is in `response.text`.

## 🔵 सरल परिभाषा (Hindi)
Gemini Google के multimodal LLMs का परिवार है, जो Gemini Developer API (Google AI Studio से API key) और Google Cloud के Vertex AI के ज़रिए मिलता है। Python में `google-genai` SDK use होता है: `genai.Client` बनाओ, फिर `client.models.generate_content(model=..., contents=...)` call करो। Text `response.text` में होता है।

---

## 🔴 Problem it Solves
Different models are best at different jobs. Gemini offers very large context windows, strong multimodal input (text, images, audio, video, PDFs), a generous free tier for prototyping, and tight integration with Google Cloud. Learning its API completes your multi-provider toolkit and gives another fallback option.

## 🔴 यह क्यों बना? (Hindi)
अलग-अलग models अलग कामों में बेहतर होते हैं। Gemini बहुत बड़ी context windows, मज़बूत multimodal input (text, images, audio, video, PDFs), prototyping के लिए free tier और Google Cloud के साथ गहरा integration देता है। इसकी API सीखने से आपका multi-provider toolkit पूरा होता है और एक और fallback विकल्प मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Get a key from Google AI Studio; set GEMINI_API_KEY (or GOOGLE_API_KEY)
Step 2 → pip install google-genai
Step 3 → from google import genai ; client = genai.Client()  (reads key from env)
Step 4 → Call client.models.generate_content(model="gemini-...", contents="...")
Step 5 → Settings go in config=types.GenerateContentConfig(system_instruction, temperature, max_output_tokens)
Step 6 → Read response.text and response.usage_metadata (prompt_token_count, candidates_token_count)
Step 7 → Async: await client.aio.models.generate_content(...)
Step 8 → Streaming: client.models.generate_content_stream(...) yields chunks with .text
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Google AI Studio से key लो; GEMINI_API_KEY (या GOOGLE_API_KEY) set करो
Step 2 → pip install google-genai
Step 3 → from google import genai ; client = genai.Client()  (key env से पढ़ता है)
Step 4 → client.models.generate_content(model="gemini-...", contents="...") call करो
Step 5 → Settings config=types.GenerateContentConfig(system_instruction, temperature, max_output_tokens) में
Step 6 → response.text और response.usage_metadata (prompt_token_count, candidates_token_count) पढ़ो
Step 7 → Async: await client.aio.models.generate_content(...)
Step 8 → Streaming: client.models.generate_content_stream(...) .text वाले chunks देता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A broker uploads a 120-page scanned tariff schedule PDF. Gemini's large context window and native PDF input let the team ask questions over the whole document in a quick prototype, without building chunking first. In production the team still uses RAG for cost, but Gemini remains an option for one-off deep document reviews and as a fallback provider.

**Zomato AI**: Menu photo understanding: send a restaurant menu image and get structured dish data.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: Broker 120-page का scanned tariff schedule PDF upload करता है। Gemini की बड़ी context window और native PDF input से team बिना chunking बनाए पूरे document पर सवाल पूछकर जल्दी prototype बना सकती है। Production में cost के लिए RAG ही रहता है, पर one-off गहरे document reviews और fallback provider के रूप में Gemini विकल्प रहता है।

**Zomato AI**: Menu photo समझना: restaurant menu की image भेजो और structured dish data पाओ।

---

## 💻 Code Example — Basic
```python
# Basic Gemini call (needs: pip install google-genai, and GEMINI_API_KEY)
import os                                        # env access
from google import genai                         # new unified SDK
from google.genai import types                   # config classes

if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
    raise SystemExit("Set GEMINI_API_KEY first")  # fail early with clear message

client = genai.Client()                          # reads the key from env

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")   # check docs for current model names

response = client.models.generate_content(
    model=MODEL,                                 # model id
    contents="HS heading for a smartphone?",     # plain string is one user turn
    config=types.GenerateContentConfig(
        system_instruction="You are a customs tariff assistant. Be concise.",  # system prompt
        temperature=0,                           # deterministic
        max_output_tokens=100,                   # cap output
    ),
)

print(response.text)                             # answer text
um = response.usage_metadata                     # token usage
print("tokens in/out:", um.prompt_token_count, um.candidates_token_count)
```

## 💻 Code Example — Advanced
```python
# Production wrapper: typed result, errors, sync + async, safety-block handling
import asyncio                                           # async runner
import logging                                           # logs
import os                                                # env
from dataclasses import dataclass                        # result container
from typing import Optional                              # type hints

from google import genai                                 # SDK
from google.genai import errors, types                   # error classes + config

logger = logging.getLogger(__name__)                     # logger
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")    # configurable model id
client = genai.Client()                                  # one shared client


@dataclass
class GeminiResult:
    text: str                                            # answer
    input_tokens: int                                    # prompt tokens
    output_tokens: int                                   # candidate tokens


def _config(system: str) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=system, temperature=0, max_output_tokens=300)


def _to_result(resp: types.GenerateContentResponse) -> Optional[GeminiResult]:
    text = resp.text                                     # can be None if blocked/empty
    if not text:
        logger.warning("empty response (blocked or no candidates)")
        return None
    um = resp.usage_metadata
    return GeminiResult(text, um.prompt_token_count or 0, um.candidates_token_count or 0)


def ask(prompt: str, system: str = "Be concise.") -> Optional[GeminiResult]:
    try:
        resp = client.models.generate_content(model=MODEL, contents=prompt, config=_config(system))
    except errors.APIError as exc:                       # HTTP-level API errors (has .code)
        logger.error("gemini error %s: %s", getattr(exc, "code", "?"), exc)
        return None
    return _to_result(resp)


async def aask(prompt: str, system: str = "Be concise.") -> Optional[GeminiResult]:
    try:
        resp = await client.aio.models.generate_content(   # async interface lives under .aio
            model=MODEL, contents=prompt, config=_config(system))
    except errors.APIError as exc:
        logger.error("async gemini error: %s", exc)
        return None
    return _to_result(resp)


if __name__ == "__main__":
    print(asyncio.run(aask("HS heading for a laptop?")))
```

---

## 🟠 FastAPI Integration

```python
import os                                          # env
from fastapi import FastAPI, HTTPException         # framework
from pydantic import BaseModel, Field              # pydantic v2
from google import genai                           # SDK
from google.genai import errors, types             # errors + config

app = FastAPI()                                    # app
client = genai.Client()                            # shared client
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class Body(BaseModel):
    product: str = Field(min_length=2, max_length=500)


@app.post("/classify")
async def classify(b: Body) -> dict:
    try:
        resp = await client.aio.models.generate_content(
            model=MODEL, contents=b.product,
            config=types.GenerateContentConfig(
                system_instruction="Return only the 6-digit HS code.",
                temperature=0, max_output_tokens=30))
    except errors.APIError as exc:
        status = 429 if getattr(exc, "code", None) == 429 else 502
        raise HTTPException(status_code=status, detail="AI service error")
    if not resp.text:                              # safety block or empty candidate
        raise HTTPException(status_code=422, detail="No answer produced")
    return {"hs_code": resp.text.strip(),
            "tokens": resp.usage_metadata.total_token_count}
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-google-genai` provides `ChatGoogleGenerativeAI` (chat) and `GoogleGenerativeAIEmbeddings`. It works in LCEL chains and LangGraph nodes like any other chat model.

```python
from langchain_google_genai import ChatGoogleGenerativeAI   # pip install langchain-google-genai
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)   # reads GOOGLE_API_KEY
prompt = ChatPromptTemplate.from_messages([
    ("system", "Return only the 6-digit HS code."),
    ("human", "{product}"),
])
chain = prompt | llm
# print(chain.invoke({"product": "power bank"}).content)   # needs GOOGLE_API_KEY
# Note: LangChain's wrapper reads GOOGLE_API_KEY; the raw SDK also accepts GEMINI_API_KEY.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the old `google-generativeai` package examples (`genai.configure`, `GenerativeModel`)
✅ Correct: New code should use `google-genai` (`genai.Client`). Check which package a tutorial uses.

```python
# Older style (legacy package)
# import google.generativeai as genai; genai.configure(api_key=...); genai.GenerativeModel(...)
# Current style
from google import genai
client = genai.Client()
```

❌ Mistake 2: Assuming `response.text` always exists
✅ Correct: It can be empty if the output was blocked by safety filters or stopped early; check candidates and `finish_reason`.

❌ Mistake 3: Hard-coding model names
✅ Correct: Names change (preview, stable, deprecated); keep in config.

❌ Mistake 4: Mixing up Developer API and Vertex AI auth
✅ Correct: Developer API uses an API key; Vertex uses Google Cloud credentials and project/location (`genai.Client(vertexai=True, project=..., location=...)`).

---

## 🧠 Tricky Interview Question

**Q**: "Your Gemini classifier returns an empty string for some legitimate customs queries (for example about restricted chemicals). Why, and how do you handle it?"

**Answer**: Safety filters can block a response or prompt, leaving `response.text` empty while the call itself succeeded (HTTP 200). Inspect `response.candidates[0].finish_reason` and `response.prompt_feedback` to see why. Mitigations: adjust safety settings where policy allows (`types.SafetySetting` in the config), rephrase the prompt with legitimate context, treat empty results as a distinct state (not an error and not an answer), route to a fallback model or a human reviewer, and log the block reason for audit.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which package and class do you use for Gemini in Python?
A1: `google-genai`, with `from google import genai` and `genai.Client()`.

Q2: [Easy] Where is the system prompt set?
A2: In `GenerateContentConfig(system_instruction=...)`.

Q3: [Medium] Difference between Gemini Developer API and Vertex AI?
A3: Developer API: simple API key, quick start, free tier. Vertex AI: Google Cloud project, IAM auth, enterprise controls, regional data residency, SLAs. The `google-genai` SDK supports both via client settings.

Q4: [Medium] How do you send an image or PDF?
A4: Pass `types.Part.from_bytes(data=..., mime_type=...)` in `contents` alongside text, or upload via the Files API for larger files.

Q5: [Hard] When would you pick Gemini over other providers?
A5: Very long-context or multimodal-heavy workloads (video, audio, PDFs), Google Cloud integration and compliance needs, cost-sensitive high volume with flash-tier models, or as a fallback provider. Decide with evals on your data and check latency, rate limits, and region availability.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large documents, multimodal inputs, Google Cloud stack
- Free-tier prototyping

❌ Avoid when:
- Strict data-handling rules conflict with the chosen tier (check terms; use Vertex or another provider)
- Your evals show another model is better for your task

---

## 📊 Visual Diagram
```
 your app
    |  genai.Client()
    v
 +----------- Gemini API -----------------------------+
 | models.generate_content(model, contents, config)    |
 |   -> response.text                                  |
 |   -> response.usage_metadata                        |
 |        prompt_token_count / candidates_token_count  |
 +-----------------------------------------------------+
 Developer API (API key)   or   Vertex AI (GCP credentials)

 contents = text | image | audio | video | PDF parts
```

---

## 💰 Cost Impact
- Billed per input and output token (rates vary by model; flash-tier models are typically cheap, pro-tier cost more; confirm on the pricing page). Free tier has low rate limits and different data-use terms.
- Large inputs (long video/PDF) become many tokens; check `usage_metadata` after calls, and use the count-tokens method before big requests.
- Optimise: pick the flash tier first, cap `max_output_tokens`, use context caching for repeated large documents, and use RAG when only parts of a document matter.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Gemini | Google's LLM family | Google का LLM परिवार |
| google-genai | Current Python SDK | मौजूदा Python SDK |
| system_instruction | System prompt in Gemini | Gemini में system prompt |
| usage_metadata | Token counts | Token गिनती |
| Vertex AI | Google Cloud enterprise route | Google Cloud का enterprise रास्ता |
| Multimodal | Handles text, image, audio, video | Text, image, audio, video सब समझता है |

---

## ⚡ 3-Line Summary
English: Use the `google-genai` SDK: `genai.Client().models.generate_content(model, contents, config)`. The system prompt is `system_instruction`, and the async API lives under `client.aio`. Handle empty or blocked responses and keep model names in config.
Hindi: `google-genai` SDK use करो: `genai.Client().models.generate_content(model, contents, config)`। System prompt `system_instruction` है और async API `client.aio` के नीचे है। खाली या blocked responses संभालो और model names config में रखो।

---

## ➡️ Next Topic
**040. Groq API (Fast Inference)** — very low-latency hosted open models with an OpenAI-compatible API.
