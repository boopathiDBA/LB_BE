# HTTPS ALB listener
# --------------------------------------

resource "aws_alb_listener" "web-https" {
  depends_on        = [aws_alb.main]
  load_balancer_arn = aws_alb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = module.acm.this_acm_certificate_arn

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
      host        = "littlebirdie.com.au"
    }
  }

  tags = local.common_tags
}

resource "aws_alb_listener" "web-http" {
  depends_on        = [aws_alb.main]
  load_balancer_arn = aws_alb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = local.common_tags
}

resource "aws_lb_listener" "main-internal-443" {
  depends_on        = [aws_alb.main-internal]
  load_balancer_arn = aws_alb.main-internal.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = module.acm.this_acm_certificate_arn

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
      host        = "littlebirdie.com.au"
    }
  }

  tags = local.common_tags
}

resource "aws_lb_listener" "main-internal-80" {
  depends_on        = [aws_alb.main-internal]
  load_balancer_arn = aws_alb.main-internal.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = local.common_tags
}

# HTTP ALB
# --------------------------------------

resource "aws_alb" "main" {
  name            = "${var.environment}-main-alb-2"
  internal        = false
  subnets         = module.main-network.public_subnets
  security_groups = [aws_security_group.main.id]

  tags = local.common_tags
}

resource "aws_alb" "main-internal" {
  name            = "${var.environment}-main-alb-1"
  internal        = true
  subnets         = module.main-network.private_subnets
  security_groups = [aws_security_group.main.id]

  tags = local.common_tags
}
