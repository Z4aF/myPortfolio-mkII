Portfolio ON, WAF ON

terraform apply -var="enable_waf=true"

Portfolio OFF (your cost-saving mode)

terraform apply -var="enable_distribution=false"
