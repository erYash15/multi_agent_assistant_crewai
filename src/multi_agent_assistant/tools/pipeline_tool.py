from enum import Enum
from typing import Type
from pydantic import BaseModel, Field, PrivateAttr
from crewai.tools import BaseTool
import requests
from requests.auth import HTTPBasicAuth

class PipelineStage(str, Enum):
    PREPROCESSING = "preprocessing"
    TRAINING = "training"
    POSTPROCESSING = "postprocessing"

class JenkinsTriggerInput(BaseModel):
    stage: PipelineStage = Field(..., description="Stage of the pipeline to trigger")

class JenkinsTriggerTool(BaseTool):
    name: str = "JenkinsTriggerTool"
    description: str = (
    """
    Jenkins Pipeline Trigger Tool

    A tool for triggering specific stages in a Jenkins pipeline. This tool interfaces with Jenkins'
    REST API to initiate jobs corresponding to different pipeline stages (preprocessing, training, 
    postprocessing).

    Features:
    - Supports triggering of three pipeline stages: preprocessing, training, and postprocessing
    - Uses Jenkins' REST API with basic authentication
    - Provides detailed feedback on job triggering status
    - Handles errors and exceptions gracefully

    Usage:
    1. Initialize the tool with Jenkins credentials:
    
    Input: `preprocessing`, `training`, or `postprocessing` (any one of these three)
    
    2. Trigger a pipeline stage by specifying one of:
    - 'preprocessing'
    - 'training'
    - 'postprocessing'

    Returns:
    A string indicating success or failure, including:
    - Success: Job name, status code (201), and timestamp
    - Failure: Error details, status code, and response text
    - Exception: Error message if request fails

    Example Responses:
    - Success: "✅ Jenkins job 'preprocessing-size-pro' triggered successfully! 201\nWed, 21 Feb 2024 15:30:45 GMT"
    - Failure: "❌ Failed to trigger 'training-size-pro': 404\nJob not found\nWed, 21 Feb 2024 15:31:22 GMT"
    - Exception: "❌ Exception triggering 'postprocessing-size-pro': Connection timed out"
    """
    )
    
    args_schema: Type[BaseModel] = JenkinsTriggerInput

    _JENKINS_URL: str = PrivateAttr()
    _USERNAME: str = PrivateAttr()
    _API_TOKEN: str = PrivateAttr()

    def __init__(self, jenkins_api_token: str, jenkins_url: str = "http://localhost:8080", username: str = "admin"):
        super().__init__()
        self._JENKINS_URL = jenkins_url
        self._USERNAME = username
        self._API_TOKEN = jenkins_api_token

    def _run(self, stage: str) -> str:
        job_name = f"{stage.lower()}-size-pro"  # Ensure lowercase consistency
        trigger_url = f"{self._JENKINS_URL}/job/{job_name}/build"
        
        print(f"Attempting to trigger job at: {trigger_url}")
        
        try:
            response = requests.post(
                trigger_url,
                auth=HTTPBasicAuth(self._USERNAME, self._API_TOKEN),
                timeout=10
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 201:
                return f"✅ Jenkins job '{job_name}' triggered successfully! {response.status_code}\n{response.headers._store['date'][1]}"
            return f"❌ Failed to trigger '{job_name}': {response.status_code}\n{response.text}\n{response.headers._store['date'][1]}"
        except Exception as e:
            return f"❌ Exception triggering '{job_name}': {str(e)}"