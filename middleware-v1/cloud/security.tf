# Public Security group
# -----------------------------------------------------
resource "aws_security_group" "main" {
  name        = "${var.environment}-main-sg"
  description = "Allow access to main"
  vpc_id      = module.main-network.vpc_id

  tags = local.common_tags
}

resource "aws_security_group_rule" "main-ingress" {
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = -1
  cidr_blocks       = [var.vpc_base_cidr_block]
  security_group_id = aws_security_group.main.id
  description       = "Allow access ingress access"
}

resource "aws_security_group_rule" "main-ingress-443" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.main.id
  description       = "Allow access ingress access"
}

resource "aws_security_group_rule" "main-ingress-80" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.main.id
  description       = "Allow access ingress access"
}

resource "aws_security_group_rule" "main-egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = -1
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.main.id
  description       = "Allow access egress access"
}

# Private Security group
# -----------------------------------------------------
resource "aws_security_group" "main-private" {
  name        = "${var.environment}-main-private-sg"
  description = "Allow access to main"
  vpc_id      = module.main-network.vpc_id

  tags = local.common_tags
}

resource "aws_security_group_rule" "main-public-egress" {
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = -1
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.main-private.id
  description       = "Allow access egress access"
}

resource "aws_security_group_rule" "main-private-egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = -1
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.main-private.id
  description       = "Allow access egress access"
}
