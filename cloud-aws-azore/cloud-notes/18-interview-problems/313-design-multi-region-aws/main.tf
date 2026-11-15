# Active-passive multi-region: primary ap-south-1, DR ap-southeast-1.
# Terraform >= 1.5, AWS provider ~> 5.0. Not applied here (no credentials).
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = "ap-south-1"
}

provider "aws" {
  alias  = "dr"
  region = "ap-southeast-1"
}

variable "zone_id"        { type = string }  # existing Route 53 hosted zone
variable "domain"         { type = string }  # e.g. api.example.com
variable "primary_alb_dns" { type = string }
variable "primary_alb_zone_id" { type = string }
variable "dr_alb_dns"     { type = string }
variable "dr_alb_zone_id" { type = string }

# Global table (version 2019.11.21): table in primary + replica in DR.
resource "aws_dynamodb_table" "orders" {
  name             = "orders"
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "pk"
  stream_enabled   = true                 # required for replicas
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "pk"
    type = "S"
  }

  replica {
    region_name = "ap-southeast-1"
  }
}

# Health check on the primary ALB; failure triggers DNS failover.
resource "aws_route53_health_check" "primary" {
  fqdn              = var.primary_alb_dns
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 30
}

resource "aws_route53_record" "primary" {
  zone_id         = var.zone_id
  name            = var.domain
  type            = "A"
  set_identifier  = "primary"
  health_check_id = aws_route53_health_check.primary.id

  failover_routing_policy {
    type = "PRIMARY"
  }

  alias {
    name                   = var.primary_alb_dns
    zone_id                = var.primary_alb_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "secondary" {
  zone_id        = var.zone_id
  name           = var.domain
  type           = "A"
  set_identifier = "secondary"

  failover_routing_policy {
    type = "SECONDARY"
  }

  alias {
    name                   = var.dr_alb_dns
    zone_id                = var.dr_alb_zone_id
    evaluate_target_health = true
  }
}

# S3 with cross-region replication needs versioning on both buckets.
resource "aws_s3_bucket" "assets" {
  bucket = "myapp-assets-primary"
}
resource "aws_s3_bucket" "assets_dr" {
  provider = aws.dr
  bucket   = "myapp-assets-dr"
}
resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_versioning" "assets_dr" {
  provider = aws.dr
  bucket   = aws_s3_bucket.assets_dr.id
  versioning_configuration { status = "Enabled" }
}

data "aws_iam_policy_document" "s3_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "replication" {
  name               = "s3-crr-role"
  assume_role_policy = data.aws_iam_policy_document.s3_assume.json
}
data "aws_iam_policy_document" "replication" {
  statement {
    actions   = ["s3:GetReplicationConfiguration", "s3:ListBucket"]
    resources = [aws_s3_bucket.assets.arn]
  }
  statement {
    actions   = ["s3:GetObjectVersionForReplication", "s3:GetObjectVersionAcl", "s3:GetObjectVersionTagging"]
    resources = ["${aws_s3_bucket.assets.arn}/*"]
  }
  statement {
    actions   = ["s3:ReplicateObject", "s3:ReplicateDelete", "s3:ReplicateTags"]
    resources = ["${aws_s3_bucket.assets_dr.arn}/*"]
  }
}
resource "aws_iam_role_policy" "replication" {
  role   = aws_iam_role.replication.id
  policy = data.aws_iam_policy_document.replication.json
}

resource "aws_s3_bucket_replication_configuration" "assets" {
  depends_on = [aws_s3_bucket_versioning.assets, aws_s3_bucket_versioning.assets_dr]
  role       = aws_iam_role.replication.arn
  bucket     = aws_s3_bucket.assets.id

  rule {
    id     = "all"
    status = "Enabled"
    filter {}
    delete_marker_replication { status = "Enabled" }
    destination {
      bucket = aws_s3_bucket.assets_dr.arn
    }
  }
}
