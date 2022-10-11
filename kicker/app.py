
import json

from kicker import Kicker, KickerConfig

\

def clean_params(params):
    if params.get("angle"):
        angle_degree = float(params["angle"])
    else:
        raise Exception("angle not provided")
   
    if params.get("height"):
        height_inches = float(params["height"]) * 12.0
    else:
        raise Exception("height not provided")
    
    
    return {
        "angle_degree": angle_degree,
        "height_inches": height_inches,
        "debug": True if params.get("debug") == "true" else False
    }


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

    print(f"event {event['queryStringParameters'].keys()}")
    params = clean_params(event["queryStringParameters"])

    config = KickerConfig(**params)
    kicker = Kicker(config)
    print("Creating image")
    kicker.draw_image()

    
    url = kicker.save_image()
    print(f"Saved to S3 {url}")

    stats = kicker.stats
    
    print("Saving to DynamoDB")
    id = kicker.save()
    stats.update({"id": id}) 

    return {
        "statusCode": 200,
        "body": json.dumps(kicker.stats)
    }
