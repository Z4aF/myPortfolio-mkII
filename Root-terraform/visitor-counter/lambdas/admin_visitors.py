import json
import boto3


def get_dynamodb():
    return boto3.resource("dynamodb")


def get_visitors_table():
    return get_dynamodb().Table("resume-visitors")


def lambda_handler(event, context):
    visitors_table = get_visitors_table()

    try:
        items = []
        response = visitors_table.scan()

        items.extend(response.get("Items", []))

        while "LastEvaluatedKey" in response:
            response = visitors_table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            items.extend(response.get("Items", []))

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