# 41. ALB vs NLB vs CLB
# AWS: Elastic Load Balancing (ALB / NLB / CLB)
# Azure: Application Gateway (L7) / Azure Load Balancer (L4)
# हिंदी में: ट्रैफिक को कई सर्वरों में बाँटने वाले तीन तरह के लोड बैलेंसर

---

## 🔵 Simple Definition (2 lines)
ALB works at Layer 7 (HTTP/HTTPS, path/host routing), NLB at Layer 4 (TCP/UDP/TLS, very fast, static IP), CLB is the legacy one that does both poorly.
ALB = HTTP समझता है, NLB = सिर्फ TCP/UDP पैकेट, CLB = पुराना (deprecated जैसा) विकल्प।

---

## 🔴 Why it Exists (2 lines)
One server cannot handle all traffic or survive failure; a load balancer spreads requests across healthy targets in many AZs.
Different protocols need different balancers: web APIs need routing rules, games/DBs need raw speed.

---

## 🟢 How it Works
```
Client -> DNS -> [ALB: listener :443]
                   rule /api/*  -> TG api  (NestJS :3000)
                   rule /ml/*   -> TG ml   (FastAPI :8000)
                   default      -> TG web
Client -> [NLB: listener TCP:5432] -> TG (targets, static IP per AZ)
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation: internet-facing ALB with HTTPS listener
Resources:
  Alb:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Type: application            # use "network" for NLB
      Scheme: internet-facing
      Subnets: [subnet-aaa, subnet-bbb]   # 2+ AZs
      SecurityGroups: [sg-0123456789abcdef0]
  ApiTg:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      VpcId: vpc-0123456789abcdef0
      Port: 3000
      Protocol: HTTP
      TargetType: ip
      HealthCheckPath: /health
  Https:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref Alb
      Port: 443
      Protocol: HTTPS
      Certificates: [{ CertificateArn: arn:aws:acm:ap-south-1:111122223333:certificate/example }]
      DefaultActions: [{ Type: forward, TargetGroupArn: !Ref ApiTg }]
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| L7 (HTTP) | ALB | Application Gateway |
| L4 (TCP/UDP) | NLB | Azure Load Balancer |
| Legacy | CLB (not for new builds) | N/A (AWS-only concept) |
| Pricing | per hour + LCU/NLCU (approximate — check current docs) | per hour + capacity units / rules + data (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using CLB for new projects, or NLB when you need path-based routing.
✅ Correct: ALB for HTTP APIs (NestJS/FastAPI), NLB for TCP/UDP, static IP, or extreme throughput.

❌ Mistake: Putting the ALB in only one AZ/subnet.
✅ Correct: At least two subnets in different AZs.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which LB supports path-based routing?
A1: ALB (also host, header, query-string rules). NLB and CLB do not.

Q2: [Medium] You need a fixed IP for a partner's firewall allow-list. What do you use?
A2: NLB gives one static (Elastic) IP per AZ. ALB IPs change; either put an NLB in front of ALB or use Global Accelerator.

Q3: [Hard] Client IP is lost behind ALB; how to get it?
A3: ALB terminates the connection, so read the `X-Forwarded-For` header. NLB can preserve the source IP for instance targets (and via proxy protocol v2 if enabled).

---

## ✅ Quick Checklist
□ ALB for HTTP/HTTPS, NLB for TCP/UDP
□ Subnets span 2+ AZs
□ Health check path returns 200 quickly
□ ACM certificate on the HTTPS listener

---

## ⚡ 1-Line Summary
ALB routes web traffic smartly, NLB moves raw packets fast, CLB is legacy. | वेब के लिए ALB, तेज़ TCP के लिए NLB, CLB नए काम में नहीं।

## ➡️ Next: Target Groups
