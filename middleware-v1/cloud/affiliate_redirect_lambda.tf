module "affiliate_redirect" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "4.7.1"

  function_name = "${var.environment}-be-affiliate-redirect-service"
  description   = "Evaluates the affiliate url and redirects the request"
  handler       = "app.delivery.rest.affiliate.redirect.handler"
  runtime       = "python3.8"
  publish       = true
  timeout       = 60
  hash_extra    = "middleware-affiliate-redirect"

  source_path = [
    {
      path = "${path.module}/../",
      patterns = [
        "!.*/*",
        "app/.+",
      ]
    }
  ]

  vpc_subnet_ids         = module.main-network.private_subnets
  vpc_security_group_ids = [aws_security_group.main-private.id]
  attach_network_policy  = true

  policy        = aws_iam_policy.ecs_task_execution_iam_policy.arn
  attach_policy = true

  environment_variables = var.merge_external_vars
  attach_tracing_policy = true

  layers = [
    data.aws_lambda_layer_version.aws_lambda_layer.arn,
    var.python_aws_powertools,
    var.python_sentry_layer
  ]

  depends_on = [
    aws_iam_role_policy_attachment.ecs_task_execution_role
  ]

  tags = local.common_tags
}
