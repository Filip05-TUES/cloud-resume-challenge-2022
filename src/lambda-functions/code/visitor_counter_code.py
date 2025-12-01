import os
import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "VisitorCounterDB")
DYNAMODB = boto3.resource("dynamodb")
TABLE = DYNAMODB.Table(TABLE_NAME)

def _get_allowed_origin():
    return os.environ.get("ALLOWED_ORIGIN", "*")

def _get_method(event):
    try:
        method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
        return method if method else "GET"
    except Exception:
        return "GET"

def _text_response(status, text_body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "text/plain",
            "Access-Control-Allow-Origin": _get_allowed_origin(),
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "'Content-Type'"
        },
        "body": str(text_body)
    }

def lambda_handler(event, context):
    method = _get_method(event)

    try:
        if method == "POST":
            res = TABLE.update_item(
                Key={"Id": "visitor_count"},
                UpdateExpression="SET #c = if_not_exists(#c, :start) + :inc",
                ExpressionAttributeNames={"#c": "count"},
                ExpressionAttributeValues={":inc": 1, ":start": 0},
                ReturnValues="UPDATED_NEW"
            )
            count = res.get("Attributes", {}).get("count", 0)
            return _text_response(200, count)

        elif method == "OPTIONS":
            return _text_response(200, "")

        else:
            res = TABLE.get_item(Key={"Id": "visitor_count"})

            if "Item" not in res:
                count = 0
            else:
                count = res["Item"].get("count", 0)
            
            return _text_response(200, count)
            
    except Exception as e:
        print("Error:", str(e))
        return _text_response(500, 0)