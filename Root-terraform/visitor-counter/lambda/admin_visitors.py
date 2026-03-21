import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
visitors_table = dynamodb.Table("resume-visitors")


def lambda_handler(event, context):
    try:
        items = []
        response = visitors_table.scan()

        items.extend(response.get("Items", []))

        while "LastEvaluatedKey" in response:
            response = visitors_table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            items.extend(response.get("Items", []))

        # Normalize numeric fields
        for item in items:
            item["first_visit"] = int(item.get("first_visit", 0))
            item["last_visit"] = int(item.get("last_visit", 0))
            item["visit_count"] = int(item.get("visit_count", 0))

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "https://d177m2z4znivqh.cloudfront.net",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
            },
            "body": json.dumps({
                "visitors": items
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "https://d177m2z4znivqh.cloudfront.net"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }