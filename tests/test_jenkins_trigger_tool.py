import pytest
from src.multi_agent_assistant.tools.pipeline_tool import JenkinsTriggerTool, PipelineStage
import os
import requests
from requests.auth import HTTPBasicAuth

# Configuration - set these in your environment or replace directly
JENKINS_URL = os.getenv("JENKINS_URL", "http://localhost:8080")
JENKINS_USER = os.getenv("JENKINS_USER", "admin")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN", "your_api_token")

@pytest.fixture
def jenkins_tool():
    return JenkinsTriggerTool(
        jenkins_api_token=JENKINS_TOKEN,
        jenkins_url=JENKINS_URL,
        username=JENKINS_USER
    )
    
def test_jenkins_auth():
    response = requests.get(
        f"{JENKINS_URL}/api/json",
        auth=HTTPBasicAuth(JENKINS_USER, JENKINS_TOKEN),
        timeout=5
    )
    print(f"Auth Test Status: {response.status_code}")
    assert response.status_code == 200, "Authentication failed!"
    
def test_real_jenkins_connection(jenkins_tool):
    """Test basic connection to Jenkins"""
    result = jenkins_tool._run("preprocessing")
    print("result:", result)
    
    assert "triggered" in result or "Failed" in result
    print(f"\nJenkins Response: {result}")

def test_all_pipeline_stages(jenkins_tool):
    """Test all defined pipeline stages"""
    for stage in PipelineStage:
        result = jenkins_tool._run(stage.value)
        print(f"\nStage {stage.value} result: {result}")
        assert "triggered" in result or "Failed" in result

def test_invalid_job_handling(jenkins_tool):
    """Test error handling for non-existent job"""
    result = jenkins_tool._run("nonexistent-stage")
    print(f"\nInvalid job response: {result}")
    assert "Failed" in result or "Exception" in result