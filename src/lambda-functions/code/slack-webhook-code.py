import json
import boto3
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ssm = boto3.client('ssm')

def lambda_handler(event, context):
    print(json.dumps(event))

    message = json.loads(event['Records'][0]['Sns']['Message'])
    print(json.dumps(message))

    alarm_name = message['AlarmName']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']

    slack_message = {
        'text': (f':fire: *{alarm_name}* state is now *{new_state}*: {reason} from Nesq\n'
                f'```\n{json.dumps(message, indent=2)}```')
    }

    try:
        param = ssm.get_parameter(Name='slackwebhookurl', WithDecryption=True)
        webhook_url = param['Parameter']['Value']
    except Exception as e:
        print(f"Error retrieving SSM parameter 'slackwebhookurl': {str(e)}")
        return

    req = Request(
        webhook_url,
        json.dumps(slack_message).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        response = urlopen(req)
        response.read()
        print("Message posted to Slack")
    except HTTPError as e:
        print(f'Request failed: {e.code} {e.reason}')
    except URLError as e:
        print(f'Server Connection failed: {e.reason}')