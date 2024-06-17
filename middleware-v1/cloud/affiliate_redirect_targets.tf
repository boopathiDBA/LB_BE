# Create a lambda target group resource
# ---------------------------------------------

resource "aws_lambda_permission" "affiliate_redirect" {
  statement_id  = "AllowExecutionFromlb"
  action        = "lambda:InvokeFunction"
  function_name = module.affiliate_redirect.lambda_function_name
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = aws_lb_target_group.affiliate_redirect.arn
}

resource "aws_lb_target_group" "affiliate_redirect" {
  name        = "${var.environment}-affiliate-redirect"
  target_type = "lambda"
}

resource "aws_lb_target_group_attachment" "affiliate_redirect" {
  target_group_arn = aws_lb_target_group.affiliate_redirect.arn
  target_id        = module.affiliate_redirect.lambda_function_arn
  depends_on       = [aws_lambda_permission.affiliate_redirect]
}

resource "aws_lb_listener_rule" "affiliate_redirect" {

  listener_arn = aws_alb_listener.web-https.arn

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.affiliate_redirect.arn
  }

  condition {
    host_header {
      values = concat(var.subject_alternative_names, [var.cache_domain_name])
    }
  }

  condition {
    path_pattern {
      values = ["/affiliate/redirect"]
    }
  }

  condition {
    query_string {
      value = "offer_url=*"
    }
  }

  tags = local.common_tags
}
