# Create a variable with default values
# --------------------------------------

variable "main" {
  default = {
    SERP_API_KEY = "PLEASE_UPDATE_ME_MANUALLY_ON_AWS"
  }

  type = map(string)
}

# Populate secret with variable
# --------------------------------------

resource "aws_secretsmanager_secret_version" "main" {
  secret_id     = aws_secretsmanager_secret.main.id
  secret_string = jsonencode(var.main)

  lifecycle {
    ignore_changes = [
      secret_string,
    ]
  }
}

# Create secrets
# --------------------------------------

resource "aws_secretsmanager_secret" "main" {
  name = var.environment == "pprod" ? "/${var.environment}/search-services-a" : "/${var.environment}/search-services"
  tags = local.common_tags
}
