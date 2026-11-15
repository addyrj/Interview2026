# 101. ECS Fargate vs EC2
# AWS: Amazon ECS (Fargate launch type vs EC2 launch type)
# Azure: Azure Container Apps / Azure Container Instances (serverless) vs AKS node pools (VM-based)
# हिंदी में: ECS में container चलाने के दो तरीके - Fargate (server AWS संभालता है) या EC2 (server आप संभालते हैं)

---

## 🔵 Simple Definition
ECS runs your Docker containers. With Fargate AWS manages the servers; with the EC2 launch type you run and patch the EC2 instances yourself.
Fargate = कोई server नहीं संभालना, EC2 = server आपकी ज़िम्मेदारी, पर सस्ता और ज़्यादा control।

---

## 🔴 Why it Exists
Teams want to run containers without managing OS patching and capacity (Fargate), but some need GPUs, custom AMIs, or lower cost at steady load (EC2).

---

## 🟢 How it Works
```
Task Definition (image, cpu, memory)
        |
   ECS Service  --launchType-->  FARGATE : AWS picks hidden host, you pay per vCPU+GB-second
        |                  \-->  EC2     : tasks placed on YOUR instances (ASG + capacity provider)
        v
   Tasks (containers) in your VPC (awsvpc mode = own ENI per task)
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation (YAML) - Fargate task + service for a NestJS API
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  Subnets: { Type: "List<AWS::EC2::Subnet::Id>" }
  SecurityGroup: { Type: "AWS::EC2::SecurityGroup::Id" }
  ExecRoleArn: { Type: String }
Resources:
  Cluster:
    Type: AWS::ECS::Cluster
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: nest-api
      RequiresCompatibilities: [FARGATE]   # use EC2 for the EC2 launch type
      NetworkMode: awsvpc                  # mandatory for Fargate
      Cpu: "256"                           # 0.25 vCPU (valid combos are fixed)
      Memory: "512"
      ExecutionRoleArn: !Ref ExecRoleArn
      ContainerDefinitions:
        - Name: api
          Image: nginx:alpine              # replace with your ECR image
          PortMappings: [{ ContainerPort: 80 }]
  Service:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref Cluster
      LaunchType: FARGATE
      DesiredCount: 2
      TaskDefinition: !Ref TaskDef
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Ref Subnets
          SecurityGroups: [!Ref SecurityGroup]
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Serverless containers | ECS Fargate | Container Apps / ACI |
| Self-managed hosts | ECS on EC2 | AKS node pools (VMSS) |
| GPU / custom AMI | EC2 launch type only | AKS GPU node pools |
| Pricing | Fargate: per vCPU/GB-second; EC2: pay for instances (approximate - check current docs) | Container Apps: per vCPU/GB-second with free grant (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using Fargate for a 24x7 high-CPU workload and ignoring cost.
✅ Correct: Compare with EC2 + Savings Plans / Fargate Spot for steady or interruptible load.

❌ Mistake: Invalid Fargate CPU/memory combo (e.g. 256 CPU with 8 GB).
✅ Correct: Use documented combos (256 CPU supports 512 MB - 2 GB).

---

## ⚫ Interview Q&A
Q1: [Easy] What is the difference between Fargate and EC2 launch type?
A1: Fargate is serverless (no instances to manage); EC2 means you manage the cluster instances.
Q2: [Medium] When pick EC2 over Fargate?
A2: GPUs, privileged/daemon workloads, very large tasks, or cheaper steady-state utilisation with bin-packing.
Q3: [Hard] How do you mix both?
A3: Capacity providers: a service can use FARGATE, FARGATE_SPOT and EC2 ASG providers with base/weight strategy.

---

## ✅ Quick Checklist
□ Task definition has valid CPU/memory combo
□ awsvpc mode with proper subnets + security group
□ Execution role can pull from ECR and write logs

---

## ⚡ 1-Line Summary
Fargate = no servers to manage, EC2 = more control/cheaper at scale | Fargate में server नहीं, EC2 में control और बड़े scale पर सस्ता।

## ➡️ Next: 102. ECS with ALB
