# 384. ECS Cluster
# हिंदी में: ECS Cluster (services और tasks का logical group)

---

## 🔵 Simple Definition (English)
An ECS cluster is a logical grouping of capacity and services. With Fargate it is just a namespace (no servers to see). With EC2 it is backed by an Auto Scaling group of instances that run the ECS agent. Capacity providers connect the cluster to the compute.

## 🔵 सरल परिभाषा (Hindi)
ECS cluster capacity और services का logical group है। Fargate में यह सिर्फ एक namespace है (कोई server दिखता नहीं)। EC2 में इसके पीछे instances का Auto Scaling group होता है जो ECS agent चलाता है। Capacity providers cluster को compute से जोड़ते हैं।

---

## 🔴 Problem it Solves
- You need a boundary to organise services, permissions, metrics and capacity per environment.
- You need a place to define where tasks may run (Fargate, Fargate Spot, EC2) and how much capacity exists.

## 🔴 यह क्यों बना? (Hindi)
- Services, permissions, metrics और capacity को environment के हिसाब से व्यवस्थित करने की सीमा चाहिए।
- यह तय करने की जगह चाहिए कि tasks कहाँ चल सकते हैं (Fargate, Fargate Spot, EC2) और कितनी capacity है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create cluster "prod"
Step 2 → Attach capacity providers: FARGATE, FARGATE_SPOT (and/or an EC2 ASG provider)
Step 3 → Set a default capacity provider strategy (e.g. base 2 FARGATE, rest SPOT)
Step 4 → Services in the cluster use that strategy or their own
Step 5 → EC2 only: ASG launches instances with the ECS-optimized AMI, agent registers them
Step 6 → Managed scaling adds instances when tasks cannot be placed
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Cluster "prod" बनाओ
Step 2 → Capacity providers जोड़ो: FARGATE, FARGATE_SPOT (और/या EC2 ASG provider)
Step 3 → Default capacity provider strategy सेट करो (जैसे base 2 FARGATE, बाकी SPOT)
Step 4 → Cluster की services वही strategy या अपनी strategy इस्तेमाल करती हैं
Step 5 → सिर्फ EC2: ASG ECS-optimized AMI वाले instances launch करता है, agent register करता है
Step 6 → Tasks place न हो पाएँ तो managed scaling instances बढ़ाती है
```

---

## 🟡 Real World Example
A company runs three clusters: `dev`, `staging`, `prod`, each in its own AWS account or at least own IAM boundaries. In `prod`, the strategy is base=3 on regular FARGATE (so the minimum is stable) and 70% of extra tasks on FARGATE_SPOT for workers, saving about 60% on the worker bill. Container Insights shows per-service CPU and memory.

## 🟡 Real Example Hindi mein
एक company के तीन clusters हैं: `dev`, `staging`, `prod`, हर का अपना AWS account या कम से कम अपनी IAM सीमा। `prod` में strategy है base=3 regular FARGATE पर (न्यूनतम stable रहे) और extra tasks का 70% workers के लिए FARGATE_SPOT पर, जिससे worker bill लगभग 60% कम होता है। Container Insights से हर service का CPU और memory दिखता है।

---

## 💻 Code / Config Example — Basic

```bash
# cluster-basic.sh
set -euo pipefail                                                  # stop on error
aws ecs create-cluster --cluster-name dev \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1   # simple: all on regular Fargate
aws ecs describe-clusters --clusters dev --include SETTINGS STATISTICS \
  --query 'clusters[0].{status:status,running:runningTasksCount,services:activeServicesCount}'   # check state
```

## 💻 Code / Config Example — Advanced
CloudFormation: cluster with Fargate + Fargate Spot strategy, Container Insights and an EC2 Auto Scaling capacity provider (with managed scaling).

```yaml
# ecs-cluster.yml  - CloudFormation
AWSTemplateFormatVersion: "2010-09-09"             # template version
Parameters:
  PrivateSubnets: {Type: "List<AWS::EC2::Subnet::Id>"}   # subnets for EC2 instances
  InstanceSg: {Type: AWS::EC2::SecurityGroup::Id}  # SG for instances
  AmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ecs/optimized-ami/amazon-linux-2023/recommended/image_id   # AWS-maintained ECS AMI
Resources:
  InstanceRole:
    Type: AWS::IAM::Role                           # role for the EC2 host (agent permissions)
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal: {Service: ec2.amazonaws.com}
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role   # ECS agent permissions
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore                       # SSM shell instead of SSH
  InstanceProfile:
    Type: AWS::IAM::InstanceProfile                # wrapper so EC2 can use the role
    Properties: {Roles: [!Ref InstanceRole]}
  Cluster:
    Type: AWS::ECS::Cluster                        # the cluster itself
    Properties:
      ClusterName: prod
      ClusterSettings:
        - {Name: containerInsights, Value: enabled}   # per-task metrics in CloudWatch
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate                 # how instances look
    Properties:
      LaunchTemplateData:
        ImageId: !Ref AmiId                        # ECS-optimized AMI
        InstanceType: t3.large                     # example size
        IamInstanceProfile: {Arn: !GetAtt InstanceProfile.Arn}
        SecurityGroupIds: [!Ref InstanceSg]
        UserData:
          Fn::Base64: !Sub |                       # tell agent which cluster to join
            #!/bin/bash
            echo "ECS_CLUSTER=${Cluster}" >> /etc/ecs/ecs.config
  Asg:
    Type: AWS::AutoScaling::AutoScalingGroup       # fleet of instances
    Properties:
      MinSize: "0"                                 # capacity provider can scale from zero
      MaxSize: "10"
      VPCZoneIdentifier: !Ref PrivateSubnets
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      NewInstancesProtectedFromScaleIn: true       # required for managed termination protection
  Ec2Provider:
    Type: AWS::ECS::CapacityProvider               # connects ASG to ECS
    Properties:
      AutoScalingGroupProvider:
        AutoScalingGroupArn: !Ref Asg
        ManagedScaling: {Status: ENABLED, TargetCapacity: 80}   # keep ~80% reserved
        ManagedTerminationProtection: ENABLED      # do not kill instances running tasks
  Association:
    Type: AWS::ECS::ClusterCapacityProviderAssociations
    Properties:
      Cluster: !Ref Cluster
      CapacityProviders: [FARGATE, FARGATE_SPOT, !Ref Ec2Provider]
      DefaultCapacityProviderStrategy:
        - {CapacityProvider: FARGATE, Base: 3, Weight: 1}        # first 3 tasks on regular Fargate
        - {CapacityProvider: FARGATE_SPOT, Weight: 3}            # then 3:1 spot to regular
```

---

## 🟠 My Stack Integration
- One cluster per environment: `staging` and `prod`. Services `node-api`, `fastapi-ml`, `worker`.
- Move off the VPS gradually: run staging on ECS Fargate first, keep prod on the VPS behind Nginx, then switch DNS.
- Use SSM Session Manager (ECS Exec) instead of SSH to debug.

```bash
# enable ECS Exec on a service, then open a shell in a running task
aws ecs update-service --cluster prod --service api --enable-execute-command --force-new-deployment   # needs task role ssmmessages permissions
aws ecs execute-command --cluster prod --task <TASK_ID> --container api --interactive --command "/bin/sh"   # shell inside the container
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting dev and prod in one cluster.
✅ Correct: Separate clusters (better, separate accounts).

❌ Mistake 2: All production tasks on Fargate Spot.
✅ Correct: Spot can be reclaimed with a 2-minute warning; use it for fault-tolerant work and keep a regular base.

❌ Mistake 3: EC2 instances in public subnets with SSH open.
✅ Correct: Private subnets and SSM; no port 22.

❌ Mistake 4: Container Insights off, so no data during incidents.
✅ Correct: Enable it (note it has a small cost).

---

## 🧠 Tricky Interview Question
The EC2-backed cluster has plenty of total free memory across instances, but a task that needs 4 GB cannot be placed. Why?

Answer: Free resources are fragmented per instance. Each task must fit on one instance, so four instances with 1 GB free each cannot host a 4 GB task. Use managed scaling to add instances, binpack placement, bigger instance types or Fargate.

---

## ⚫ Interview Questions + Answers

Q1: Is a cluster regional?
A1: Yes, regional. Tasks run in the VPC subnets you specify in that region.

Q2: What is a capacity provider?
A2: A link between the cluster and compute (Fargate, Fargate Spot, or an ASG), with a strategy of base and weight.

Q3: Base vs weight?
A3: Base = minimum number of tasks on that provider first. Weight = ratio for the remaining tasks.

Q4: What is the ECS container agent?
A4: A process on each EC2 instance that talks to ECS, starts containers and reports state. Fargate runs it for you.

Q5: How do you drain an instance for patching?
A5: Set the container instance to DRAINING; ECS moves its tasks elsewhere before you terminate it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always; every ECS service needs a cluster
- Separate clusters for environments or teams

❌ Avoid when:
- Creating a cluster per service (wasteful, hard to manage)

---

## 📊 Visual Diagram
```
 Cluster "prod"
  |-- capacity providers:
  |     FARGATE (base 3) | FARGATE_SPOT (weight 3) | EC2 ASG (managed scaling)
  |-- services: api, worker, ml
  |-- Container Insights -> CloudWatch
  '-- ECS Exec / SSM for debugging
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cluster | Logical group of capacity | Capacity का logical group |
| Capacity provider | Compute source for tasks | Tasks के compute का स्रोत |
| Base / Weight | Fixed count / ratio for the rest | तय संख्या / बाकी का अनुपात |
| Fargate Spot | Cheap interruptible Fargate | सस्ता पर बाधित हो सकने वाला Fargate |
| Container instance | EC2 host running the agent | Agent चलाने वाला EC2 host |

---

## ⚡ 3-Line Summary
English: A cluster is a regional group of services backed by Fargate and/or EC2 capacity.
Capacity providers with base and weight mix stable and cheap compute.
Use one cluster per environment and debug with ECS Exec, not SSH.

Hindi: Cluster services का regional group है जिसके पीछे Fargate और/या EC2 capacity है।
Base और weight वाले capacity providers stable और सस्ता compute मिलाते हैं।
हर environment के लिए एक cluster रखो और debugging ECS Exec से करो, SSH से नहीं।

---

## ➡️ Next Topic
385. Fargate vs EC2 Launch Type: choosing the compute model.
