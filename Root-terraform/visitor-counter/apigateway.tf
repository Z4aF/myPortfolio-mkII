resource "aws_apigatewayv2_api" "counter_api" {
  name          = "visitor-counter-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["https://d177m2z4znivqh.cloudfront.net"]
    allow_methods = ["GET"]
    allow_headers = ["content-type", "x-visitor-id"]
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.counter_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.counter.invoke_arn
}

resource "aws_apigatewayv2_route" "counter" {
  api_id    = aws_apigatewayv2_api.counter_api.id
  route_key = "GET /count"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.counter_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.counter.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.counter_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "admin_visitors" {
  api_id           = aws_apigatewayv2_api.counter_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.admin_visitors.invoke_arn
}

resource "aws_apigatewayv2_route" "admin_visitors" {
  api_id    = aws_apigatewayv2_api.counter_api.id
  route_key = "GET /admin/visitors"
  target    = "integrations/${aws_apigatewayv2_integration.admin_visitors.id}"
}

resource "aws_lambda_permission" "apigw_admin_visitors" {
  statement_id  = "AllowAPIGatewayInvokeAdminVisitors"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.admin_visitors.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.counter_api.execution_arn}/*/*"
}
