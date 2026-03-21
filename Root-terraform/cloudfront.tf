resource "aws_cloudfront_origin_access_control" "oac" {
  name                              = "resume-site-oac"
  description                       = "OAC for resume site"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "resume" {
  enabled             = var.enable_distribution
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.resume.bucket_regional_domain_name
    origin_id   = "s3-resume-origin"

    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
  }

  default_cache_behavior {
    target_origin_id       = "s3-resume-origin"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD"]
    cached_methods  = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  web_acl_id = (var.enable_distribution && var.enable_waf
    ? aws_wafv2_web_acl.resume[0].arn
    : null
  )

  lifecycle {
    prevent_destroy = true
  }
}



