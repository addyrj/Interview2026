---

# 280. DEPLOY FASTAPI TO APP SERVICE
# AWS: Elastic Beanstalk (Python) / App Runner
# Azure: Azure App Service (Linux, Python)
# हिंदी में: FastAPI को App Service पर डिप्लॉय करना

---

## 🔵 Simple Definition (2 lines)
Run a FastAPI app on App Service Linux with Gunicorn using Uvicorn workers, configured through a startup command.
हिंदी: FastAPI को Gunicorn + Uvicorn वर्कर के साथ App Service पर चलाओ, स्टार्टअप कमांड से।

---

## 🔴 Why it Exists (2 lines)
FastAPI is ASGI; App Service does not auto-detect it like Flask/Django, so you must give the right start command.

---

## 🟢 How it Works
```
requirements.txt (fastapi, uvicorn, gunicorn)
  -> zip deploy -> Oryx builds venv (pip install)
  -> startup command:
     gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 main:app
  -> App Service forwards to the port (WEBSITES_PORT=8000 if not default)
Health check path -> /health
```

---

## 💻 Code / Config Example
```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"msg": "hello from FastAPI on App Service"}
```
```text
# requirements.txt
fastapi
uvicorn
gunicorn
```
```bash
az group create -n rg-prod -l centralindia
az appservice plan create -g rg-prod -n plan-py --is-linux --sku B1
az webapp create -g rg-prod -p plan-py -n fastapi-prod-unique123 --runtime "PYTHON:3.11"

az webapp config set -g rg-prod -n fastapi-prod-unique123 \
  --startup-file "gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 main:app"
az webapp config appsettings set -g rg-prod -n fastapi-prod-unique123 \
  --settings WEBSITES_PORT=8000 SCM_DO_BUILD_DURING_DEPLOYMENT=true

zip -r app.zip main.py requirements.txt
az webapp deploy -g rg-prod -n fastapi-prod-unique123 --src-path app.zip --type zip
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Elastic Beanstalk / App Runner | App Service |
| ASGI config | Procfile | Startup command |
| Container option | App Runner / ECS | Web App for Containers (Docker) |
| Pricing | Underlying resources | Per plan hour (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: No startup command, so default app is not found.
✅ Correct: Set Gunicorn + UvicornWorker command.

❌ Mistake: Binding to 127.0.0.1.
✅ Correct: Bind 0.0.0.0 and set WEBSITES_PORT to match.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Why Gunicorn with Uvicorn workers?
A1: Gunicorn manages processes; Uvicorn workers run the ASGI app.

Q2: [Medium] How set workers?
A2: Roughly based on cores (e.g. 2*cores+1 for sync; fewer for async) tuned by load testing.

Q3: [Hard] Container vs code deploy?
A3: Container gives exact dependency parity with Docker locally and CI; code deploy is simpler. For Docker use ACR + managed identity pull.

---

## ✅ Quick Checklist
□ Startup command set
□ /health endpoint + Health check
□ Secrets via Key Vault references

---

## ⚡ 1-Line Summary
FastAPI on App Service needs Gunicorn/Uvicorn startup command | FastAPI के लिए स्टार्टअप कमांड ज़रूरी है।

## ➡️ Next: 281 (next section)

---
