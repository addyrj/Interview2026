# 379. Pull Image from ECR
# हिंदी में: ECR से Image Pull करना

---

## 🔵 Simple Definition (English)
Pulling from ECR means a machine (ECS task, EC2/VPS host, Kubernetes node or your laptop) authenticates to the registry and downloads an image's layers by tag or digest so a container can start from it.

## 🔵 सरल परिभाषा (Hindi)
ECR से pull करने का मतलब है कि कोई machine (ECS task, EC2/VPS host, Kubernetes node या laptop) registry में authenticate होकर tag या digest से image की layers download करती है ताकि उससे container start हो सके।

---

## 🔴 Problem it Solves
- Servers need the exact tested artifact, not a fresh build on the server (builds on prod servers are slow, non-reproducible and need dev tools installed).
- Pull permissions must be separate from push permissions: servers should never be able to overwrite images.
- Pulls over the public internet via NAT are slow and cost money.

## 🔴 यह क्यों बना? (Hindi)
- Servers को वही tested artifact चाहिए, server पर नया build नहीं (prod पर build धीमा, non-reproducible और dev tools माँगता है)।
- Pull और push की permissions अलग होनी चाहिए: servers कभी images overwrite न कर सकें।
- NAT से public internet पर pull धीमा और महँगा होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Host/agent authenticates (execution role, instance role, or docker login)
Step 2 → Docker asks ECR for the manifest of repo:tag
Step 3 → ECR returns the list of layer digests
Step 4 → Docker downloads missing layers (parallel, from S3 via ECR)
Step 5 → Layers are verified by hash and unpacked
Step 6 → Container starts from the image
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Host/agent authenticate करता है (execution role, instance role या docker login)
Step 2 → Docker ECR से repo:tag का manifest माँगता है
Step 3 → ECR layer digests की list देता है
Step 4 → Docker जो layers नहीं हैं उन्हें download करता है (parallel, S3 से)
Step 5 → Layers hash से verify होकर unpack होती हैं
Step 6 → Image से container start होता है
```

---

## 🟡 Real World Example
During a flash sale, an ECS service autoscales from 4 to 40 Fargate tasks in two minutes. Each new task must pull the 120 MB image. With a slim image and VPC endpoints for ECR and S3, all 36 new tasks pull privately in seconds. Before the fix (900 MB image, NAT gateway), scaling took 6 minutes and the NAT data bill was large.

## 🟡 Real Example Hindi mein
Flash sale के दौरान ECS service दो मिनट में 4 से 40 Fargate tasks तक scale होती है। हर नए task को 120 MB image pull करनी है। Slim image और ECR/S3 के VPC endpoints के साथ 36 नए tasks सेकंडों में private pull कर लेते हैं। पहले (900 MB image, NAT gateway) scaling में 6 मिनट लगते थे और NAT data का bill बड़ा था।

---

## 💻 Code / Config Example — Basic

```bash
# pull-basic.sh  - pull on a laptop/VPS
set -euo pipefail                                        # stop on first failure
REGION=ap-south-1                                        # registry region
REG=123456789012.dkr.ecr.$REGION.amazonaws.com          # registry host (example account)
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REG   # login
docker pull $REG/myapp-api:4f2a9c1d8e3b                  # pull by immutable tag
docker pull $REG/myapp-api@sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef   # example digest pull (replace with a real digest)
docker run -d --name api -p 127.0.0.1:3000:3000 $REG/myapp-api:4f2a9c1d8e3b   # run bound to localhost only
```

## 💻 Code / Config Example — Advanced
IAM pull-only policy for servers, plus VPC endpoints so private subnets pull without NAT.

```yaml
# ecr-pull-infra.yml  - CloudFormation (parameters supplied at deploy time)
AWSTemplateFormatVersion: "2010-09-09"              # template version
Parameters:
  VpcId: {Type: AWS::EC2::VPC::Id}                  # VPC where tasks run
  PrivateSubnets: {Type: "List<AWS::EC2::Subnet::Id>"}   # private subnets of the tasks
  TaskSg: {Type: AWS::EC2::SecurityGroup::Id}       # security group of the tasks
  RouteTableIds: {Type: "List<String>"}             # private route tables (for S3 gateway endpoint)
Resources:
  PullPolicy:
    Type: AWS::IAM::ManagedPolicy                   # attach to EC2 instance role / VPS user
    Properties:
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Action: ecr:GetAuthorizationToken       # token for docker login
            Resource: "*"                           # this action cannot be limited by repo
          - Effect: Allow
            Action:                                 # read only: no PutImage
              - ecr:BatchGetImage
              - ecr:GetDownloadUrlForLayer
              - ecr:BatchCheckLayerAvailability
            Resource: arn:aws:ecr:ap-south-1:123456789012:repository/myapp-api
  EcrApiEndpoint:
    Type: AWS::EC2::VPCEndpoint                     # private path to ECR API
    Properties:
      VpcId: !Ref VpcId
      ServiceName: com.amazonaws.ap-south-1.ecr.api # login and manifest calls
      VpcEndpointType: Interface                    # ENI based endpoint
      SubnetIds: !Ref PrivateSubnets
      SecurityGroupIds: [!Ref TaskSg]               # must allow 443 from tasks
      PrivateDnsEnabled: true                       # normal hostnames resolve privately
  EcrDkrEndpoint:
    Type: AWS::EC2::VPCEndpoint                     # private path to the Docker registry API
    Properties:
      VpcId: !Ref VpcId
      ServiceName: com.amazonaws.ap-south-1.ecr.dkr
      VpcEndpointType: Interface
      SubnetIds: !Ref PrivateSubnets
      SecurityGroupIds: [!Ref TaskSg]
      PrivateDnsEnabled: true
  S3Endpoint:
    Type: AWS::EC2::VPCEndpoint                     # layers are stored in S3, so this is required too
    Properties:
      VpcId: !Ref VpcId
      ServiceName: com.amazonaws.ap-south-1.s3
      VpcEndpointType: Gateway                      # free gateway endpoint
      RouteTableIds: !Ref RouteTableIds
```

---

## 🟠 My Stack Integration
On a VPS you pull the Node/FastAPI image and Compose restarts it. A deploy script keeps it repeatable; Nginx proxies to localhost.

```bash
#!/usr/bin/env bash
# /opt/app/deploy.sh <tag>  - run on the VPS (aws cli + docker + compose installed)
set -euo pipefail                                   # strict mode
TAG="$1"                                            # image tag passed by CI over SSH
REG=123456789012.dkr.ecr.ap-south-1.amazonaws.com   # registry host
cd /opt/app                                         # folder with docker-compose.yml
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin "$REG"   # fresh token
export IMAGE_TAG="$TAG"                             # compose file reads ${IMAGE_TAG}
docker compose pull api                             # download new image first (no downtime yet)
docker compose up -d api                            # recreate container with new image
docker image prune -f                               # remove dangling layers to save disk
curl -fsS http://127.0.0.1:3000/health              # fail the script if the new version is unhealthy
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Private subnet tasks without S3 endpoint.
✅ Correct: ECR needs ecr.api + ecr.dkr + S3 gateway endpoints (or a NAT); otherwise "CannotPullContainerError ... i/o timeout".

❌ Mistake 2: Using the task role for pulling.
✅ Correct: Pull uses the task EXECUTION role; the task role is for your app code calling AWS.

❌ Mistake 3: Server with push permission.
✅ Correct: Read-only pull policy for runtime hosts.

❌ Mistake 4: Pulling `latest` in prod.
✅ Correct: Pull an SHA tag or digest to get what you tested.

---

## 🧠 Tricky Interview Question
A Fargate task in a public subnet with no public IP assigned fails with `CannotPullContainerError: ... dial tcp ... i/o timeout`. The execution role is correct. Why?

Answer: Pulling needs network reach to ECR and S3. A public subnet task without a public IP (and no NAT/VPC endpoints) has no route out. Fix by enabling `assignPublicIp: ENABLED`, using a NAT gateway, or adding the VPC endpoints.

---

## ⚫ Interview Questions + Answers

Q1: What does ECS pull on each task start?
A1: Only missing layers; Fargate has no cache between tasks, so each new task pulls everything. Small images matter.

Q2: How to speed up Fargate startup?
A2: Smaller images, fewer layers, same-region ECR, VPC endpoints, and SOCI (seekable OCI) lazy loading for big images.

Q3: Why is a digest more secure than a tag?
A3: Tags can be re-pointed (if mutable). A digest is a content hash: an attacker cannot swap the image under you.

Q4: How to pull from another AWS account?
A4: Add a repository policy allowing that account's principal, and give its role the pull actions.

Q5: What are ECR pull-through cache rules?
A5: ECR can proxy and cache images from upstream registries (Docker Hub, Quay, etc.), avoiding Docker Hub rate limits. Set up per upstream; Docker Hub needs credentials in Secrets Manager.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every runtime (ECS/EKS/EC2/VPS) gets images from the registry, not from builds

❌ Avoid when:
- Building on the production server
- Pulling by mutable tags in production

---

## 📊 Visual Diagram
```
 ECS agent --(execution role)--> ECR API  (via vpce ecr.api / ecr.dkr)
      |                              |
      |<------ manifest + layer list-+
      +--- layer download ---------> S3 (via gateway endpoint)
      v
  container starts (no internet needed)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pull | Download image layers | Image layers download करना |
| Execution role | Role used to pull and log | Pull और log का role |
| VPC endpoint | Private door to an AWS service | AWS service का private दरवाज़ा |
| Pull-through cache | ECR proxy for other registries | दूसरे registry का cache |
| SOCI | Lazy-load large images | बड़ी images का lazy loading |

---

## ⚡ 3-Line Summary
English: Servers pull exact tagged or digest images using a read-only identity.
In private subnets add ECR and S3 VPC endpoints so pulls work without NAT.
Small images and SHA tags make scaling fast and rollbacks safe.

Hindi: Servers read-only identity से exact tag या digest वाली image pull करते हैं।
Private subnets में ECR और S3 VPC endpoints जोड़ो ताकि NAT के बिना pull चले।
छोटी images और SHA tags से scaling तेज़ और rollback सुरक्षित रहता है।

---

## ➡️ Next Topic
380. ECR Lifecycle Policies: automatic cleanup so old images do not pile up.
