output "visitor_counter_api_url" {
  value = "${aws_apigatewayv2_api.counter_api.api_endpoint}/count"
}
