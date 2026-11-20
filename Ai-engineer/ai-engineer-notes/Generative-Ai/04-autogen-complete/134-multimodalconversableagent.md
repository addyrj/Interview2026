---

# 134. MultimodalConversableAgent
# हिंदी में: MultimodalConversableAgent — image समझने वाले agents (v0.2 बनाम v0.4)
# Framework: AutoGen
# Already Known: No

---

## 🔵 Simple Definition (2-3 lines)
`MultimodalConversableAgent` was a v0.2 agent class for vision models. It is not part of v0.4 (checked: not exported). In v0.4, any `AssistantAgent` can handle images if its model client supports vision: you send a `MultiModalMessage` whose `content` list mixes strings and `autogen_core.Image` objects.

## 🔵 सरल परिभाषा (Hindi)
`MultimodalConversableAgent` v0.2 की vision models वाली agent class थी। v0.4 में यह नहीं है (जाँचा: export नहीं होती)। v0.4 में कोई भी `AssistantAgent` image संभाल सकता है अगर उसका model client vision support करता है: आप `MultiModalMessage` भेजते हैं जिसके `content` list में strings और `autogen_core.Image` objects मिलाकर होते हैं।

---

## 🔴 Problem it Solves
Customs work is full of documents: invoices, packing lists, bills of lading, product photos. Text-only agents cannot read scans or photos. A separate OCR pipeline is brittle. Vision-capable models can read an invoice image and extract fields directly, but you need a clean way to put images in the conversation and to avoid sending images to models that cannot handle them.

## 🔴 यह क्यों बना? (Hindi)
Customs के काम में documents भरे होते हैं: invoices, packing lists, bills of lading, product photos। Text-only agents scans या photos नहीं पढ़ सकते। अलग OCR pipeline नाज़ुक होती है। Vision models invoice image सीधे पढ़कर fields निकाल सकते हैं, पर image को conversation में डालने और non-vision model को image न भेजने का साफ़ तरीका चाहिए।

---

## 🟢 How it Works

```
Step 1 -> Load an image: Image.from_file(path) / Image.from_pil(img) / Image.from_base64(b64)
Step 2 -> Build MultiModalMessage(content=['question', image], source='user')
Step 3 -> Agent's model_client must report model_info['vision'] == True
Step 4 -> await agent.run(task=multimodal_message)
Step 5 -> Model reads text + image tokens, returns text (or structured JSON)
Step 6 -> Validate extracted fields (HS code format, totals) in code
Step 7 -> Low confidence -> hand off to a human reviewer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 -> Image load करो: Image.from_file(path) / Image.from_pil(img) / Image.from_base64(b64)
Step 2 -> MultiModalMessage(content=['सवाल', image], source='user') बनाओ
Step 3 -> agent के model_client में model_info['vision'] == True होना चाहिए
Step 4 -> await agent.run(task=multimodal_message)
Step 5 -> Model text + image tokens पढ़कर text (या structured JSON) लौटाता है
Step 6 -> code में extracted fields validate करो (HS code format, totals)
Step 7 -> कम confidence हो तो human reviewer को सौंपो
```

---

## 🟡 Real World Example
**Invoice reader.** A broker uploads a scanned commercial invoice. The vision agent extracts consignee, product description and declared value. A second agent maps the description to an HS code, and a validator checks that line totals add up before anything is filed. Image input is the front door of the whole pipeline.

## 🟡 Real Example Hindi mein
**Invoice reader.** Broker स्कैन की हुई commercial invoice upload करता है। Vision agent consignee, product description और declared value निकालता है। दूसरा agent description को HS code से जोड़ता है, और filing से पहले validator जाँचता है कि line totals जुड़ते हैं। Image input पूरी pipeline का प्रवेश द्वार है।

---

## 💻 Code Example — Basic
Basic: a generated 64x64 white image stands in for an invoice; the vision flag is declared on the fake model. No real image understanding was tested: the replay client returns a scripted sentence.

```python
# Multimodal: v0.2 MultimodalConversableAgent -> v0.4 AssistantAgent + MultiModalMessage (vision-capable model required)
import asyncio                                                    # async
from PIL import Image as PILImage                                 # Pillow, to make a demo image
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.messages import MultiModalMessage          # text + image message
from autogen_core import Image                                    # AutoGen image wrapper
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

async def main() -> None:
    info = {"function_calling": False, "vision": True, "json_output": False,
            "family": "unknown", "structured_output": False}      # vision=True is mandatory, else images are rejected
    client = ReplayChatCompletionClient(["This looks like a commercial invoice."], model_info=info)
    agent = AssistantAgent("vision", model_client=client, system_message="Describe shipping documents.")
    img = Image.from_pil(PILImage.new("RGB", (64, 64), "white"))  # in real use: Image.from_file(path) / from_base64
    msg = MultiModalMessage(content=["What document is this?", img], source="user")  # list mixes str and Image
    res = await agent.run(task=msg)
    print(res.messages[-1].content)

if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 Code Example — Advanced
Advanced: base64 image in a JSON body (avoids the `python-multipart` dependency), size limit, image validation with Pillow, timeout and error mapping.

```python
# Multimodal over FastAPI: base64 image in JSON, size limit, vision check, errors
import asyncio, base64, io                                        # stdlib
from fastapi import FastAPI, HTTPException                        # web
from fastapi.testclient import TestClient                         # offline test
from PIL import Image as PILImage                                 # decode/validate image
from pydantic import BaseModel                                    # schema
from autogen_agentchat.agents import AssistantAgent               # agent
from autogen_agentchat.messages import MultiModalMessage          # message
from autogen_core import Image                                    # wrapper
from autogen_ext.models.replay import ReplayChatCompletionClient  # fake LLM

MAX_BYTES = 2_000_000                                             # protect memory + token cost (images cost tokens too)

class DocReq(BaseModel):
    question: str                                                 # what to ask about the image
    image_b64: str                                                # base64 PNG/JPEG

app = FastAPI()

def build_agent() -> AssistantAgent:
    info = {"function_calling": False, "vision": True, "json_output": False, "family": "unknown", "structured_output": False}
    return AssistantAgent("vision", ReplayChatCompletionClient(["Commercial invoice, total USD 500."], model_info=info))

@app.post("/describe")
async def describe(req: DocReq) -> dict:
    try:
        raw = base64.b64decode(req.image_b64, validate=True)      # reject malformed base64
    except Exception:
        raise HTTPException(422, "invalid base64")
    if len(raw) > MAX_BYTES:                                      # size guard
        raise HTTPException(413, "image too large")
    try:
        pil = PILImage.open(io.BytesIO(raw)); pil.load()          # verify it really is an image
    except Exception:
        raise HTTPException(422, "not an image")
    msg = MultiModalMessage(content=[req.question, Image.from_pil(pil)], source="user")
    try:
        res = await asyncio.wait_for(build_agent().run(task=msg), timeout=30)
    except Exception as exc:
        raise HTTPException(502, f"vision model error: {exc}")
    return {"answer": str(res.messages[-1].content)}

if __name__ == "__main__":
    buf = io.BytesIO(); PILImage.new("RGB", (32, 32), "white").save(buf, format="PNG")  # make a tiny PNG
    b64 = base64.b64encode(buf.getvalue()).decode()
    print(TestClient(app).post("/describe", json={"question": "What is this?", "image_b64": b64}).json())
```

**Verification status:** verified against autogen-agentchat 0.7.5, autogen-core 0.7.5, autogen-ext 0.7.5, fastapi 0.163.0, pydantic 2.14.3 (Python 3.13). Both examples were executed offline with `ReplayChatCompletionClient` (scripted replies, no API key, no network). They were NOT run against a real LLM: swap in `OpenAIChatCompletionClient(model=...)` from `autogen_ext.models.openai` (needs an API key) for production. Token numbers printed offline are estimates by the replay client, not real billing.

---

## 🔗 Framework Comparison
| Feature | LangGraph | CrewAI | OpenAI SDK | AutoGen |
|---------|-----------|--------|------------|---------|
| Image input | HumanMessage with image content blocks | Multimodal flag / tools | Image inputs in message items | MultiModalMessage + autogen_core.Image |
| Capability check | Provider-specific | Provider-specific | Model dependent | model_info['vision'] enforced |
| Dedicated class | No | No | No | v0.2 had one; v0.4 does not |
| Document OCR | Tool/loader | Tool | File search / vision | Vision model or your OCR tool |
| Cost driver | Image tokens | Image tokens | Image tokens | Image tokens (provider rules) |

---

## ⚠️ Common Mistakes
❌ Mistake: Looking for `MultimodalConversableAgent` in v0.4 or sending images to a text-only model.
✅ Correct: Use `AssistantAgent` + a model client with `vision=True` and a `MultiModalMessage`.

❌ Mistake: Accepting arbitrary uploads: huge files, non-images, decompression bombs.
✅ Correct: Limit size, validate with Pillow, resize before sending.

❌ Mistake: Trusting extracted numbers blindly.
✅ Correct: Cross-check with code (sums, formats) and keep a human fallback.

❌ Mistake: Sending full-resolution photos every turn: each turn re-sends the image tokens in context.
✅ Correct: Downscale, crop to the region needed, and drop the image from later context once extracted.

---

## 🧠 Tricky Interview Question
Your invoice agent works in dev but costs 10x more in prod and sometimes mixes up fields. Why?

Answer: Cost: images are tokenised and re-sent with the conversation history on every later turn; high-resolution pages from users cost far more than your dev samples. Provider billing for images varies by size/detail setting (verify current rules). Fix by resizing, extracting once into structured JSON, and continuing the conversation with the JSON only. Accuracy: scans with rotated or low-contrast text, multi-page documents and handwriting break vision models; add pre-processing (deskew, contrast), page splitting, schema-constrained output, arithmetic validation and a confidence-based human review path. Evaluate on a labelled set of real production documents, not clean samples.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Does v0.4 have a MultimodalConversableAgent?
A1: No. Use an `AssistantAgent` with a vision-capable model client and send a `MultiModalMessage`.

Q2: [Medium] How do you create an `Image` object?
A2: `Image.from_file(Path)`, `Image.from_pil(pil_image)`, `Image.from_base64(str)` from `autogen_core`.

Q3: [Hard] What happens if the model has no vision support?
A3: The model client rejects image input; with the replay client it must declare `vision: True` in `model_info`. Always check `model_info` for custom clients.

Q4: [Hard] How do you control image cost?
A4: Resize, crop, extract once to JSON, remove the image from later context via a bounded `model_context`, and use cheaper models for easy documents.

Q5: [System Design] Design a document-intake pipeline for 50k invoices per day.
A5: Queue-based workers; pre-process (deskew, resize); vision agent extracts to a pydantic schema; code validators (sums, HS format); low-confidence or failed validation to a human review queue; store extracted JSON, not images, in later agent contexts; per-document cost and accuracy metrics; retries with backoff; PII redaction and retention policy.

---

## 💰 Cost Impact
Image tokens depend on image size and provider rules, so do not assume a fixed number; check the provider's current documentation (verify). An image is part of the prompt, so it is billed on every call that includes it in context. Formula: `call_cost = (text_tokens + image_tokens + history_tokens) * in_price + out_tokens * out_price`. Savings: downscale to the minimum legible size, send once, keep only the extracted structured result in later turns, and route simple documents to a cheaper model. Prices: approximate, from public pricing at time of writing -- verify.

---

## 🔷 When to Use
✅ Use when:
- Invoices, packing lists, screenshots, product photos.
- Extraction that is hard with OCR + rules.
- As the first step of a pipeline followed by text-only agents.

❌ Avoid when:
- Text already available digitally: parse the text directly.
- High-precision numeric extraction without validation.
- Models without vision support.

---

## 📊 Visual Diagram
```
 upload (PNG/JPG) --> size + Pillow validation --> resize
                                                     |
                     MultiModalMessage(["extract fields", Image])
                                                     |
                              AssistantAgent(model_client vision=True)
                                                     |
                           JSON {consignee, description, total}
                                                     |
                  validators (sum check, HS format) --fail--> human review queue
                                                     |
                                       next agents continue with JSON only (no image)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MultiModalMessage | Message mixing text and images | text और images वाला message |
| Image | autogen_core wrapper for image data | image data का wrapper |
| vision | Model capability to read images | image पढ़ने की model क्षमता |
| model_info | Declared capabilities of a model client | model client की घोषित क्षमताएँ |
| OCR | Optical character recognition | अक्षर पहचान तकनीक |
| base64 | Text encoding of binary data | binary data का text encoding |
| image tokens | Tokens billed for an image | image के लिए गिने गए tokens |
| deskew | Straighten a tilted scan | टेढ़े scan को सीधा करना |

---

## ⚡ 3-Line Summary
English: v0.2's MultimodalConversableAgent is replaced by AssistantAgent + MultiModalMessage + a vision-capable model client.
Validate and downscale uploads, extract once to structured JSON, and verify numbers with code.
Images are billed as tokens on every call that carries them.
Hindi: v0.2 के MultimodalConversableAgent की जगह AssistantAgent + MultiModalMessage + vision वाला model client है।
Uploads validate और downscale करें, एक बार structured JSON में extract करें और संख्याएँ code से जाँचें।
Images हर उस call में tokens के रूप में बिल होती हैं जिसमें वे शामिल हों।

---

## ➡️ Next Topic
135. GroupChat -- Complete -- how many agents collaborate in v0.4 teams.

---
