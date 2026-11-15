---

# 250. Azure Notification Hubs
# AWS: Amazon SNS Mobile Push (or Amazon Pinpoint / End User Messaging)
# Azure: Azure Notification Hubs
# हिंदी में: मोबाइल ऐप्स को लाखों push notification एक साथ भेजने की सर्विस

---

## 🔵 Simple Definition (2 lines)
Notification Hubs sends push notifications to iOS, Android and Windows devices through one API, hiding APNs/FCM differences.
यह एक ही API से Android और iOS दोनों को push notification भेज देता है।

---

## 🔴 Why it Exists (2 lines)
Each platform (APNs, FCM) has its own protocol and token handling.
Managing millions of device tokens and fan-out yourself is hard.

---

## 🟢 How it Works
```
Backend (Node/FastAPI) -> Notification Hub (namespace)
                              |-- APNs (iOS)
                              |-- FCM  (Android)
Device registers: installation {installationId, platform, pushChannel(token), tags}
Send: broadcast | tag expression ("premium && india") | single installation
```

---

## 💻 Code / Config Example
```javascript
// npm i @azure/notification-hubs
const { createClientContext, sendNotification, createFcmV1Notification } = require("@azure/notification-hubs");

const ctx = createClientContext(process.env.NH_CONNECTION_STRING, process.env.NH_HUB_NAME);

async function notifyPremium() {
  const msg = createFcmV1Notification({
    body: { message: { notification: { title: "Order shipped", body: "Order #42 is on the way" } } },
  });
  // send only to devices tagged "premium"
  await sendNotification(ctx, msg, { tagExpression: "premium" });
}
notifyPremium().catch(console.error);
```
```bash
az notification-hub namespace create -g rg-demo -n nh-demo-ns -l centralindia --sku Free
az notification-hub create -g rg-demo --namespace-name nh-demo-ns -n myhub -l centralindia
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | SNS mobile push / Pinpoint | Notification Hubs |
| Targeting | Topics, endpoints | Tags, tag expressions, templates |
| Platforms | APNs, FCM | APNs, FCM, WNS, Baidu |
| Pricing | Per push (approximate - check current docs) | Free/Basic/Standard tiers (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Storing raw device tokens only in your DB and never refreshing.
✅ Correct: Use installations and re-register on app start; tokens rotate.

❌ Mistake: Using the legacy FCM API.
✅ Correct: Use FCM v1 credentials (legacy FCM was shut down by Google).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does it abstract?
A1: Platform notification services (APNs, FCM) behind one API.

Q2: [Medium] Tags vs templates?
A2: Tags target device groups; templates let each device define its payload shape so backend sends one generic message.

Q3: [Hard] Scale and reliability?
A3: Fan-out is managed, but delivery is best-effort (PNS dependent); keep business-critical state in-app, not only push.

---

## ✅ Quick Checklist
□ APNs/FCM credentials configured
□ Installations with tags, refreshed on launch
□ Fallback for non-delivery

---

## ⚡ 1-Line Summary
Notification Hubs fans out push notifications to all mobile platforms | Notification Hubs सभी मोबाइल प्लेटफ़ॉर्म पर push भेजता है।

## ➡️ Next: 251. Azure SignalR Service

---
