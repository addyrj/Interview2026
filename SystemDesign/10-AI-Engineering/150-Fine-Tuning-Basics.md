# 150. Fine Tuning Basics
# हिंदी में: Fine-Tuning — पहले से trained model को अपने उदाहरणों पर थोड़ा और train करना ताकि वो किसी ख़ास काम, style या format में बेहतर हो (जैसे support के जवाब, ticket classification, हिंदी लहजा) — SFT, LoRA/QLoRA, DPO, डेटा की तैयारी, और कब fine-tune करना सही है (और कब RAG या prompt काफ़ी है)

---

## 🔵 Simple Definition (English)
**Fine-tuning** continues training a **pretrained model** on your **task-specific examples**, so its weights adapt to a desired behaviour: output format, tone, domain language, a narrow skill like classification or extraction, or tool-calling style.
Main approaches:
- **Supervised fine-tuning (SFT)**: train on prompt → ideal-response pairs (chat-format JSONL).
- **Parameter-efficient fine-tuning (PEFT)**: instead of updating all weights, train small **adapters**:
  - **LoRA** (low-rank matrices added to layers)
  - **QLoRA** (LoRA on a 4-bit-quantized base model), which can fit a 7–8B model on a single GPU
- **Preference tuning**: **DPO** (direct preference optimization), RLHF/RLAIF, KTO/ORPO. The model learns from chosen-vs-rejected responses: more helpful, safer, on-brand.
- **Distillation**: train a smaller model on a stronger model's outputs (check provider terms) to cut cost and latency.
- **Continued pretraining**: further training on large domain or language corpora (e.g., Hindi text) before SFT.
- **Embedding/reranker fine-tuning**: improve retrieval on your domain.
Options: hosted fine-tuning APIs (OpenAI, cloud platforms such as Amazon Bedrock and Vertex AI for supported models), or open-source models (Llama, Mistral, Qwen, Gemma, Indic models) with Hugging Face **TRL + PEFT**, Unsloth or Axolotl, served via **vLLM** (including multi-LoRA serving).
**Key principle**: use fine-tuning for **behaviour and skills**, and RAG for **knowledge that changes**.

## 🔵 सरल परिभाषा (Hindi)
Fine-tuning = पहले से trained model को अपने काम के उदाहरणों पर आगे train करना ताकि उसके weights मनचाहे व्यवहार की ओर ढलें — format, लहजा, domain की भाषा, classification/extraction जैसा सीमित कौशल, tool-calling का तरीका।
तरीके: SFT (prompt → सही जवाब जोड़ियाँ), PEFT — सारे weights की जगह छोटे adapters (LoRA; QLoRA = 4-bit base + LoRA, एक GPU पर 7–8B model), preference tuning (DPO, RLHF — चुना बनाम ठुकराया जवाब), distillation (बड़े model के जवाबों से छोटा model — शर्तें जाँचो), continued pretraining (हिंदी जैसे बड़े corpus पर), embedding/reranker fine-tuning। Hosted APIs या open-source (TRL + PEFT, Unsloth) + vLLM serving। मूल नियम: व्यवहार/कौशल के लिए fine-tuning, बदलते ज्ञान के लिए RAG।

---

## 🔴 Problem it Solves
Prompting and RAG can't always deliver what production needs:
- **Consistency at scale**: a 3,000-token prompt with 20 examples still drifts in format 3% of the time. A fine-tuned model follows the format reliably with a short prompt.
- **Cost and latency**: running a large model for 50 million ticket classifications a month is expensive. A fine-tuned small model (or distilled model) can match quality for that narrow task at a fraction of the cost and latency.
- **Domain language and style**: legal or medical phrasing, a brand voice, or natural Hindi or Hinglish replies that generic models handle awkwardly.
- **Low-resource languages**: Indic languages with fewer pretraining tokens benefit from continued pretraining and instruction tuning.
- **On-prem or data-residency** needs: fine-tuned open models running inside your VPC in India.
But fine-tuning is often **misused** to inject facts (which go stale and can't be cited), when RAG is the right tool, and it brings data, training, evaluation and maintenance costs.

## 🔴 यह क्यों बना? (Hindi)
Prompt और RAG हमेशा production की ज़रूरत पूरी नहीं करते: 3,000 tokens के prompt और 20 उदाहरणों के बाद भी 3% बार format बिगड़े — fine-tuned model छोटे prompt से भी पक्का format; महीने के 5 करोड़ tickets classify करने के लिए बड़ा model महँगा — fine-tuned/distilled छोटा model उसी काम में कम ख़र्च/देर में बराबर; कानूनी/चिकित्सा भाषा, brand की आवाज़, स्वाभाविक हिंदी/Hinglish; कम संसाधन वाली भारतीय भाषाएँ; VPC/भारत में चलने वाले models।
पर अक्सर ग़लत इस्तेमाल — तथ्य "डालने" के लिए (पुराने हो जाते हैं, citation नहीं), जहाँ RAG सही है; और डेटा, training, evaluation, रख-रखाव का ख़र्च भी।

---

## 🟢 How it Works — Step by Step

### Decision ladder (do this in order)

```
1. Better prompt (clear instructions, examples, structured output)  → cheapest; re-run evals
2. RAG / tools for knowledge & live data                              → facts stay fresh, citable
3. Model routing (bigger model for hard cases)                        → quality without training
4. Fine-tune when evals show a persistent gap in: format/style consistency, narrow-task accuracy,
   latency/cost at volume, domain/language fluency — AND you have (or can create) quality data
Fine-tuning ≠ knowledge injection: facts learned in weights can't be updated quickly or cited
```

### Data preparation (the most important part)

```
Format (chat SFT JSONL):
{"messages": [{"role": "system", "content": "You are QuickBite support…"},
              {"role": "user", "content": "Raita missing tha, kya karoon?"},
              {"role": "assistant", "content": "Sorry about that! I've noted the missing raita…"}]}
Quality > quantity: start with ~200–2,000 high-quality examples for a narrow task; more for broad behaviour
Sources: expert-written responses, curated production conversations (anonymized, PII removed),
         corrected model outputs, synthetic data from a stronger model (reviewed; check terms of use)
Coverage: edge cases, refusals ("I can't share OTP"), multilingual (Hindi/Hinglish/English), escalations
Splits: train / validation / held-out test (never train on eval cases); dedupe near-duplicates
Preference data (DPO): {prompt, chosen, rejected} pairs from human rankings or policy-guided judging
```

### LoRA / QLoRA intuition

```
Full fine-tune: update all W (billions of params) → huge GPU memory, a full model copy per variant
LoRA: keep W frozen; learn ΔW = B·A where A (r×d), B (d×r), r small (8–64) → ~0.1–1% trainable params
      → adapters are small (MBs), swap per task/tenant; serve many LoRAs on one base (vLLM multi-LoRA)
QLoRA: base weights quantized to 4-bit (NF4) + LoRA adapters in higher precision → 7–8B models on a
      single 24–48 GB GPU
Key hyperparameters: epochs (1–3; more → overfit), learning rate, LoRA r & alpha, target modules,
      max sequence length, batch size
```

### Training → evaluation → deployment

```
Train (hosted API or TRL/Unsloth on GPUs) → evaluate vs baseline on held-out set:
  task metrics (accuracy/F1, format validity, rubric scores), plus REGRESSION checks on general ability,
  safety (refusals still correct?), multilingual quality, latency/cost
Deploy: hosted fine-tuned model endpoint, or open model + adapter on vLLM/TGI (GPU autoscaling)
Monitor: drift (new intents/policies), feedback; retrain periodically with fresh curated data
Version everything: dataset version, base model, hyperparameters, adapter version, eval report
```

### Risks

```
Overfitting & catastrophic forgetting (loses general skills) → small LR, few epochs, mixed general data
Safety degradation (fine-tuning can weaken refusals) → include safety examples, re-run red-team suites
Data leakage/memorization of PII → scrub data, don't train on secrets
Maintenance: base model upgrades require re-tuning & re-evaluation
Licensing/terms: open-model licences; provider rules on training with model outputs
```

## 🟢 कैसे काम करता है? (Hindi)
1. सीढ़ी: पहले बेहतर prompt → फिर ज्ञान/live डेटा के लिए RAG/tools → कठिन cases के लिए बड़ा model → fine-tune तभी जब evals में format/style, सीमित काम की सटीकता, भारी मात्रा पर ख़र्च/देर या भाषा में लगातार कमी दिखे और अच्छा डेटा हो; fine-tuning से तथ्य "डालना" ग़लत — बदल नहीं सकते, cite नहीं कर सकते।
2. डेटा सबसे अहम: chat JSONL (system/user/assistant); संकीर्ण काम के लिए 200–2,000 अच्छे उदाहरण; स्रोत — विशेषज्ञ जवाब, anonymized असली बातचीत, सुधारे हुए outputs, जाँचा synthetic; edge cases, मना करने वाले, हिंदी/Hinglish, escalation; train/validation/test अलग, duplicates हटाओ; DPO के लिए chosen/rejected जोड़ियाँ।
3. LoRA: असली weights जमे रहते हैं, छोटे matrices (rank 8–64) सीखते हैं — ~0.1–1% parameters, adapters MBs के, हर काम/tenant का अलग adapter, एक base पर कई LoRAs (vLLM); QLoRA: base 4-bit + LoRA — 7–8B model एक 24–48 GB GPU पर; मुख्य settings — epochs (1–3), learning rate, r/alpha।
4. Train → held-out set पर baseline से तुलना (काम के नाप + सामान्य क्षमता, safety, भाषा, latency/ख़र्च में गिरावट तो नहीं) → deploy (hosted endpoint या vLLM पर adapter) → drift पर निगरानी और समय-समय पर retrain; dataset, base model, settings, adapter, eval report — सबके versions।
5. जोखिम: overfitting और पुराना कौशल भूलना, safety कमज़ोर होना (safety उदाहरण + red-team दोबारा), PII याद रह जाना (डेटा साफ़ करो), base model बदलने पर फिर tuning, licences और provider की शर्तें।

---

## 🟡 Real World Example

**OpenAI fine-tuning (GPT-3.5 Turbo, 2023, and later models)** — OpenAI opened fine-tuning for chat models, reporting that fine-tuned smaller models can match or beat larger base models on narrow tasks with shorter prompts. Businesses use it for consistent formatting and tone.

**Claude fine-tuning via Amazon Bedrock (2024)** — Anthropic and AWS offered fine-tuning for Claude 3 Haiku in Amazon Bedrock, so enterprises can customize a fast model for domain tasks within their AWS environment.

**Indic models: Sarvam AI's OpenHathi (2023) and AI4Bharat's Airavata (2024)** — OpenHathi extended Llama 2 with Hindi through tokenizer extension and continued pretraining. Airavata instruction-tuned a model for Hindi. These are Indian examples of continued pretraining plus SFT for low-resource languages.

**LoRA/QLoRA papers (2021, 2023)** — LoRA (Microsoft) and QLoRA (University of Washington) made fine-tuning large open models feasible on modest hardware. QLoRA showed a 65B model could be fine-tuned on a single 48 GB GPU, which democratized customization.

## 🟡 Real Example Hindi में
OpenAI ने 2023 में chat models की fine-tuning खोली — छोटे fine-tuned models संकीर्ण कामों में छोटे prompt के साथ बड़े models के बराबर या बेहतर; 2024 में Amazon Bedrock पर Claude 3 Haiku की fine-tuning आई — कंपनियाँ अपने AWS में तेज़ model को ढाल सकें।
भारत में Sarvam AI का OpenHathi (2023) — Llama 2 में हिंदी tokenizer और continued pretraining; AI4Bharat का Airavata (2024) — हिंदी के लिए instruction tuning; LoRA (2021) और QLoRA (2023) ने साधारण hardware पर fine-tuning संभव बनाया — QLoRA में 65B model एक 48 GB GPU पर।

---

## 🟠 My Stack Example

### Build an SFT dataset from curated support conversations (Python)
```python
def to_example(conv) -> dict:
    return {"messages": [
        {"role": "system", "content": "You are QuickBite support. Be brief, polite, reply in the user's language, follow policy."},
        *[{"role": m.role, "content": redact_pii(m.text)} for m in conv.turns if m.role in ("user", "assistant")]]}

convs = [c for c in load_conversations(since="2026-06-01") if c.csat >= 4 and c.qa_reviewed and not c.has_sensitive_data]
random.seed(7); random.shuffle(convs)
n = len(convs); train, val = convs[: int(n * 0.9)], convs[int(n * 0.9):]
write_jsonl("ft/support_train_v3.jsonl", [to_example(c) for c in train])
write_jsonl("ft/support_val_v3.jsonl", [to_example(c) for c in val])
# Held-out TEST set (separately curated) lives in evals/ and is never used for training
```

### Open model + QLoRA with Hugging Face TRL/PEFT (classification/extraction or style)
```python
# pip install trl peft transformers datasets bitsandbytes accelerate
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig
import torch

base = "an-open-instruct-model-7b"                       # e.g., a Llama/Qwen/Gemma or Indic instruct model (check licence)
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
model = AutoModelForCausalLM.from_pretrained(base, quantization_config=bnb, device_map="auto")
tok = AutoTokenizer.from_pretrained(base)

ds = load_dataset("json", data_files={"train": "ft/support_train_v3.jsonl", "validation": "ft/support_val_v3.jsonl"})
trainer = SFTTrainer(
    model=model, processing_class=tok, train_dataset=ds["train"], eval_dataset=ds["validation"],
    peft_config=LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, target_modules="all-linear", task_type="CAUSAL_LM"),
    args=SFTConfig(output_dir="out/support-lora-v3", num_train_epochs=2, learning_rate=2e-4,
                   per_device_train_batch_size=4, gradient_accumulation_steps=4, max_length=2048,
                   eval_strategy="steps", eval_steps=200, logging_steps=20, bf16=True),
)
trainer.train()
trainer.save_model("out/support-lora-v3")                 # small adapter (MBs)
```

### Serve base + multiple LoRA adapters with vLLM (OpenAI-compatible API)
```bash
vllm serve an-open-instruct-model-7b --enable-lora \
  --lora-modules support-v3=out/support-lora-v3 ticket-classifier-v2=out/ticket-lora-v2 \
  --max-loras 4 --gpu-memory-utilization 0.9
# Clients call model="support-v3" or "ticket-classifier-v2" on the same GPU pool
```

### Hosted fine-tuning API (OpenAI example)
```python
from openai import OpenAI
oai = OpenAI()
f = oai.files.create(file=open("ft/ticket_train.jsonl", "rb"), purpose="fine-tune")
job = oai.fine_tuning.jobs.create(training_file=f.id, model=os.environ["OPENAI_FT_BASE_MODEL"],
                                  suffix="ticket-classifier-v2")
# poll job → fine_tuned_model id → evaluate on held-out set before switching traffic
```

### Evaluate fine-tuned vs baseline (task + regression + safety)
```python
report = {
  "task_accuracy":  {m: accuracy(m, "evals/tickets_test.jsonl") for m in ["base+prompt", "ft-v2"]},
  "format_valid":   {m: format_validity(m, "evals/tickets_test.jsonl") for m in ["base+prompt", "ft-v2"]},
  "safety_refusals":{m: refusal_correctness(m, "redteam/support_v4.jsonl") for m in ["base+prompt", "ft-v2"]},
  "hindi_quality":  {m: judge_language(m, "evals/hindi_replies.jsonl") for m in ["base+prompt", "ft-v2"]},
  "p95_latency_ms": {m: latency_p95(m) for m in ["base+prompt", "ft-v2"]},
  "cost_per_1k":    {m: cost_per_1k(m) for m in ["base+prompt", "ft-v2"]},
}
# Ship only if task gains are real AND safety/general metrics don't regress
```

---

## ⚫ Interview Questions + Answers

**Q1: When should you fine-tune instead of using prompting or RAG?**
A1: Fine-tune when evals show a persistent gap that better prompts, examples, RAG or model routing can't close, and you have quality data. Typical cases are strict format or style consistency, high-volume narrow tasks (classification, extraction) where a smaller fine-tuned model cuts cost and latency, domain or language fluency (brand voice, Hindi or Hinglish replies, specialized jargon), and on-prem deployment of open models. Use RAG for knowledge that changes or must be cited. Fine-tuning isn't a good way to keep facts current.

**Q2: What are LoRA and QLoRA?**
A2: LoRA (Low-Rank Adaptation) freezes the pretrained weights and trains small low-rank matrices added to selected layers, so only a tiny fraction of parameters is learned. Training is cheaper, adapters are small, and many adapters can be swapped or served on one base model. QLoRA additionally loads the base model in 4-bit quantized form while training LoRA adapters in higher precision, drastically reducing GPU memory so large models can be fine-tuned on a single GPU with little quality loss.

**Q3: How do you prepare data for fine-tuning?**
A3: Define the target behaviour and collect high-quality examples in the model's chat format: expert-written responses, curated and anonymized production conversations, and corrected or reviewed synthetic data. Cover edge cases, refusals, escalations and all languages you serve, and remove PII and secrets. Dedupe, balance classes or intents, and split into train, validation and a separately curated held-out test set never used for training. For preference tuning, gather chosen-vs-rejected pairs. Version datasets and document sources.

**Q4: What can go wrong with fine-tuning?**
A4: Overfitting to the training set and catastrophic forgetting of general abilities, degraded safety behaviour (weaker refusals), memorization of sensitive data present in training examples, learning bad habits from noisy data, and maintenance costs when the base model is upgraded or policies change (retrain and re-evaluate). Also licensing or provider-terms issues, and false confidence if evaluation reuses training-like data. Mitigate with clean, diverse data, few epochs and a modest learning rate, a held-out eval plus regression and safety suites, and versioned pipelines.

**Q5: What's the difference between SFT and DPO?**
A5: Supervised fine-tuning trains the model to imitate target responses for given prompts (maximum likelihood on demonstrations), teaching format, style and task behaviour. Direct Preference Optimization trains on pairs of preferred and rejected responses for the same prompt, increasing the likelihood of preferred outputs relative to rejected ones without a separate reward model or RL loop, which shapes qualities like helpfulness, tone and safety that are easier to compare than to demonstrate. They're often combined: SFT first, then DPO.

---

## 🔷 Trade-offs
✅ Fine-tuning: consistent behaviour, shorter prompts, smaller/faster models — ❌ data & training cost, maintenance, risk of regressions.
✅ LoRA adapters: cheap, swappable, multi-tenant serving — ❌ slightly below full fine-tune quality in some cases.
✅ Hosted fine-tuning: no GPU ops — ❌ limited model choices, vendor lock-in, data leaves your environment.
✅ Open models + self-hosting: control, residency — ❌ GPU infra & MLOps burden.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fine-tuning | Further training on task data | काम के डेटा पर आगे training |
| SFT | Supervised fine-tuning on demos | उदाहरणों से सिखाना |
| PEFT | Parameter-efficient fine-tuning | कम parameters से tuning |
| LoRA | Low-rank adapter training | छोटे adapter |
| QLoRA | LoRA on 4-bit quantized base | 4-bit base पर LoRA |
| DPO | Preference-based tuning | पसंद के आधार पर tuning |
| Distillation | Small model learns from big | बड़े से छोटे को सिखाना |
| Continued pretraining | Extra pretraining on domain corpus | domain डेटा पर और pretraining |
| Catastrophic forgetting | Losing general skills | पुराना कौशल भूलना |
| Adapter | Small add-on weights | जोड़ने वाले छोटे weights |

---

## ⚡ 3-Line Summary
**English:**
1. Fine-tune for behaviour/skills (format, tone, narrow tasks, language, cost/latency via smaller models) — use RAG for changing knowledge.
2. Data quality is everything: curated, anonymized, diverse (incl. Hindi/Hinglish, refusals), split with a held-out test; SFT then optionally DPO; LoRA/QLoRA for efficiency.
3. Evaluate vs baseline on task + regression + safety; version datasets/adapters; serve via hosted endpoints or vLLM multi-LoRA; retrain as policies drift.

**Hindi:**
1. व्यवहार/कौशल के लिए fine-tune (format, लहजा, संकीर्ण काम, भाषा, छोटे model से कम ख़र्च) — बदलते ज्ञान के लिए RAG।
2. डेटा सबसे अहम: साफ़, anonymized, विविध, अलग test set; पहले SFT फिर DPO; कुशलता के लिए LoRA/QLoRA।
3. Baseline से तुलना (काम + गिरावट + safety); versions रखो; hosted या vLLM पर serve; नीति बदले तो retrain।

---

## ➡️ Next Topic Suggestion
**151. AI System Design at Scale** — Now combine everything (APIs, RAG, tools, agents, memory, caching, guardrails, evals and observability) into a production AI system for millions of users, with estimation, architecture and cost.
