## Create a lambda target group resource
## ---------------------------------------------
#
#resource "aws_lambda_permission" "main" {
#  statement_id  = "AllowExecutionFromlb"
#  action        = "lambda:InvokeFunction"
#  function_name = module.merge.lambda_function_name
#  principal     = "elasticloadbalancing.amazonaws.com"
#  source_arn    = aws_lb_target_group.merge.arn
#}
#
#resource "aws_lb_target_group" "merge" {
#  name        = "${var.environment}-merge"
#  target_type = "lambda"
#}
#
#resource "aws_lb_target_group_attachment" "main" {
#  target_group_arn = aws_lb_target_group.merge.arn
#  target_id        = module.merge.lambda_function_arn
#  depends_on       = [aws_lambda_permission.main]
#}
#
#resource "aws_lb_listener_rule" "main" {
#
#  listener_arn = aws_alb_listener.web-https.arn
#
#  action {
#    type             = "forward"
#    target_group_arn = aws_lb_target_group.merge.arn
#  }
#
#  condition {
#    host_header {
#      values = concat(var.subject_alternative_names, [var.cache_domain_name])
#    }
#  }
#
#  condition {
#    path_pattern {
#      values = ["/offer/ext*", "/offer/update", "/offer/parse-detail"]
#    }
#  }
#
#  tags = local.common_tags
#}
