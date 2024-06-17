# Create a lambda target group resource
# ---------------------------------------------

resource "aws_lambda_permission" "price_history_aws_lambda_permission" {
  statement_id  = "AllowExecutionFromlb"
  action        = "lambda:InvokeFunction"
  function_name = module.price_history.lambda_function_name
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = aws_lb_target_group.price_history_target_group.arn
  qualifier     = aws_lambda_alias.price_history_alias.name
}

resource "aws_lambda_alias" "price_history_alias" {
  name             = "provisioned"
  function_name    = module.price_history.lambda_function_name
  function_version = module.price_history.lambda_function_version
}

resource "aws_lambda_provisioned_concurrency_config" "price_history_provisioned_concurrency" {
  function_name                     = module.price_history.lambda_function_name
  provisioned_concurrent_executions = 5
  qualifier                         = aws_lambda_alias.price_history_alias.name
}

resource "aws_lb_target_group" "price_history_target_group" {
  name        = "${var.environment}-price-history"
  target_type = "lambda"
}


resource "aws_lb_target_group_attachment" "price_history_target_group_attachment" {
  target_group_arn = aws_lb_target_group.price_history_target_group.arn
  target_id        = aws_lambda_alias.price_history_alias.arn
  depends_on       = [aws_lambda_permission.price_history_aws_lambda_permission]
}

resource "aws_lb_listener_rule" "price_history_aws_alb_listener" {

  listener_arn = aws_alb_listener.web-https.arn

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.price_history_target_group.arn
  }

  condition {
    host_header {
      values = concat(var.subject_alternative_names, [var.cache_domain_name])
    }
  }

  condition {
    path_pattern {
      values = ["/offer/price_history"]
    }
  }

  condition {
    query_string {
      value = "id=*"
    }
  }

  tags = local.common_tags
}
