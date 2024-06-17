# WAF attached to CLOUDFRONT
# ----------------------------------------------

module "browser-extension-cache" {

  providers = {
    aws = aws.cloudfront
  }

  source  = "umotif-public/waf-webaclv2/aws"
  version = "~> 5.1.2"

  name_prefix = "${var.environment}-browser-extension-cache"
  scope       = "CLOUDFRONT"

  create_alb_association = false

  # create_logging_configuration = true
  # log_destination_configs      = [module.mod-common.blue_waf_logs_cf_kinesis_firehose_delivery_stream]

  allow_default_action = true

  visibility_config = {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.environment}-browser-extension-cache-waf-cf-setup-main-metrics"
    sampled_requests_enabled   = true
  }

  rules = [
    {
      name     = "${var.environment}-browser-extension-cache-aws-managed-rules-common-rule-set"
      priority = "1"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-cache-aws-managed-rules-common-rule-set-metrics"
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
      name     = "${var.environment}-browser-extension-cache-aws-managed-rules-known-bad-input-rule-set"
      priority = "2"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-cache-aws-managed-rules-known-bad-input-rule-set-metrics"
        sampled_requests_enabled   = true
      }

      managed_rule_group_statement = {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    },
    {
      name     = "${var.environment}-browser-extension-cache-aws-managed-rules-linux-rule-set"
      priority = "3"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-cache-aws-managed-rules-linux-rule-set-metrics"
        sampled_requests_enabled   = true
      }

      managed_rule_group_statement = {
        name        = "AWSManagedRulesLinuxRuleSet"
        vendor_name = "AWS"
      }
    },
    {
      name     = "${var.environment}-browser-extension-cache-aws-managed-rules-sql-rule-set"
      priority = "4"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-cache-aws-managed-rules-sql-rule-set-metrics"
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
      name     = "${var.environment}-browser-extension-cache-aws-managed-rules-bot-control-rule-set"
      priority = "5"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-cache-aws-managed-rules-bot-control-rule-set-metrics"
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
      name     = "${var.environment}-browser-extension-cache-aws-managed-rules-ip-reputation-list-rule-set"
      priority = "6"

      override_action = var.enable_waf == true ? "none" : "count"

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "${var.environment}-browser-extension-cache-aws-managed-rules-ip-reputation-list-rule-set-metrics"
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
