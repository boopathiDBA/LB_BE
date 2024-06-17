# S3 bucket used to logs of the CF s3 bucket
# ---------------------------------------------------

module "cloudfront_log_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket        = "${var.environment}-browser-extension-cache-s3-logs"
  acl           = null # conflicts with default of `acl = "private"` so set to null to use grants
  force_destroy = true

  # S3 bucket-level Public Access Block configuration
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  tags = local.common_tags
}

# S3 ACL after provider update
# --------------------------------------------------

resource "aws_s3_bucket_acl" "cloudfront_log_bucket" {
  bucket = module.cloudfront_log_bucket.s3_bucket_id
  access_control_policy {
    grant {
      grantee {
        id   = data.aws_canonical_user_id.current.id
        type = "CanonicalUser"
      }
      permission = "FULL_CONTROL"
    }

    grant {
      grantee {
        id   = "c4c1ede66af53448b93c283ce9448c4ba468c9432aa01d700d3878632f77d2d0"
        type = "CanonicalUser"
      }
      permission = "FULL_CONTROL"
    }

    owner {
      id = data.aws_canonical_user_id.current.id
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "cloudfront_log_bucket" {
  bucket = module.cloudfront_log_bucket.s3_bucket_id

  rule {
    object_ownership = "ObjectWriter"
  }
}
