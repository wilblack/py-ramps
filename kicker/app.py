
import json

from kicker import Kicker, KickerConfig


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    config = KickerConfig(event["angle"], height_inches=event["height"] * 12.0)
    kicker = Kicker(config)
    print("Creating image")
    # kicker.draw_image()
    
    return {
        "statusCode": 200,
        "body": json.dumps(kicker.stats)
    }
