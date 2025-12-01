import unittest
from unittest.mock import patch, MagicMock, patch.dict 
import os
import visitor_counter_code

os.environ["TABLE_NAME"] = "MockVisitorCounterDB"
os.environ["ALLOWED_ORIGIN"] = "https://mock.resumecount.com"

@patch('visitor_counter_code.TABLE')
class VisitorCounterTest(unittest.TestCase):
    def test_get_method_rest_api_v1(self, mock_table):
        event = {"httpMethod": "POST"}
        method = visitor_counter_code._get_method(event)
        self.assertEqual(method, "POST")

    def test_get_method_http_api_v2(self, mock_table):
        event = {"requestContext": {"http": {"method": "GET"}}}
        method = visitor_counter_code._get_method(event)
        self.assertEqual(method, "GET")

    def test_get_method_empty_event_defaults_to_get(self, mock_table):
        event = {}
        method = visitor_counter_code._get_method(event)
        self.assertEqual(method, "GET")

    def test_get_method_invalid_event_defaults_to_get(self, mock_table):
        event = {"some_key": 123}
        method = visitor_counter_code._get_method(event)
        self.assertEqual(method, "GET")

    def test_text_response_structure_and_cors(self, mock_table):
        response = visitor_counter_code._text_response(200, 42)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "42")
        self.assertEqual(response["headers"]["Content-Type"], "text/plain")
        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], os.environ["ALLOWED_ORIGIN"])

    def test_post_increments_count_successfully(self, mock_table):
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

    def test_get_returns_existing_count(self, mock_table):
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

    def test_get_returns_zero_when_item_missing(self, mock_table):
        mock_table.get_item.return_value = {}

        event = {"httpMethod": "GET"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.get_item.assert_called_once()
        mock_table.put_item.assert_not_called()
        mock_table.update_item.assert_not_called()

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "0")

    def test_get_returns_zero_if_count_attribute_missing(self, mock_table):
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

    def test_unsupported_method_falls_back_to_get(self, mock_table):
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

    def test_dynamodb_post_failure_returns_500(self, mock_table):
        mock_table.update_item.side_effect = Exception("Mock DynamoDB Error on POST")

        event = {"httpMethod": "POST"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.update_item.assert_called_once()

        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(response["body"], "0")

    def test_dynamodb_get_failure_returns_500(self, mock_table):
        mock_table.get_item.side_effect = Exception("Mock DynamoDB Error on GET")

        event = {"httpMethod": "GET"}
        context = MagicMock()

        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.get_item.assert_called_once()

        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(response["body"], "0")

    def test_get_method_invalid_input_type_defaults_to_get(self, mock_table):
        event_none = None
        self.assertEqual(visitor_counter_code._get_method(event_none), "GET")
        
        event_string = "invalid event"
        self.assertEqual(visitor_counter_code._get_method(event_string), "GET")

    def test_post_returns_zero_if_attributes_missing(self, mock_table):
        mock_table.update_item.return_value = {} 

        event = {"httpMethod": "POST"}
        context = MagicMock()
        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.update_item.assert_called_once()
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "0")

    def test_get_with_http_api_v2_event(self, mock_table):
        mock_table.get_item.return_value = {
            "Item": {"Id": "visitor_count", "count": 22}
        }
        
        event = {"requestContext": {"http": {"method": "GET"}}}
        context = MagicMock()
        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.get_item.assert_called_once_with(Key={"Id": "visitor_count"})
        mock_table.update_item.assert_not_called()
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "22")

    def test_post_with_http_api_v2_event(self, mock_table):
        mock_table.update_item.return_value = {
            "Attributes": {"count": 23}
        }

        event = {"requestContext": {"http": {"method": "POST"}}}
        context = MagicMock()
        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.update_item.assert_called_once()
        mock_table.get_item.assert_not_called()
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "23")

    def test_options_method_returns_200_without_db_call(self, mock_table):
        event = {"httpMethod": "OPTIONS"}
        context = MagicMock()
        response = visitor_counter_code.lambda_handler(event, context)

        mock_table.get_item.assert_not_called() 
        mock_table.update_item.assert_not_called()

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "") 
        self.assertIn("Access-Control-Allow-Origin", response["headers"])
        self.assertIn("Access-Control-Allow-Methods", response["headers"])

    @patch('visitor_counter_code.DYNAMODB')
    @patch.dict(os.environ, {}, clear=True)
    def test_defaults_when_env_vars_missing(self, mock_dynamodb, mock_table):
        mock_table.get_item.return_value = {
            "Item": {"Id": "visitor_count", "count": 1}
        }
        
        event = {"httpMethod": "GET"}
        context = MagicMock()
        response = visitor_counter_code.lambda_handler(event, context)

        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["body"], "1")

if __name__ == '__main__':
    unittest.main()