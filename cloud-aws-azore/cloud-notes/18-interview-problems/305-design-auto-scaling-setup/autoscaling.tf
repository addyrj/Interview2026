terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "app_subnet_ids" {
  type = list(string)
}

variable "target_group_arn" {
  type = string
}

variable "alb_arn_suffix" {
  type = string # aws_lb.web.arn_suffix
}

variable "target_group_arn_suffix" {
  type = string # aws_lb_target_group.app.arn_suffix
}

variable "ami_id" {
  type = string
}

resource "aws_launch_template" "app" {
  name_prefix   = "scale-app-"
  image_id      = var.ami_id
  instance_type = "t3.small"
}

resource "aws_autoscaling_group" "app" {
  name                      = "scale-app"
  min_size                  = 2
  max_size                  = 10
  desired_capacity          = 2
  vpc_zone_identifier       = var.app_subnet_ids
  target_group_arns         = [var.target_group_arn]
  health_check_type         = "ELB"
  health_check_grace_period = 120

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }
}

# Keep average CPU near 50%
resource "aws_autoscaling_policy" "cpu" {
  name                      = "cpu-50"
  autoscaling_group_name    = aws_autoscaling_group.app.name
  policy_type               = "TargetTrackingScaling"
  estimated_instance_warmup = 120

  target_tracking_configuration {
    target_value = 50
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
  }
}

# Keep ~200 requests per target (better signal for APIs)
resource "aws_autoscaling_policy" "requests" {
  name                      = "requests-per-target"
  autoscaling_group_name    = aws_autoscaling_group.app.name
  policy_type               = "TargetTrackingScaling"
  estimated_instance_warmup = 120

  target_tracking_configuration {
    target_value = 200
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${var.alb_arn_suffix}/${var.target_group_arn_suffix}"
    }
  }
}

# Raise the floor for business hours (UTC), drop it at night
resource "aws_autoscaling_schedule" "day" {
  scheduled_action_name  = "business-hours"
  autoscaling_group_name = aws_autoscaling_group.app.name
  min_size               = 4
  max_size               = 10
  desired_capacity       = 4
  recurrence             = "30 3 * * MON-FRI"
}

resource "aws_autoscaling_schedule" "night" {
  scheduled_action_name  = "off-hours"
  autoscaling_group_name = aws_autoscaling_group.app.name
  min_size               = 2
  max_size               = 10
  desired_capacity       = 2
  recurrence             = "30 14 * * MON-FRI"
}
