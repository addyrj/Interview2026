#!/bin/bash
# Rendered by Terraform templatefile(); ${app_image} and ${app_port} are Terraform vars.
set -euo pipefail
dnf install -y docker
systemctl enable --now docker
docker run -d --restart unless-stopped --name api -p ${app_port}:${app_port} -e PORT=${app_port} ${app_image}
