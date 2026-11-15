# 55. CloudFront + ALB
# AWS: CloudFront with ALB custom origin
# Azure: Front Door with Application Gateway / App Service origin
# हिंदी में: डायनामिक API/ऐप के आगे CloudFront लगाना

---

## 🔵 Simple Definition (2 lines)
Use an ALB as a custom origin so CloudFront terminates TLS near users and forwards dynamic requests over AWS's backbone.
ALB के आगे CloudFront लगाने से DDoS सुरक्षा, WAF और कम लेटेंसी मिलती है।

---

## 🔴 Why it Exists (2 lines)
Exposed ALBs can be hit directly, bypassing WAF and cache.
CloudFront speeds long-distance connections and caches static parts of a dynamic app.

---

## 🟢 How it Works
```
User -> CloudFront (WAF, cache) --HTTPS--> ALB (public) -> NestJS/FastAPI
Behaviors:  /static/*  -> cache optimized
            /api/*     -> CachingDisabled + AllViewer origin request policy
Lock origin: CloudFront adds secret header X-Origin-Verify; ALB rule requires it
             (or use CloudFront managed prefix list in the ALB security group)
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation: ALB listener rule that accepts only CloudFront-tagged traffic
Resources:
  RequireCfHeader:
    Type: AWS::ElasticLoadBalancingV2::ListenerRule
    Properties:
      ListenerArn: !Ref HttpsListener
      Priority: 1
      Conditions:
        - Field: http-header
          HttpHeaderConfig: { HttpHeaderName: X-Origin-Verify, Values: ["{{resolve:secretsmanager:cf-origin-secret:SecretString}}"] }
      Actions: [{ Type: forward, TargetGroupArn: !Ref ApiTg }]
  # Listener default action: fixed-response 403
  OriginSg:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      GroupId: !Ref AlbSg
      IpProtocol: tcp
      FromPort: 443
      ToPort: 443
      SourcePrefixListId: pl-xxxxxxxx   # look up "com.amazonaws.global.cloudfront.origin-facing" in your Region
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Edge | CloudFront | Azure Front Door |
| Origin | ALB | Application Gateway / App Service |
| Lock origin | Prefix list + secret header | Private Link (Premium) / `X-Azure-FDID` header |
| Pricing | egress + requests (approximate — check current docs) | base + egress (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Leaving ALB reachable from the internet directly.
✅ Correct: Restrict to CloudFront prefix list and/or secret header.

❌ Mistake: Cookies/Authorization not forwarded, so API breaks.
✅ Correct: Use AllViewer origin request policy for dynamic paths.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Why CloudFront before an API?
A1: WAF/Shield, TLS termination at edge, persistent connections to origin, lower latency.

Q2: [Medium] What origin protocol policy should you use?
A2: https-only, with a valid ACM cert on the ALB matching the origin domain.

Q3: [Hard] How do you stop users bypassing CloudFront?
A3: CloudFront managed prefix list in the ALB SG plus a secret custom header verified by an ALB rule, rotated periodically.

---

## ✅ Quick Checklist
□ https-only to origin
□ Prefix list or header lock
□ API behavior not cached
□ Origin timeout tuned for slow endpoints

---

## ⚡ 1-Line Summary
CloudFront in front of ALB adds edge security and speed; lock the ALB to it. | ALB के आगे CloudFront लगाओ और ALB को सीधे एक्सेस से बंद करो।

## ➡️ Next: CloudFront OAC
