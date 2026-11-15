#!/bin/bash
# Generate load to watch scale-out. Requires `hey` (https://github.com/rakyll/hey).
set -euo pipefail
URL="${1:?usage: loadtest.sh http://<alb-dns>/health}"
hey -z 300s -c 100 -q 20 "$URL"
# Watch activity:
#   aws autoscaling describe-scaling-activities --auto-scaling-group-name scale-app --max-items 5
