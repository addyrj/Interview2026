# 102. ECS with ALB
# AWS: ECS Service + Application Load Balancer (target group)
# Azure: Container Apps built-in ingress / AKS + Application Gateway
# हिंदी में: ALB traffic को ECS के कई containers में बाँटता है और unhealthy container हटा देता है

---

## 🔵 Simple Definition
An ALB sits in front of an ECS service, registers each task as a target in a target group, and routes HTTP requests to healthy tasks only.
ALB request को healthy containers तक पहुँचाता है, बीमार container अपने-आप बाहर।

---

## 🔴 Why it Exists
Task IPs change on every deploy; you need one stable DNS name, health checks, path routing and zero-downtime rolling deploys.

---

## 🟢 How it Works
```
Internet -> ALB :443 (listener) -> rule (path /api/*) -> Target Group (type=ip)
                                                          |-- Task A 10.0.1.5:3000
                                                          |-- Task B 10.0.2.7:3000
ECS service registers/deregisters task IPs automatically.
Health check: GET /health -> 200 else task replaced.
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation fragment: target group + listener + service wiring
Resources:
  TG:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      VpcId: !Ref VpcId
      Port: 3000
      Protocol: HTTP
      TargetType: ip                       # required for awsvpc/Fargate
      HealthCheckPath: /health
      HealthCheckIntervalSeconds: 15
      HealthyThresholdCount: 2
      TargetGroupAttributes:
        - { Key: deregistration_delay.timeout_seconds, Value: "30" }
  Listener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref Alb
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - { Type: forward, TargetGroupArn: !Ref TG }
  Service:
    Type: AWS::ECS::Service
    DependsOn: Listener                    # listener must exist first
    Properties:
      Cluster: !Ref Cluster
      LaunchType: FARGATE
      DesiredCount: 2
      TaskDefinition: !Ref TaskDef
      HealthCheckGracePeriodSeconds: 60    # let Nest boot before ALB checks kill it
      LoadBalancers:
        - { ContainerName: api, ContainerPort: 3000, TargetGroupArn: !Ref TG }
      NetworkConfiguration:
        AwsvpcConfiguration: { Subnets: !Ref Subnets, SecurityGroups: [!Ref TaskSg] }
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| L7 load balancer | ALB | Application Gateway / Container Apps ingress |
| Health check | Target group health check | Gateway probes / app probes |
| Path routing | Listener rules | URL path map |
| Pricing | Hourly + LCU usage (approximate - check current docs) | Capacity-unit based (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Target type `instance` with awsvpc tasks.
✅ Correct: Use `ip` target type.

❌ Mistake: Task security group does not allow ALB security group on app port.
✅ Correct: Ingress rule from the ALB SG to port 3000.

❌ Mistake: Slow-start app killed in a loop by health checks.
✅ Correct: Set `HealthCheckGracePeriodSeconds`.

---

## ⚫ Interview Q&A
Q1: [Easy] Why an ALB for ECS?
A1: Stable endpoint, health checks, load balancing across tasks.
Q2: [Medium] How are tasks registered?
A2: ECS service registers each task's ENI IP into the target group and deregisters on stop.
Q3: [Hard] Deploys drop requests - why?
A3: Deregistration delay too short/long, no graceful SIGTERM handling, or minimumHealthyPercent too low. Handle SIGTERM and tune the delay.

---

## ✅ Quick Checklist
□ Target type ip, correct port
□ SG chain: internet -> ALB -> task
□ Health endpoint + grace period

---

## ⚡ 1-Line Summary
ALB gives ECS a stable, health-checked front door | ALB ECS को स्थिर endpoint और health check देता है।

## ➡️ Next: 103. ECS Auto Scaling
