---

# 93. Lambda + API Gateway
# AWS: API Gateway (HTTP API) + Lambda
# Azure: Azure API Management / Functions HTTP trigger
# हिंदी में: लैम्ब्डा + API गेटवे

---

## 🔵 Simple Definition (2 lines)
API Gateway gives Lambda a public HTTPS URL and routes requests (GET /users) to functions.
हिंदी: API Gateway Lambda को HTTPS URL देता है और रिक्वेस्ट को सही फ़ंक्शन तक पहुँचाता है।

---

## 🔴 Why it Exists (2 lines)
Lambda has no HTTP endpoint of its own. API Gateway adds routing, auth, throttling, CORS and TLS in front of it.

---

## 🟢 How it Works
```
Client -> HTTPS -> API Gateway (route: GET /hello)
                      | proxy integration (payload format 2.0)
                      v
                   Lambda handler(event) -> {statusCode, headers, body}
                      |
                   Response back to client
```

---

## 💻 Code / Config Example
```yaml
# SAM template.yaml: HTTP API + Lambda
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  HelloFn:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: nodejs20.x
      Handler: index.handler
      Events:
        Hello:
          Type: HttpApi
          Properties: { Path: "/hello/{name}", Method: GET }
Outputs:
  Url:
    Value: !Sub "https://${ServerlessHttpApi}.execute-api.${AWS::Region}.amazonaws.com/hello/dev"
```
```javascript
// index.mjs : HTTP API payload v2.0
export const handler = async (event) => ({
  statusCode: 200,
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ hello: event.pathParameters?.name, method: event.requestContext.http.method }),
});
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Front door | API Gateway | API Management or Functions' built-in HTTP trigger |
| Routing | Routes to Lambda/HTTP/ALB | Operations to backends |
| Built-in alt | Lambda Function URL | Function HTTP trigger URL |
| Pricing | Per million requests (approximate — check current docs) | Consumption APIM per call (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Returning plain object/string without statusCode in REST proxy mode (502 Malformed Lambda proxy response).
✅ Correct: Return `{statusCode, headers, body}` with body as a string.

❌ Mistake: Forgetting CORS for browser clients.
✅ Correct: Configure CORS on the API (and return headers on REST).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Why API Gateway in front of Lambda?
A1: Public endpoint plus routing, auth, throttling, TLS.

Q2: [Medium] What is proxy integration?
A2: Gateway passes the whole request as event to Lambda and returns Lambda's response as-is.

Q3: [Hard] Can you run a NestJS/Express app on Lambda?
A3: Yes, with an adapter (e.g. serverless-http / @vendia/serverless-express) mapping events to the HTTP app; mind cold start and the 29-30 s API timeout.

---

## ✅ Quick Checklist
□ HTTP API unless REST features needed
□ CORS and throttling set
□ Access logs enabled

---

## ⚡ 1-Line Summary
API Gateway exposes Lambda over HTTPS | API Gateway Lambda को HTTPS पर उपलब्ध कराता है।

## ➡️ Next: API Gateway — Complete Guide

---
