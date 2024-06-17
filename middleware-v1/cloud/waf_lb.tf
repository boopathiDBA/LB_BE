# WAF attached to CLOUDFRONT
# ----------------------------------------------

resource "aws_s3_bucket" "waf" {
  bucket = "${var.environment}-aws-waf-firehose-stream-be-alb-bucket"
}

resource "aws_s3_bucket_acl" "waf" {
  bucket = aws_s3_bucket.waf.id
  acl    = "private"
}

resource "aws_iam_role" "firehose" {
  name = "${var.environment}-firehose-stream-be-alb-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "firehose.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "custom-policy" {
  name   = "${var.environment}-firehose-bw-alb-role-custom-policy"
  role   = aws_iam_role.firehose.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Action": [
        "s3:AbortMultipartUpload",
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:ListBucketMultipartUploads",
        "s3:PutObject"
      ],
      "Resource": [
        "${aws_s3_bucket.waf.arn}",
        "${aws_s3_bucket.waf.arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "iam:CreateServiceLinkedRole",
      "Resource": "arn:aws:iam::*:role/aws-service-role/wafv2.amazonaws.com/AWSServiceRoleForWAFV2Logging"
    }
  ]
}
EOF
}

resource "aws_kinesis_firehose_delivery_stream" "waf" {
  name        = "aws-waf-logs-kinesis-firehose-be-alb-stream-${var.environment}"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.waf.arn
  }
}

module "browser-extension-lb" {

  source  = "umotif-public/waf-webaclv2/aws"
  version = "~> 5.1.2"

  name_prefix = "${var.environment}-browser-extension-lb"
  scope       = "REGIONAL"

  create_alb_association = true
  alb_arn                = aws_alb.main.arn

  create_logging_configuration = true
  log_destination_configs      = [aws_kinesis_firehose_delivery_stream.waf.arn]

  allow_default_action = true

  visibility_config = {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.environment}-browser-extension-lb-waf-cf-setup-main-metrics"
    sampled_requests_enabled   = true
  }

  rules = [
    {
      name     = "${var.environment}-browser-extension-lb-aws-managed-rules-common-rule-set"
      priority = "1"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-lb-aws-managed-rules-common-rule-set-metrics"
        sampled_requests_enabled   = true
      }

      managed_rule_group_statement = {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
        excluded_rule = [
          "SizeRestrictions_BODY",
          "GenericRFI_BODY",
          "CrossSiteScripting_BODY",
          "GenericRFI_QUERYARGUMENTS",
          "EC2MetaDataSSRF_COOKIE"
        ]
      }
    },
    {
      name     = "${var.environment}-browser-extension-lb-aws-managed-rules-known-bad-input-rule-set"
      priority = "2"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-lb-aws-managed-rules-known-bad-input-rule-set-metrics"
        sampled_requests_enabled   = true
      }

      managed_rule_group_statement = {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    },
    {
      name     = "${var.environment}-browser-extension-lb-aws-managed-rules-linux-rule-set"
      priority = "3"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-lb-aws-managed-rules-linux-rule-set-metrics"
        sampled_requests_enabled   = true
      }

      managed_rule_group_statement = {
        name        = "AWSManagedRulesLinuxRuleSet"
        vendor_name = "AWS"
      }
    },
    {
      name     = "${var.environment}-browser-extension-lb-aws-managed-rules-sql-rule-set"
      priority = "4"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-lb-aws-managed-rules-sql-rule-set-metrics"
        sampled_requests_enabled   = true
      }

      managed_rule_group_statement = {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
        excluded_rule = [
          "SQLi_BODY"
        ]
      }
    },
    {
      name     = "${var.environment}-browser-extension-lb-aws-managed-rules-bot-control-rule-set"
      priority = "5"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-lb-aws-managed-rules-bot-control-rule-set-metrics"
        sampled_requests_enabled   = true
      }

      managed_rule_group_statement = {
        name        = "AWSManagedRulesBotControlRuleSet"
        vendor_name = "AWS"
        excluded_rule = [
          "CategoryAdvertising",
          "CategoryContentFetcher",
          "CategorySearchEngine",
          "CategorySeo",
          "CategorySocialMedia",
          "CategoryHttpLibrary",
          "SignalNonBrowserUserAgent"
        ]
      }
    },
    {
      name     = "${var.environment}-browser-extension-lb-aws-managed-rules-ip-reputation-list-rule-set"
      priority = "6"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-lb-aws-managed-rules-ip-reputation-list-rule-set-metrics"
        sampled_requests_enabled   = true
      }

      managed_rule_group_statement = {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }
  ]

  tags = local.common_tags
}
