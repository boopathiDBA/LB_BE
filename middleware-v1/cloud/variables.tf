# Declare tags to be applied on every resource
# ---------------------------------------------------
locals {
  common_tags = {
    Environment         = var.environment
    Maintainer_Software = "Terraform"
    Revision            = "master"
    Project             = "https://github.com/little-birdie/middleware-v1.git"
    team                = "Core Platform"
    service_name        = "search-service"
  }

}

# Declare here the common variables
#----------------------------------
variable "environment" {
  default = "uat"
}

variable "aws_region" {
  default = "ap-southeast-2"
}

variable "customer_gateway_asn" {
  default = "65000"
}

variable "customer_gateway_ip" {
  default = "202.142.49.122"
}

variable "vpc_base_cidr_block" {
  default = null
}

variable "destination_cidr_block" {
  default     = ""
  description = "CIDR to connect transit gateway"
}

variable "aladdin_cidr_block" {
  default     = ""
  description = "CIDR to connect transit gateway"
}

variable "root_cidr_block" {
  default     = ""
  description = "CIDR to connect transit gateway"
}

variable "vpn_cidr_block" {
  default     = "192.168.114.0/24"
  description = "VPN CIDR to connect transit gateway"
}

variable "b2b_cidr_block" {
  default     = ""
  description = "CIDR to connect to open search and applications from the b2b network"
}

variable "domain_name" {
  default = null
}

variable "cache_domain_name" {
  default = null
}

variable "subject_alternative_names" {
  type = list(any)
}

variable "deployment_profile" {
  type    = any
  default = "development"
}

variable "merge_external_vars" {
  type    = map(any)
  default = {}
}

variable "enable_waf" {
  type    = bool
  default = false
}

variable "python_aws_powertools" {
  type    = any
  default = "arn:aws:lambda:ap-southeast-2:017000801446:layer:AWSLambdaPowertoolsPythonV2:18"
}

variable "python_sentry_layer" {
  type    = any
  default = "arn:aws:lambda:ap-southeast-2:943013980633:layer:SentryPythonServerlessSDK:47"
}

variable "cloudwatch_log_pattern" {
  type        = string
  description = "The awslogs-multiline-pattern option defines a multiline start pattern using a regular expression. A log message consists of a line that matches the pattern and any following lines that don’t match the pattern. Thus the matched line is the delimiter between log messages."
  default     = "([0-9]{4})-([0-1][0-9])-([0-3][0-9])T([0-2][0-9]):([0-5][0-9]):([0-5][0-9])\\\\.([0-9]{3})[+-][0-1][0-9]{3}"
}
