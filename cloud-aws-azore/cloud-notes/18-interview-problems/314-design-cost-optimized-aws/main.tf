# Cost-optimized web tier: Spot-heavy ASG on Graviton, S3 lifecycle, budget alert.
# Terraform >= 1.5, AWS provider ~> 5.0. Not applied here (no credentials).
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}
provider "aws" { region = "ap-south-1" }

variable "subnet_ids"  { type = list(string) }
variable "alert_email" { type = string }

data "aws_ssm_parameter" "al2023_arm" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64"
}

resource "aws_launch_template" "web" {
  name_prefix   = "web-"
  image_id      = data.aws_ssm_parameter.al2023_arm.value
  instance_type = "t4g.small"          # Graviton; overridden by ASG list below

  metadata_options {
    http_tokens = "required"           # IMDSv2
  }
  tag_specifications {
    resource_type = "instance"
    tags          = { CostCenter = "web", Env = "prod" }
  }
}

resource "aws_autoscaling_group" "web" {
  name                = "web-spot"
  min_size            = 2
  max_size            = 6
  desired_capacity    = 2
  vpc_zone_identifier = var.subnet_ids

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 1    # baseline stays on-demand
      on_demand_percentage_above_base_capacity = 0    # everything above is Spot
      spot_allocation_strategy                 = "price-capacity-optimized"
    }
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.web.id
        version            = "$Latest"
      }
      # Several families -> more Spot pools -> fewer interruptions.
      override { instance_type = "t4g.small" }
      override { instance_type = "t4g.medium" }
      override { instance_type = "m6g.large" }
    }
  }
}

# Scale on CPU so you do not pay for idle capacity.
resource "aws_autoscaling_policy" "cpu" {
  name                   = "cpu-target-50"
  autoscaling_group_name = aws_autoscaling_group.web.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 50
  }
}

resource "aws_s3_bucket" "logs" {
  bucket = "myapp-logs-example-12345"
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    id     = "tiering"
    status = "Enabled"
    filter {}
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    expiration { days = 365 }
    abort_incomplete_multipart_upload { days_after_initiation = 7 }
  }
}

resource "aws_budgets_budget" "monthly" {
  name         = "monthly-cap"
  budget_type  = "COST"
  limit_amount = "100"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.alert_email]
  }
}
