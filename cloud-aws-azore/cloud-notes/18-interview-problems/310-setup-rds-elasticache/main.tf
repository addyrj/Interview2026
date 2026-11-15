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

variable "data_subnet_ids" {
  type = list(string) # isolated subnets in 2+ AZ
}

variable "app_sg_id" {
  type = string
}

resource "aws_security_group" "db" {
  name   = "rds-sg"
  vpc_id = var.vpc_id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.app_sg_id]
  }
}

resource "aws_security_group" "cache" {
  name   = "redis-sg"
  vpc_id = var.vpc_id
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.app_sg_id]
  }
}

resource "aws_db_subnet_group" "db" {
  name       = "data-db"
  subnet_ids = var.data_subnet_ids
}

resource "aws_db_parameter_group" "pg" {
  name   = "app-pg16"
  family = "postgres16"
  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }
}

resource "aws_db_instance" "pg" {
  identifier                  = "app-pg"
  engine                      = "postgres"
  engine_version              = "16"
  instance_class              = "db.t4g.medium"
  allocated_storage           = 50
  max_allocated_storage       = 200 # storage autoscaling
  storage_encrypted           = true
  multi_az                    = true
  db_name                     = "app"
  username                    = "appadmin"
  manage_master_user_password = true
  parameter_group_name        = aws_db_parameter_group.pg.name
  db_subnet_group_name        = aws_db_subnet_group.db.name
  vpc_security_group_ids      = [aws_security_group.db.id]
  backup_retention_period     = 7
  deletion_protection         = true
  skip_final_snapshot         = false
  final_snapshot_identifier   = "app-pg-final"
  performance_insights_enabled = true
}

resource "aws_elasticache_subnet_group" "cache" {
  name       = "data-cache"
  subnet_ids = var.data_subnet_ids
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "app-redis"
  description                = "Redis cache for app"
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = "cache.t4g.small"
  num_cache_clusters         = 2 # primary + 1 replica in another AZ
  automatic_failover_enabled = true
  multi_az_enabled           = true
  subnet_group_name          = aws_elasticache_subnet_group.cache.name
  security_group_ids         = [aws_security_group.cache.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
}

output "db_endpoint" {
  value = aws_db_instance.pg.address
}

output "redis_primary_endpoint" {
  value = aws_elasticache_replication_group.redis.primary_endpoint_address
}
