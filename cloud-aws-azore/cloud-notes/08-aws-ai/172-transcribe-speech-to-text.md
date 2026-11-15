# 172. Transcribe (Speech to Text)
# AWS: Amazon Transcribe
# Azure: Azure AI Speech (speech to text)
# हिंदी में: audio/call को text में बदलना

---

## 🔵 Simple Definition
Transcribe converts speech in audio/video files or live streams into text with timestamps and optional speaker labels.
हिंदी: Transcribe audio या call recording को text में बदल देता है।

---

## 🔴 Why it Exists
Call-centre recordings, meetings and videos are unsearchable until transcribed.

---

## 🟢 How it Works
```
audio in S3 -> start_transcription_job (language or IdentifyLanguage)
 -> status IN_PROGRESS -> COMPLETED
 -> JSON transcript at TranscriptFileUri / OutputBucketName
Live: streaming transcription over WebSocket/HTTP2
```

---

## 💻 Code / Config Example
```python
import boto3, time

t = boto3.client("transcribe", region_name="ap-south-1")
job = "call-2024-001"
t.start_transcription_job(
    TranscriptionJobName=job,
    Media={"MediaFileUri": "s3://my-audio/call.mp3"},
    MediaFormat="mp3",
    LanguageCode="hi-IN",
    OutputBucketName="my-transcripts",
    Settings={"ShowSpeakerLabels": True, "MaxSpeakerLabels": 2},
)
while True:
    j = t.get_transcription_job(TranscriptionJobName=job)["TranscriptionJob"]
    if j["TranscriptionJobStatus"] in ("COMPLETED", "FAILED"):
        break
    time.sleep(10)
print(j["TranscriptionJobStatus"])
```
In production use an EventBridge rule on job state change instead of polling.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Transcribe | AI Speech STT |
| Batch | Transcription jobs | Batch transcription |
| Real-time | Streaming | Real-time SDK/WebSocket |
| Pricing | Per second of audio (approximate — check current docs) | Per audio hour |

---

## ⚠️ Common Mistakes
❌ Mistake: Reusing a job name (must be unique per account/region).
✅ Correct: Include timestamp or UUID.

❌ Mistake: Wrong LanguageCode on mixed Hindi-English audio.
✅ Correct: Use language identification or multi-language options where supported; test samples.

---

## ⚫ Interview Q&A
Q1: [Easy] Batch vs streaming?
A1: Batch handles stored files; streaming gives live partial results.

Q2: [Medium] How to improve accuracy for product names?
A2: Custom vocabulary or custom language model.

Q3: [Hard] Pipeline for call analytics.
A3: S3 upload -> Transcribe job (speaker labels, PII redaction) -> EventBridge -> Lambda -> Comprehend sentiment -> store in OpenSearch/DB.

---

## ✅ Quick Checklist
□ Unique job names
□ Event-driven completion
□ PII redaction if needed

---

## ⚡ 1-Line Summary
Transcribe turns audio into searchable text | Transcribe audio को searchable text बनाता है।

## ➡️ Next: 173. Translate
