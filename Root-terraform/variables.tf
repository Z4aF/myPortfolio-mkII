variable "enable_distribution" {
  description = "Enable or disable the CloudFront distribution"
  type        = bool
  default     = true
}

variable "enable_waf" {
  description = "Enable WAF only when distribution is enabled"
  type        = bool
  default     = false
}
