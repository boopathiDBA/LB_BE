#module "merge" {
#  source  = "terraform-aws-modules/lambda/aws"
#  version = "4.7.1"
#
#  function_name = "${var.environment}-be-search-service"
#  description   = "Searches OpenSearch and Google for matching offers"
#  handler       = "app.delivery.rest.handler"
#  runtime       = "python3.8"
#  publish       = true
#  timeout       = 60
#  memory_size   = 512
#  hash_extra    = "middleware-merge"
#
#  source_path = [
#    {
#      path = "${path.module}/../",
#      patterns = [
#        "!.*/*",
#        "app/.+",
#      ]
#    }
#  ]
#
#  vpc_subnet_ids         = module.main-network.private_subnets
#  vpc_security_group_ids = [aws_security_group.main-private.id]
#  attach_network_policy  = true
#
#  policy        = aws_iam_policy.ecs_task_execution_iam_policy.arn
#  attach_policy = true
#
#  environment_variables = var.merge_external_vars
#  attach_tracing_policy = true
#
#  layers = [
#    data.aws_lambda_layer_version.aws_lambda_layer.arn,
#    var.python_aws_powertools,
#    var.python_sentry_layer
#  ]
#
#  depends_on = [
#    aws_iam_role_policy_attachment.ecs_task_execution_role
#  ]
#
#  tags = local.common_tags
#}
