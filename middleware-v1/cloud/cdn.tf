# Creates cache policy
# ----------------------------------------------

resource "aws_cloudfront_cache_policy" "cdn" {
  name        = "${var.environment}-be-cache-policy"
  comment     = "Browser Extension Cache Policy"
  default_ttl = 3000
  max_ttl     = 3600
  min_ttl     = 1
  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "all"
    }
  }
}

# Creates Origin request policy
# ----------------------------------------------

resource "aws_cloudfront_origin_request_policy" "cdn" {
  name        = "${var.environment}-be-origin-policy"
  comment     = "Browser Extension Origin Request Policy"
  cookies_config {
    cookie_behavior = "none"
  }
  headers_config {
    header_behavior = "allViewer"
  }
  query_strings_config {
    query_string_behavior = "all"
  }
}

# Creates an AWS CloudFront distribution
# ----------------------------------------------

module "cdn" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "~> 3.2.0"

  aliases = [var.cache_domain_name]

  comment             = "Little Birdie Browser Extension Cache ${var.environment} environment"
  enabled             = true
  is_ipv6_enabled     = true
  price_class         = "PriceClass_All"
  retain_on_delete    = false
  wait_for_deployment = false
  default_root_object = "index.html"

  web_acl_id = module.browser-extension-cache.web_acl_arn

  create_origin_access_identity = true
  origin_access_identities = {
    alb_cache_one = "Cache alb one ${var.environment}"
  }

  logging_config = {
    bucket = module.cloudfront_log_bucket.s3_bucket_bucket_domain_name
  }

  origin = {
    cache-app-sync = {
      domain_name = aws_route53_record.www-live.name
      custom_origin_config = {
        http_port              = 80
        https_port             = 443
        origin_protocol_policy = "https-only"
        origin_ssl_protocols   = ["TLSv1.2"]
      }
    }
  }

  default_cache_behavior = {
    target_origin_id       = "cache-app-sync"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods          = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    compress                 = true
    query_string             = true
    use_forwarded_values     = false
    cache_policy_id          = aws_cloudfront_cache_policy.cdn.id
    origin_request_policy_id = aws_cloudfront_origin_request_policy.cdn.id
  }


  viewer_certificate = {
    acm_certificate_arn      = module.acma.this_acm_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  tags = local.common_tags
}

