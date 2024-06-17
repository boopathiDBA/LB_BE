# Create a lambda target group resource
# ---------------------------------------------

resource "aws_lambda_permission" "search_offer_update_aws_lambda_permission" {
  statement_id  = "AllowExecutionFromlb"
  action        = "lambda:InvokeFunction"
  function_name = module.search_offer_update.lambda_function_name
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = aws_lb_target_group.search_offer_update_target_group.arn
}

resource "aws_lb_target_group" "search_offer_update_target_group" {
  name        = "${var.environment}-search-offer-update"
  target_type = "lambda"
}

resource "aws_lb_target_group_attachment" "search_offer_update_target_group_attachment" {
  target_group_arn = aws_lb_target_group.search_offer_update_target_group.arn
  target_id        = module.search_offer_update.lambda_function_arn
  depends_on       = [aws_lambda_permission.search_offer_update_aws_lambda_permission]
}

resource "aws_lb_listener_rule" "search_offer_update_aws_alb_listener" {

  listener_arn = aws_alb_listener.web-https.arn

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.search_offer_update_target_group.arn
  }

  condition {
    host_header {
      values = concat(var.subject_alternative_names, [var.cache_domain_name])
    }
  }

  condition {
    path_pattern {
      values = ["/offer/update"]
    }
  }

  tags = local.common_tags
}
