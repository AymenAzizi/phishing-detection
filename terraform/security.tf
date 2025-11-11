# Infrastructure as Code Security Configuration
# Secure infrastructure setup for phishing detection system

# Security Group for API Server
resource "aws_security_group" "phishing_detection_api" {
  name_prefix = "phishing-detection-api-"
  description = "Security group for phishing detection API"
  vpc_id      = var.vpc_id

  # Allow HTTPS traffic
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS traffic"
  }

  # Allow HTTP traffic (redirect to HTTPS)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP traffic (redirect to HTTPS)"
  }

  # Allow internal communication
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Internal API communication"
  }

  # Allow database access
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "PostgreSQL database access"
  }

  # Allow Redis access
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Redis cache access"
  }

  # Outbound rules
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "phishing-detection-api-sg"
    Environment = var.environment
    Security    = "High"
    Compliance  = "SOC2"
  }
}

# Security Group for Database
resource "aws_security_group" "phishing_detection_db" {
  name_prefix = "phishing-detection-db-"
  description = "Security group for phishing detection database"
  vpc_id      = var.vpc_id

  # Allow PostgreSQL access from API servers only
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.phishing_detection_api.id]
    description     = "PostgreSQL access from API servers"
  }

  # No outbound rules (database doesn't need internet access)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "phishing-detection-db-sg"
    Environment = var.environment
    Security    = "Critical"
    Compliance  = "SOC2"
  }
}

# Security Group for Redis Cache
resource "aws_security_group" "phishing_detection_redis" {
  name_prefix = "phishing-detection-redis-"
  description = "Security group for Redis cache"
  vpc_id      = var.vpc_id

  # Allow Redis access from API servers only
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.phishing_detection_api.id]
    description     = "Redis access from API servers"
  }

  tags = {
    Name        = "phishing-detection-redis-sg"
    Environment = var.environment
    Security    = "High"
    Compliance  = "SOC2"
  }
}

# WAF Web ACL for API Protection
resource "aws_wafv2_web_acl" "phishing_detection_waf" {
  name  = "phishing-detection-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  # SQL Injection protection
  rule {
    name     = "SQLInjectionRule"
    priority = 2

    action {
      block {}
    }

    statement {
      sqli_match_statement {
        field_to_match {
          all_query_arguments {}
        }
        text_transformation {
          priority = 0
          type     = "URL_DECODE"
        }
        text_transformation {
          priority = 1
          type     = "HTML_ENTITY_DECODE"
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "SQLInjectionRule"
      sampled_requests_enabled   = true
    }
  }

  # XSS protection
  rule {
    name     = "XSSRule"
    priority = 3

    action {
      block {}
    }

    statement {
      xss_match_statement {
        field_to_match {
          all_query_arguments {}
        }
        text_transformation {
          priority = 0
          type     = "URL_DECODE"
        }
        text_transformation {
          priority = 1
          type     = "HTML_ENTITY_DECODE"
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "XSSRule"
      sampled_requests_enabled   = true
    }
  }

  # AWS managed rules
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 4

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # AWS managed SQL injection rules
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 5

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # AWS managed XSS rules
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 6

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  tags = {
    Name        = "phishing-detection-waf"
    Environment = var.environment
    Security    = "Critical"
    Compliance  = "SOC2"
  }
}

# KMS Key for encryption
resource "aws_kms_key" "phishing_detection_encryption" {
  description             = "KMS key for phishing detection system encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnEquals = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "phishing-detection-encryption-key"
    Environment = var.environment
    Security    = "Critical"
    Compliance  = "SOC2"
  }
}

resource "aws_kms_alias" "phishing_detection_encryption" {
  name          = "alias/phishing-detection-encryption"
  target_key_id = aws_kms_key.phishing_detection_encryption.key_id
}

# CloudTrail for audit logging
resource "aws_cloudtrail" "phishing_detection_audit" {
  name                          = "phishing-detection-audit-trail"
  s3_bucket_name                = aws_s3_bucket.audit_logs.bucket
  s3_key_prefix                 = "cloudtrail"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true

  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.audit_logs.arn}/*"]
    }
  }

  tags = {
    Name        = "phishing-detection-audit-trail"
    Environment = var.environment
    Security    = "Critical"
    Compliance  = "SOC2"
  }
}

# S3 Bucket for audit logs
resource "aws_s3_bucket" "audit_logs" {
  bucket        = "${var.project_name}-audit-logs-${random_id.bucket_suffix.hex}"
  force_destroy = false

  tags = {
    Name        = "phishing-detection-audit-logs"
    Environment = var.environment
    Security    = "Critical"
    Compliance  = "SOC2"
  }
}

resource "aws_s3_bucket_versioning" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.phishing_detection_encryption.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudWatch Log Groups with encryption
resource "aws_cloudwatch_log_group" "phishing_detection_api" {
  name              = "/aws/ecs/phishing-detection-api"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.phishing_detection_encryption.arn

  tags = {
    Name        = "phishing-detection-api-logs"
    Environment = var.environment
    Security    = "High"
    Compliance  = "SOC2"
  }
}

resource "aws_cloudwatch_log_group" "phishing_detection_security" {
  name              = "/aws/security/phishing-detection"
  retention_in_days = 90
  kms_key_id        = aws_kms_key.phishing_detection_encryption.arn

  tags = {
    Name        = "phishing-detection-security-logs"
    Environment = var.environment
    Security    = "Critical"
    Compliance  = "SOC2"
  }
}

# Security monitoring and alerting
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "phishing-detection-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ErrorCount"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors error rate"
  alarm_actions       = [aws_sns_topic.security_alerts.arn]

  tags = {
    Name        = "phishing-detection-high-error-rate"
    Environment = var.environment
    Security    = "High"
  }
}

resource "aws_cloudwatch_metric_alarm" "high_cpu_utilization" {
  alarm_name          = "phishing-detection-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors cpu utilization"
  alarm_actions       = [aws_sns_topic.security_alerts.arn]

  tags = {
    Name        = "phishing-detection-high-cpu"
    Environment = var.environment
    Security    = "Medium"
  }
}

# SNS Topic for security alerts
resource "aws_sns_topic" "security_alerts" {
  name              = "phishing-detection-security-alerts"
  kms_master_key_id = aws_kms_key.phishing_detection_encryption.arn

  tags = {
    Name        = "phishing-detection-security-alerts"
    Environment = var.environment
    Security    = "Critical"
    Compliance  = "SOC2"
  }
}

# Random ID for unique bucket names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Variables
variable "vpc_id" {
  description = "VPC ID for the security groups"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "phishing-detection"
}
