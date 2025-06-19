import boto3
from typing import Dict
from dotenv import load_dotenv
import os
load_dotenv()
PREDICTION_SESSIONS = os.getenv("PREDICTION_SESSIONS")
DETECTION_OBJECTS = os.getenv("DETECTION_OBJECTS")

class DynamoDBStorage:
    def __init__(self):
        region = os.getenv("AWS_REGION", "us-west-1")  # default to us-west-1 if not set
        if not region:
            raise ValueError("Missing AWS_REGION environment variable")
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.session_table = self.dynamodb.Table(PREDICTION_SESSIONS)
        self.objects_table = self.dynamodb.Table(DETECTION_OBJECTS)

    def get_prediction(self, uid: str) -> Dict:
        session = self.session_table.get_item(Key={"uid": uid}).get("Item")
        if not session:
            raise ValueError("Prediction not found")
        return {
            "predicted_image": session.get("predicted_image")
        }