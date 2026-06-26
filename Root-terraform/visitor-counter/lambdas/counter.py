import json
import boto3
import hashlib
import time

COOLDOWN = 24 * 60 * 60  # 24 hours in seconds


def get_dynamodb():
    return boto3.resource("dynamodb")


def get_visitors_table():
    return get_dynamodb().Table("resume-visitors")


def hash_ip(ip):
    return hashlib.sha256(ip.encode()).hexdigest()


def lambda_handler(event, context):

    allowed_origins = [
        "https://pdzaf.site",
        "https://www.pdzaf.site",
    ]

    origin = event.get("headers", {}).get("origin", "")

    if origin in allowed_origins:
        cors_origin = origin
    else:
        cors_origin = "https://pdzaf.site"


    visitors_table = get_visitors_table()

    headers = event.get("headers", {}) or {}
    visitor_id = headers.get("x-visitor-id") or headers.get("X-Visitor-Id")

    if not visitor_id:
        visitor_id = hash_ip(event["requestContext"]["identity"]["sourceIp"])

    now = int(time.time())
    existing = visitors_table.get_item(Key={"visitor_id": visitor_id})

    increment = False

    if "Item" not in existing:
        increment = True

        visitors_table.put_item(
            Item={
                "visitor_id": visitor_id,
                "first_visit": now,
                "last_seen": now,
                "last_counted_at": now,
                "hit_count": 1,
                "counted_visit_count": 1
            }
        )
    else:
        item = existing["Item"]
        last_counted = item.get("last_counted_at", 0)

        # always update hits
        visitors_table.update_item(
            Key={"visitor_id": visitor_id},
            UpdateExpression="SET last_seen = :t ADD hit_count :inc",
            ExpressionAttributeValues={
                ":t": now,
                ":inc": 1
            }
        )

        if now - last_counted > COOLDOWN:
            increment = True

            visitors_table.update_item(
                Key={"visitor_id": visitor_id},
                UpdateExpression="""
                    SET last_counted_at = :t
                    ADD counted_visit_count :inc
                """,
                ExpressionAttributeValues={
                    ":t": now,
                    ":inc": 1
                }
            )

    #
    items = []
    response = visitors_table.scan(
        ProjectionExpression="counted_visit_count"
    )
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = visitors_table.scan(
            ProjectionExpression="counted_visit_count",
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))

    total = sum(
        int(item.get("counted_visit_count", 0))
        for item in items
    )

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Headers": "Content-Type,X-Visitor-Id",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"
        },
        "body": json.dumps({
            "count": total
        })
    }