# Cloud Resume Challenge – Visitor Counter Portfolio

This project is my implementation of the Cloud Resume Challenge with extra features beyond the basic requirements.

It includes:

- a portfolio frontend hosted on AWS
- a visitor counter powered by API Gateway, Lambda, and DynamoDB
- a visitor analytics admin dashboard
- Terraform for infrastructure as code
- CloudFront distribution
- optional WAF protection

## Features

### Public portfolio site
- Responsive portfolio frontend
- Background video sections
- Visitor counter displayed on the site
- Unique visitor tracking using browser-generated visitor IDs
- Fallback hashed-IP logic when no visitor ID is provided

### Visitor counter backend
- AWS Lambda function for counting visitors
- API Gateway HTTP API endpoint
- DynamoDB table for total visitor count
- DynamoDB table for visitor records
- 24-hour cooldown logic for unique visitor counting

### Admin dashboard
- Hidden admin page accessed from the lambda symbol in the site branding
- Displays:
  - total unique visitors
  - total logged visits
  - repeat visitors
  - latest visit
  - visitor records table
- Uses the same visual theme as the main portfolio

### Infrastructure
- Terraform-managed AWS resources
- S3 for static hosting
- CloudFront for content delivery
- API Gateway for backend endpoints
- Lambda for backend logic
- DynamoDB for persistence

## Architecture

Frontend:
- HTML
- CSS
- JavaScript
- S3
- CloudFront

Backend:
- API Gateway
- Lambda
- DynamoDB

Infrastructure:
- Terraform

## Project Structure

```text
.
├── frontend/
│   ├── index.html
│   ├── admin.html
│   ├── style.css
│   └── assets/
│
├── backend/
│    ├── cloudfront.tf
│    ├── cloudfront_waf.tf
│    ├── s3.tf
│    ├── provider.tf
│    ├── variables.tf
│    ├── outputs.tf
│    └── README.md
│   ├── visitor-counter/
│   │   ├── lambda/
│   │   │   ├── counter.py
│   │   │   └── admin_visitors.py
│   │   ├── apigateway.tf
│   │   ├── dynamodb.tf
│   │   ├── iam.tf
│   │   ├── lambda.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
