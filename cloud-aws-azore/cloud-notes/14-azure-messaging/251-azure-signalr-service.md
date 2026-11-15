---

# 251. Azure SignalR Service
# AWS: API Gateway WebSocket APIs / AWS AppSync subscriptions / IoT Core (no direct equivalent)
# Azure: Azure SignalR Service (and Web PubSub for raw WebSockets)
# हिंदी में: रियल-टाइम (chat, live updates) के लिए managed WebSocket सर्विस

---

## 🔵 Simple Definition (2 lines)
Azure SignalR Service manages thousands of persistent real-time connections so your app server does not have to.
SignalR Service लाइव कनेक्शन सँभालता है, आपका सर्वर सिर्फ़ मैसेज भेजता है।

---

## 🔴 Why it Exists (2 lines)
WebSockets are stateful and hard to scale across servers.
The service offloads connections, scaling and fallback transports (WebSocket, SSE, long polling).

---

## 🟢 How it Works
```
Browser <==WebSocket==> Azure SignalR Service <== server connections ==> ASP.NET Core app (Hub)
 1. Client calls /negotiate on your app -> gets service URL + access token
 2. Client connects directly to the service
 3. Hub sends to: all | group | user | connection
Modes: Default (app hosts hub), Serverless (Functions + REST API), Classic
Node.js/FastAPI: use Azure Web PubSub (raw WebSocket) or SignalR serverless REST
```

---

## 💻 Code / Config Example
```bash
az signalr create -g rg-demo -n sig-demo -l centralindia --sku Free_F1 --service-mode Default
az signalr key list -g rg-demo -n sig-demo --query primaryConnectionString -o tsv
```
```javascript
// Node.js with Web PubSub (WebSocket); npm i @azure/web-pubsub
const { WebPubSubServiceClient } = require("@azure/web-pubsub");
const svc = new WebPubSubServiceClient(process.env.WPS_CONNECTION_STRING, "chat");

// Give client a URL to connect to
async function token(userId) {
  return svc.getClientAccessToken({ userId, roles: ["webpubsub.joinLeaveGroup"] });
}
// Broadcast to everyone in hub
async function broadcast(text) {
  await svc.sendToAll({ text }, { contentType: "application/json" });
}
module.exports = { token, broadcast };
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Managed WebSockets | API Gateway WebSocket API | SignalR Service / Web PubSub |
| GraphQL realtime | AppSync | N/A (use SignalR) |
| Fallbacks | Self-managed | SignalR handles SSE/long polling |
| Pricing | Per message + connection minutes (approximate - check current docs) | Per unit/day + message quota (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Running your own Socket.IO with sticky sessions on multiple VPS nodes.
✅ Correct: Use managed service or Redis adapter; avoid sticky-session fragility.

❌ Mistake: Exposing the connection string to clients.
✅ Correct: Issue short-lived client access tokens from the server.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is SignalR?
A1: A library/service for real-time server-to-client push using WebSocket with fallbacks.

Q2: [Medium] SignalR Service vs Web PubSub?
A2: SignalR Service targets the SignalR protocol/SDKs; Web PubSub is protocol-agnostic raw WebSocket pub/sub, good for Node and Python.

Q3: [Hard] How does it scale?
A3: Service holds client connections; units add connection capacity; app servers only keep a few server connections and stay stateless.

---

## ✅ Quick Checklist
□ Negotiate endpoint issues scoped tokens
□ Groups used for rooms
□ Unit count sized for peak connections

---

## ⚡ 1-Line Summary
SignalR Service offloads real-time connection scaling | SignalR Service रियल-टाइम कनेक्शन की scaling खुद सँभालता है।

## ➡️ Next: 252. Messaging Pattern Comparison

---
