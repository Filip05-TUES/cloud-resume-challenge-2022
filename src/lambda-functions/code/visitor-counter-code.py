import json
import os
import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "VisitorCounterDB")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def _get_method(event):
    try:
        return event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
    except Exception:
        return "GET"

def _text_response(status, text_body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "text/plain",
            "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "'Content-Type'"
        },
        "body": str(text_body)
    }

def lambda_handler(event, context):
    method = _get_method(event) or "GET"
    try:
        if method == "POST":
            res = table.update_item(
                Key={"Id": "visitor_count"},
                UpdateExpression="SET #c = if_not_exists(#c, :start) + :inc",
                ExpressionAttributeNames={"#c": "count"},
                ExpressionAttributeValues={":inc": 1, ":start": 0},
                ReturnValues="UPDATED_NEW"
            )
            count = res.get("Attributes", {}).get("count", 0)
            return _text_response(200, count)
        else:
            res = table.get_item(Key={"Id": "visitor_count"})
            if "Item" not in res:
                table.put_item(Item={"Id": "visitor_count", "count": 0})
                count = 0
            else:
                count = res["Item"].get("count", 0)
            return _text_response(200, count)
    except Exception as e:
        print("Error:", str(e))
        return _text_response(500, 0)