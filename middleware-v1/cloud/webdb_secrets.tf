# Create a variable with default values
# --------------------------------------

variable "webdb_secret" {
  default = {
    host = "localhost"
    username = "postgres"
    password = "postgres"
    dbname = "postgres"
    port = "5432"
}

  type = map(string)
}

# Populate secret with variable
# --------------------------------------

resource "aws_secretsmanager_secret_version" "webdb_secret" {
  secret_id     = aws_secretsmanager_secret.webdb_secret.id
  secret_string = jsonencode(var.webdb_secret)

  lifecycle {
    ignore_changes = [
      secret_string,
    ]
  }
}

# Create secrets
# --------------------------------------

resource "aws_secretsmanager_secret" "webdb_secret" {
  name = "/${var.environment}/webdb/postgres"
  tags = local.common_tags
}
