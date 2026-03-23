resource "aws_dynamodb_table" "counter" {
  name         = "resume-visitor-counter"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Project = "CloudResumeChallenge"
    Owner   = "Paolo"
  } 
}

resource "aws_dynamodb_table" "visitors" {
  name         = "resume-visitors"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "visitor_id"

  attribute {
    name = "visitor_id"
    type = "S"
  }
}
