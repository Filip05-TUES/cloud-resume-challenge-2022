import unittest
from unittest.mock import patch, MagicMock
import os
import visitor_counter_code

os.environ["TABLE_NAME"] = "MockVisitorCounterDB"
os.environ["ALLOWED_ORIGIN"] = "https://mock.resumecount.com"

@patch('visitor_counter_code.boto3')
class VisitorCounterTest(unittest.TestCase):
    def test_get_method_rest_api_v1(self, mock_boto3):
        event = {"httpMethod": "POST"}
        method = visitor_counter_code._get_method(event)
        self.assertEqual(method, "POST")

    def test_get_method_http_api_v2(self, mock_boto3):
        event = {"requestContext": {"http": {"method": "GET"}}}
        method = visitor_counter_code._get_method(event)
        self.assertEqual(method, "GET")

    def test_get_method_empty_event_defaults_to_get(self, mock_boto3):
        event = {}
        method = visitor_counter_code._get_method(event)
        self.assertEqual(method, "GET")

    def test_get_method_invalid_event_defaults_to_get(self, mock_boto3):
        event = {"some_key": 123}
        method = visitor_counter_code._get_method(event)
        self.assertEqual(method, "GET")

    def test_text_response_structure_and_cors(self, mock_boto3):
        response = visitor_counter_code._text_response(200, 42)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "42")
        self.assertEqual(response["headers"]["Content-Type"], "text/plain")
        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], os.environ["ALLOWED_ORIGIN"])

    def test_post_increments_count_successfully(self, mock_boto3):
        mock_table = mock_boto3.resource.return_value.Table.return_value

        mock_table.update_item.return_value = {
            "Attributes": {"count": 123}
        }

        event = {"httpMethod": "POST"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.update_item.assert_called_once_with(
            Key={"Id": "visitor_count"},
            UpdateExpression="SET #c = if_not_exists(#c, :start) + :inc",
            ExpressionAttributeNames={"#c": "count"},
            ExpressionAttributeValues={":inc": 1, ":start": 0},
            ReturnValues="UPDATED_NEW"
        )

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "123")

    def test_get_returns_existing_count(self, mock_boto3):
        mock_table = mock_boto3.resource.return_value.Table.return_value

        mock_table.get_item.return_value = {
            "Item": {"Id": "visitor_count", "count": 50}
        }

        event = {"httpMethod": "GET"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.get_item.assert_called_once_with(Key={"Id": "visitor_count"})

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "50")

        mock_table.update_item.assert_not_called()

    def test_get_initializes_and_returns_zero_when_item_missing(self, mock_boto3):
        mock_table = mock_boto3.resource.return_value.Table.return_value

        mock_table.get_item.return_value = {}

        event = {"httpMethod": "GET"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.get_item.assert_called_once()
        mock_table.put_item.assert_called_once_with(Item={"Id": "visitor_count", "count": 0})

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "0")

        mock_table.update_item.assert_not_called()

    def test_get_returns_zero_if_count_attribute_missing(self, mock_boto3):
        mock_table = mock_boto3.resource.return_value.Table.return_value

        mock_table.get_item.return_value = {
            "Item": {"Id": "visitor_count"} 
        }

        event = {"httpMethod": "GET"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.get_item.assert_called_once()

        mock_table.put_item.assert_not_called() 
        mock_table.update_item.assert_not_called()

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "0")

    def test_unsupported_method_falls_back_to_get(self, mock_boto3):
        mock_table = mock_boto3.resource.return_value.Table.return_value
        mock_table.get_item.return_value = {
            "Item": {"Id": "visitor_count", "count": 99}
        }

        event = {"httpMethod": "PUT"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.get_item.assert_called_once()
        mock_table.update_item.assert_not_called()

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "99")

    def test_dynamodb_post_failure_returns_500(self, mock_boto3):
        mock_table = mock_boto3.resource.return_value.Table.return_value
        mock_table.update_item.side_effect = Exception("Mock DynamoDB Error on POST")

        event = {"httpMethod": "POST"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.update_item.assert_called_once()

        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(response["body"], "0")

    def test_dynamodb_get_failure_returns_500(self, mock_boto3):
        mock_table = mock_boto3.resource.return_value.Table.return_value
        mock_table.get_item.side_effect = Exception("Mock DynamoDB Error on GET")

        event = {"httpMethod": "GET"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.get_item.assert_called_once()

        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(response["body"], "0")

if __name__ == '__main__':
    unittest.main()