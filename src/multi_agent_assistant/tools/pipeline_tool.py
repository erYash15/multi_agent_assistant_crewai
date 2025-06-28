from enum import Enum
from typing import Type
from pydantic import BaseModel, Field, PrivateAttr
from crewai.tools import BaseTool
import requests
from requests.auth import HTTPBasicAuth

# Define pipeline stages
class PipelineStage(str, Enum):
    preprocessing = "Preprocessing"
    training = "Training"
    postprocessing = "Postprocessing"

# Define tool input schema
class JenkinsTriggerInput(BaseModel):
    stage: PipelineStage = Field(..., description="Stage of the pipeline to trigger")

# Define Jenkins trigger tool
class JenkinsTriggerTool(BaseTool):
    name: str = "JenkinsTriggerTool"
    description: str = (
        "Trigger a Jenkins job for one of the pipeline stages: Preprocessing, Training, or Postprocessing."
    )
    args_schema: Type[BaseModel] = JenkinsTriggerInput

    # Declare private attributes
    _JENKINS_URL: str = PrivateAttr()
    _USERNAME: str = PrivateAttr()
    _API_TOKEN: str = PrivateAttr()

    def __init__(self, jenkin_api_token: str):
        super().__init__()
        self._JENKINS_URL = "http://localhost:8080"
        self._USERNAME = "admin"
        self._API_TOKEN = jenkin_api_token

    def _run(self, stage: str) -> str:
        JOB_NAME = f"{stage}-size-pro"
        trigger_url = f"{self._JENKINS_URL}/job/{JOB_NAME}/buildWithParameters"

        try:
            response = requests.post(
                trigger_url,
                auth=HTTPBasicAuth(self._USERNAME, self._API_TOKEN),
            )
            if response.status_code == 201:
                return f"✅ Jenkins job for '{stage}' triggered successfully!"
            else:
                return f"❌ Failed to trigger job for '{stage}': {response.status_code}\n{response.text}"
        except Exception as e:
            return f"❌ Exception while triggering Jenkins job: {str(e)}"
