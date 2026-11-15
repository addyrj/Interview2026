#!/usr/bin/env bash
# Initial + incremental file copy from VPS to S3 (cutover does a final delta sync).
# Usage: ./sync-data.sh /var/www/uploads my-bucket [--dry-run]
set -euo pipefail
SRC="${1:?source dir}"
BUCKET="${2:?bucket}"
EXTRA="${3:-}"
# aws s3 sync only copies new/changed files, so it is safe to re-run before cutover.
aws s3 sync "$SRC" "s3://$BUCKET/uploads/" --only-show-errors $EXTRA
echo "synced $SRC -> s3://$BUCKET/uploads/"
# Azure equivalent: azcopy sync "$SRC" "https://<acct>.blob.core.windows.net/<container>" --recursive
