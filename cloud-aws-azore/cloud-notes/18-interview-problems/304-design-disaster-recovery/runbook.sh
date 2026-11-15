#!/bin/bash
# DR runbook: restore latest RDS recovery point in the DR region.
# Requires AWS CLI v2 and credentials; run in the DR region.
set -euo pipefail

DR_REGION="${DR_REGION:-ap-southeast-1}"
VAULT="dr-vault"
RESOURCE_TYPE="RDS"

echo "1. Find newest recovery point in ${VAULT}"
RP_ARN=$(aws backup list-recovery-points-by-backup-vault \
  --region "$DR_REGION" --backup-vault-name "$VAULT" \
  --by-resource-type "$RESOURCE_TYPE" \
  --query 'sort_by(RecoveryPoints,&CreationDate)[-1].RecoveryPointArn' --output text)
echo "   $RP_ARN"

echo "2. Start restore (metadata must match your DR subnet group / SGs)"
echo "   aws backup get-recovery-point-restore-metadata --region $DR_REGION \\"
echo "     --backup-vault-name $VAULT --recovery-point-arn $RP_ARN"
echo "   then: aws backup start-restore-job --recovery-point-arn ... --metadata file://meta.json --iam-role-arn ..."

echo "3. Terraform apply the app stack in DR region, then flip Route 53 failover record"
