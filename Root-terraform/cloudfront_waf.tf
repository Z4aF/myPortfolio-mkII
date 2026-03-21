resource "aws_wafv2_web_acl" "resume" {
  provider = aws.us_east_1
  count    = (var.enable_distribution && var.enable_waf) ? 1 : 0
  name     = "resume-waf"
  scope    = "CLOUDFRONT"

  default_action {
    allow {}
  }

  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = "resumeWAF"
    sampled_requests_enabled   = false
  }
}

