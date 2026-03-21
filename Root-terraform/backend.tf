terraform {
  backend "s3" {
    bucket         = "paolo-zafra-terraform-state"
    key            = "cloud-resume-challenge/terraform.tfstate"
    region         = "ap-southeast-2"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}