terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string) # 3 subnets, one per AZ
}

variable "app_subnet_ids" {
  type = list(string)
}

variable "db_subnet_group_name" {
  type = string
}

variable "alb_sg_id" {
  type = string
}

variable "app_sg_id" {
  type = string
}

variable "db_sg_id" {
  type = string
}

variable "ami_id" {
  type = string
}

resource "aws_lb" "web" {
  name                             = "ha-alb"
  load_balancer_type               = "application"
  subnets                          = var.public_subnet_ids
  security_groups                  = [var.alb_sg_id]
  enable_cross_zone_load_balancing = true
}

resource "aws_lb_target_group" "app" {
  name                 = "ha-app"
  port                 = 3000
  protocol             = "HTTP"
  vpc_id               = var.vpc_id
  deregistration_delay = 30
  health_check {
    path                = "/health"
    interval            = 15
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.web.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_launch_template" "app" {
  name_prefix            = "ha-app-"
  image_id               = var.ami_id
  instance_type          = "t3.small"
  vpc_security_group_ids = [var.app_sg_id]
}

resource "aws_autoscaling_group" "app" {
  min_size                  = 3
  max_size                  = 9
  desired_capacity          = 3
  vpc_zone_identifier       = var.app_subnet_ids
  target_group_arns         = [aws_lb_target_group.app.arn]
  health_check_type         = "ELB"
  health_check_grace_period = 120

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 66
    }
  }
}

resource "aws_rds_cluster" "db" {
  cluster_identifier          = "ha-aurora"
  engine                      = "aurora-postgresql"
  database_name               = "app"
  master_username             = "appadmin"
  manage_master_user_password = true
  db_subnet_group_name        = var.db_subnet_group_name
  vpc_security_group_ids      = [var.db_sg_id]
  storage_encrypted           = true
  backup_retention_period     = 7
  skip_final_snapshot         = true
}

# Writer and reader land in different AZ; the reader is the failover target
resource "aws_rds_cluster_instance" "db" {
  count              = 2
  identifier         = "ha-aurora-${count.index}"
  cluster_identifier = aws_rds_cluster.db.id
  engine             = aws_rds_cluster.db.engine
  instance_class     = "db.t4g.medium"
}
