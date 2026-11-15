# 171. Polly (Text to Speech)
# AWS: Amazon Polly
# Azure: Azure AI Speech (text to speech)
# हिंदी में: text को आवाज़ (audio) में बदलना

---

## 🔵 Simple Definition
Polly converts text into natural-sounding speech in many languages and voices, returning MP3/OGG/PCM audio.
हिंदी: Polly लिखे हुए text को बोलती हुई audio में बदल देता है।

---

## 🔴 Why it Exists
Voice alerts, IVR, accessibility and audio articles need speech without recording studios.

---

## 🟢 How it Works
```
text or SSML -> polly.synthesize_speech(VoiceId, Engine, OutputFormat)
 -> AudioStream -> save file / stream to client
Long text: start_speech_synthesis_task -> S3
```

---

## 💻 Code / Config Example
```python
import boto3

polly = boto3.client("polly", region_name="ap-south-1")
resp = polly.synthesize_speech(
    Text="Your order has been shipped.",
    VoiceId="Kajal",          # Indian English / Hindi voice; check supported voices & engine
    Engine="neural",
    OutputFormat="mp3",
)
with open("out.mp3", "wb") as f:
    f.write(resp["AudioStream"].read())
```
```bash
aws polly describe-voices --language-code hi-IN
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Polly | AI Speech TTS |
| Markup | SSML | SSML |
| Custom voice | Brand voice (by request) | Custom Neural Voice (gated) |
| Pricing | Per million characters, varies by engine (approximate — check current docs) | Per million characters |

---

## ⚠️ Common Mistakes
❌ Mistake: Synthesising the same text on every request.
✅ Correct: Cache audio in S3/CDN keyed by text hash.

❌ Mistake: Using a voice/engine not available in the region.
✅ Correct: Run `describe-voices` for that region.

---

## ⚫ Interview Q&A
Q1: [Easy] What is SSML?
A1: XML markup to control pauses, pitch, pronunciation.

Q2: [Medium] Standard vs neural engine?
A2: Neural sounds more natural and costs more; not every voice supports it.

Q3: [Hard] Design scalable voice notifications.
A3: Event -> SQS -> Lambda synthesises (cache by hash) -> S3 -> presigned URL or telephony integration; handle text length limits via async tasks.

---

## ✅ Quick Checklist
□ Voice+engine+region verified
□ Audio cached
□ SSML for names/numbers

---

## ⚡ 1-Line Summary
Polly turns text into speech | Polly text को बोलती आवाज़ में बदलता है।

## ➡️ Next: 172. Transcribe (Speech to Text)
