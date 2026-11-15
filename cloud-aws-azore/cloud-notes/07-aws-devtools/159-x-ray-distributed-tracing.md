# 159. X-Ray - Distributed Tracing
# AWS: AWS X-Ray
# Azure: Application Insights (distributed tracing, Application Map)
# हिंदी में: X-Ray - एक रिक्वेस्ट कई सर्विसेज़ में कहाँ धीमी हुई, यह ट्रेस करना

---

## 🔵 Simple Definition
X-Ray records traces: a request's path across services with timing per segment/subsegment, and draws a service map highlighting errors and latency.
हिंदी: यह दिखाता है कि एक रिक्वेस्ट किन सर्विसेज़ से गुज़री और कहाँ कितना समय लगा।

## 🔴 Why it Exists
In microservices, logs alone cannot show which hop was slow.

## 🟢 How it Works
```
Client -> API GW -> Node API -> DynamoDB / other service
Each hop adds segment; trace header X-Amzn-Trace-Id propagates
SDK -> X-Ray daemon / ADOT collector (UDP 2000) -> X-Ray -> service map + traces
```

## 💻 Code / Config Example
```javascript
// Node.js (aws-xray-sdk-core) - Express app on ECS/EC2 with X-Ray daemon/ADOT
const AWSXRay = require('aws-xray-sdk-core');
const express = require('express');
const xrayExpress = require('aws-xray-sdk-express');
const AWS = AWSXRay.captureAWS(require('aws-sdk')); // traces SDK v2 calls

const app = express();
app.use(xrayExpress.openSegment('orders-api'));
app.get('/orders/:id', async (req, res) => {
  const sub = AWSXRay.getSegment().addNewSubsegment('db-lookup');
  try { /* query */ res.json({ ok: true }); }
  finally { sub.close(); }
});
app.use(xrayExpress.closeSegment());
app.listen(3000);
```
```yaml
# Lambda via SAM: one line
Globals:
  Function: { Tracing: Active }
```
Note: AWS has been steering new work toward OpenTelemetry (ADOT) as the instrumentation path; check current docs for SDK status.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | X-Ray | Application Insights |
| Map | Service map | Application Map |
| Instrumentation | X-Ray SDK / OpenTelemetry (ADOT) | App Insights SDK / OpenTelemetry |
| Pricing | Per traces recorded/retrieved (check current docs) | Per GB ingested |

## ⚠️ Common Mistakes
❌ No daemon/collector, so no traces. ✅ Run daemon sidecar or ADOT collector.
❌ Tracing 100% of high traffic. ✅ Tune sampling rules.

## ⚫ Interview Q&A
Q1 [Easy]: Segment vs subsegment? A1: Segment = a service's work; subsegment = downstream call or code block.
Q2 [Medium]: How does a trace cross services? A2: Propagated via X-Amzn-Trace-Id header.
Q3 [Hard]: How to reduce cost? A3: Sampling rules (e.g. 5% + first request per second), filter noisy health checks.

## ✅ Quick Checklist
□ Daemon/collector deployed
□ Sampling rules set
□ Lambda Tracing Active

## ⚡ 1-Line Summary
X-Ray follows one request across all services | X-Ray एक रिक्वेस्ट का पूरा रास्ता और देरी दिखाता है।

## ➡️ Next: AWS SDK (Node.js + Python)
