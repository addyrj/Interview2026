#!/bin/bash
# Quick CLI alternative (AWS CLI v2) and a way to test the notification path.
set -euo pipefail
TOPIC_ARN="${1:?usage: put-alarm.sh <sns-topic-arn>}"

aws cloudwatch put-metric-alarm \
  --alarm-name demo-cpu-high \
  --namespace AWS/EC2 --metric-name CPUUtilization \
  --statistic Average --period 300 --evaluation-periods 3 \
  --threshold 80 --comparison-operator GreaterThanThreshold \
  --alarm-actions "$TOPIC_ARN"

# Force the alarm into ALARM to verify the email arrives
aws cloudwatch set-alarm-state --alarm-name demo-cpu-high \
  --state-value ALARM --state-reason "test notification"
