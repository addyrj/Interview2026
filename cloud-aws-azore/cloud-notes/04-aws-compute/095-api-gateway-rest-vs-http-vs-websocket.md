---

# 95. API Gateway REST vs HTTP vs WebSocket
# AWS: API Gateway REST API / HTTP API / WebSocket API
# Azure: APIM (REST) + Azure Web PubSub / SignalR Service (real-time)
# हिंदी में: REST बनाम HTTP बनाम WebSocket API

---

## 🔵 Simple Definition (2 lines)
API Gateway has three flavours: REST (feature-rich), HTTP (cheaper, simpler, faster) and WebSocket (two-way real-time).
हिंदी: API Gateway के तीन प्रकार हैं: REST (ज़्यादा फ़ीचर), HTTP (सस्ता और सरल) और WebSocket (दोतरफ़ा रीयल-टाइम)।

---

## 🔴 Why it Exists (2 lines)
One size does not fit all: simple Lambda proxies do not need the full REST feature set, and chat/live apps need persistent connections.

---

## 🟢 How it Works
```
REST API  : API keys, usage plans, request validation, mapping templates,
            WAF, caching, private APIs, edge-optimized endpoints
HTTP API  : routes -> Lambda/HTTP/VPC Link, JWT authorizer, CORS built-in,
            cheaper (~ 70% less, approximate), lower latency
WebSocket : $connect / $disconnect / $default / custom routes
            server pushes via @connections POST URL (connectionId)
```

---

## 💻 Code / Config Example
```javascript
// WebSocket $default route handler: echo to the sender (AWS SDK v3, Node.js 20)
import { ApiGatewayManagementApiClient, PostToConnectionCommand }
  from "@aws-sdk/client-apigatewaymanagementapi";

export const handler = async (event) => {
  const { domainName, stage, connectionId } = event.requestContext;
  const client = new ApiGatewayManagementApiClient({
    endpoint: `https://${domainName}/${stage}`,
  });
  await client.send(new PostToConnectionCommand({
    ConnectionId: connectionId,
    Data: Buffer.from(JSON.stringify({ echo: event.body })),
  }));
  return { statusCode: 200 };
};
```
```bash
# Create an HTTP API quick (AWS CLI v2; needs credentials, not run here)
aws apigatewayv2 create-api --name demo --protocol-type HTTP \
  --target arn:aws:lambda:ap-south-1:123456789012:function:hello
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | REST API | HTTP API | WebSocket |
|---------|----------|----------|-----------|
| Use | Full-featured | Simple, cheap | Real-time chat/live |
| Auth | IAM, Cognito, Lambda, API keys | IAM, JWT, Lambda | IAM, Lambda authorizer |
| Price (approx.) | highest | ~lowest | per message + connection minutes |
| Azure equivalent | APIM | APIM | SignalR / Web PubSub |

Pricing: approximate — check current docs.

---

## ⚠️ Common Mistakes
❌ Mistake: Choosing REST API by default.
✅ Correct: Use HTTP API unless you need API keys/usage plans, WAF, request validation or caching.

❌ Mistake: Storing connectionIds only in memory.
✅ Correct: Store in DynamoDB; remove on $disconnect or 410 Gone.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Cheapest option for a Lambda proxy?
A1: HTTP API.

Q2: [Medium] Which features does only REST API have?
A2: API keys + usage plans, request/response mapping, request validation, caching, WAF integration, private endpoints (as of my knowledge; verify docs).

Q3: [Hard] Design live notifications for 10k users.
A3: WebSocket API with connections table in DynamoDB; backend publishes via PostToConnection (or use SNS/EventBridge fan-out Lambda); handle stale connections; consider IoT Core / AppSync for scale.

---

## ✅ Quick Checklist
□ Need API keys/WAF? Else HTTP API
□ WebSocket connection table with TTL
□ Idle timeout and message size limits considered

---

## ⚡ 1-Line Summary
REST = features, HTTP = cheap/fast, WebSocket = real-time | REST = फ़ीचर, HTTP = सस्ता, WebSocket = रीयल-टाइम।

## ➡️ Next: API Gateway Stages

---
