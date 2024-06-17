terraform {
  required_version = "= 1.3.6"


  backend "s3" {
    bucket       = "littlebirdie-git-private-runners"
    key          = "platform/search-service/terraform.tfstate"
    encrypt      = true
    region       = "ap-southeast-2"
    session_name = "search-service"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5"
    }
  }
}

provider "aws" {
  region = "ap-southeast-2"
}

provider "aws" {
  alias  = "cloudfront"
  region = "us-east-1"
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_route53_zone" "public" {
  name         = var.domain_name
  private_zone = false
}

data "aws_ec2_transit_gateway" "main" {
  filter {
    name   = "state"
    values = ["available"]
  }
}

data "aws_lambda_layer_version" "aws_lambda_layer" {
  layer_name = "${var.environment}-browser-extension-layer-3-8"
}

data "aws_cloudfront_cache_policy" "Managed-CachingOptimized" {
  name = "Managed-CachingOptimized"
}

data "aws_cloudfront_origin_request_policy" "Managed-AllViewer" {
  name = "Managed-AllViewer"
}

data "aws_cloudfront_response_headers_policy" "Managed-CORS-with-preflight-and-SecurityHeadersPolicy" {
  name = "Managed-CORS-with-preflight-and-SecurityHeadersPolicy"
}

data "aws_canonical_user_id" "current" {}
