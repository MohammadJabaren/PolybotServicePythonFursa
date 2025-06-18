import boto3
from typing import Dict

class DynamoDBStorage:
    def __init__(self):
        dynamodb = boto3.resource("dynamodb")  # Use default credentials
        self.session_table = dynamodb.Table("Jabaren_prediction_sessions_dev")
        self.objects_table = dynamodb.Table("Jabaren_detection_objects_dev")

    def get_prediction(self, uid: str) -> Dict:
        session = self.session_table.get_item(Key={"uid": uid}).get("Item")
        if not session:
            raise ValueError("Prediction not found")
        return {
            "predicted_image": session.get("predicted_image")
        }
