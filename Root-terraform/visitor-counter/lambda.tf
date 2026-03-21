data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/visitor-counter/lambdas"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "counter" {
  function_name    = "resume-visitor-counter"
  runtime          = "python3.11"
  handler          = "counter.lambda_handler"
  role             = aws_iam_role.lambda_role.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.counter.name
    }
  }
}

resource "aws_lambda_function" "admin_visitors" {
  function_name    = "resume-admin-visitors"
  runtime          = "python3.11"
  handler          = "admin_visitors.lambda_handler"
  role             = aws_iam_role.lambda_role.arn
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}