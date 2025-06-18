import boto3
from typing import Dict
from dotenv import load_dotenv
import os
load_dotenv()
PREDICTION_SESSIONS = os.getenv("PREDICTION_SESSIONS")
DETECTION_OBJECTS = os.getenv("DETECTION_OBJECTS")
class DynamoDBStorage:
    def __init__(self):
        dynamodb = boto3.resource("dynamodb")  # Use default credentials
        self.session_table = dynamodb.Table(PREDICTION_SESSIONS)
        self.objects_table = dynamodb.Table(DETECTION_OBJECTS)

    def get_prediction(self, uid: str) -> Dict:
        session = self.session_table.get_item(Key={"uid": uid}).get("Item")
        if not session:
            raise ValueError("Prediction not found")
        return {
            "predicted_image": session.get("predicted_image")
        }