import os
import pytest
from src.multi_agent_assistant.tools.prediction_tool import PandasToolBaseClass, PredictionTools

api_key = os.getenv("OPENAI_API_KEY")
dpath = "knowledge/ds_sizepro_output.csv"

@pytest.fixture
def prediction_tools():
    return PredictionTools(
        data_path=dpath,
        api_key=api_key,
    )
    
def test_prediction_output(prediction_tools):
    result = prediction_tools._run(
        "What are the top 3 most popular sizes for article S42834 and what are its respective size curve"
        )
    print(result)