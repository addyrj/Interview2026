# 104. ECS + ECR
# AWS: ECS pulling images from ECR (+ GitHub Actions deploy)
# Azure: Container Apps / AKS pulling from ACR
# हिंदी में: GitHub Actions से image बनाकर ECR में push करना और ECS में deploy करना

---

## 🔵 Simple Definition
CI builds a Docker image, pushes it to ECR, then updates the ECS task definition to the new image tag and redeploys the service.
Image बनाओ, ECR में डालो, ECS को नया tag दो।

---

## 🔴 Why it Exists
ECS needs a private, IAM-authenticated registry close to the cluster; manual `docker push` + console edits are not repeatable.

---

## 🟢 How it Works
```
git push -> GitHub Actions -> OIDC assume role (no static keys)
   -> docker build & push :sha to ECR
   -> render task definition with new image
   -> ecs deploy (waits for service stability)
Task execution role pulls image from ECR at launch.
```

---

## 💻 Code / Config Example
```yaml
# .github/workflows/deploy.yml
name: deploy
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: ap-south-1
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2
      - name: Build and push
        run: |
          IMG=${{ steps.ecr.outputs.registry }}/api:${{ github.sha }}
          docker build -t "$IMG" .
          docker push "$IMG"
          echo "IMG=$IMG" >> "$GITHUB_ENV"
      - id: td
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-def.json
          container-name: api
          image: ${{ env.IMG }}
      - uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.td.outputs.task-definition }}
          service: api
          cluster: prod
          wait-for-service-stability: true
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Registry | ECR | ACR |
| CI auth | GitHub OIDC -> IAM role | GitHub OIDC -> Entra federated credential |
| Pull permission | Task execution role | Managed identity (AcrPull role) |
| Pricing | Storage per GB-month + transfer (approximate - check current docs) | Per registry SKU per day (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Deploying `:latest` - ECS does not know it changed.
✅ Correct: Tag by commit SHA and register a new task definition revision.

❌ Mistake: Execution role missing ECR permissions in a private subnet without endpoints.
✅ Correct: Add ECR (api + dkr) and S3 VPC endpoints, or a NAT gateway.

---

## ⚫ Interview Q&A
Q1: [Easy] Where does ECS pull images from?
A1: ECR (or any registry); auth via the task execution role.
Q2: [Medium] Why OIDC instead of access keys in GitHub?
A2: Short-lived credentials, no secret to rotate or leak.
Q3: [Hard] Task fails with CannotPullContainerError in private subnet?
A3: No route to ECR: add VPC endpoints (ecr.api, ecr.dkr, S3 gateway) or NAT, and check the execution role.

---

## ✅ Quick Checklist
□ Immutable SHA tags
□ OIDC role scoped to repo/branch
□ Network path to ECR from tasks

---

## ⚡ 1-Line Summary
CI pushes SHA-tagged images to ECR and rolls ECS forward | CI image ECR में डालकर ECS को नया version देता है।

## ➡️ Next: 105. ECR - Container Registry
