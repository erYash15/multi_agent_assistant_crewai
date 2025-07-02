# src/multi_agent_assistant/tools/prediction_tool.py

from crewai.tools import BaseTool
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import OpenAI
from typing import Type, Optional, ClassVar
from pydantic import BaseModel, Field, PrivateAttr
import pandas as pd
import logging
import json

class PredictionToolInput(BaseModel):
    argument: str = Field(
        ...,
        description="User's query related to size distribution"
    )

class PandasToolBaseClass:
    def __init__(self, df: pd.DataFrame, description: str, api_key: Optional[str] = None):
        self.df = df
        self.description = description
        self.api_key = api_key
        self._setup_logging()
        self.agent = create_pandas_dataframe_agent(
            OpenAI(
                temperature=0,
                openai_api_key=self.api_key,
            ),
            self.df,
            verbose=True,
            allow_dangerous_code=True,
            max_iterations=15,  # Prevent infinite retries
            extra_tools=[],
        )

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def pandas_tool(self, query: str) -> str:
        try:
            full_prompt = f"""
            {self.description}

            Current Task: {query}

            Instructions:
            1. Analyze the data carefully
            2. Provide clear numerical results
            3. Include relevant statistics
            4. Explain your methodology
            """
            return self.agent.run(full_prompt)
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return f"Error: {str(e)}"

class PredictionTools(BaseTool):
    name: str = "Prediction Tool"
    description: str = (
    """
    Size Distribution Prediction Tool
    This tool processes natural language queries about size distribution and returns detailed 
    analytical results using pandas DataFrame operations powered by OpenAI's language model.
    - Processes complete user sentences including article numbers
    """ 
    )
    
    args_schema: Type[BaseModel] = PredictionToolInput
    # These are internal-only fields, not exposed to Pydantic
    _df: pd.DataFrame = PrivateAttr()
    _tool: PandasToolBaseClass = PrivateAttr()

    def __init__(self, data_path: str, api_key: Optional[str] = None):
        super().__init__()
        print("data_path:", data_path)
        self._df = pd.read_csv(data_path)
        self._tool = PandasToolBaseClass(self._df, self.description, api_key)

    def _run(self, argument) -> str:
        
        query = f"""
        Data Schema:
        ------------
        1. group_article (str): Unique product identifier (e.g. "S42834")
        2. technical_size (str/numeric): Standardized size value of distribution of sizes (e.g. "M", "36", "9.5")
        3. sizecurve (float): ratio of total sales for this size
        4. local_size (str): Region-specific size designation
        5. sizecurve_cluster (str): Grouping of similar size patterns
        6. business_segments (str): Product category (e.g. "menswear", "footwear")
        
        Current Query: {str(argument)}

        Business Rules:
        ---------------
        - Higher size_curve = more popular size
        - Compare sizes within the same sizecurve_cluster for accurate analysis
        - Regional preferences visible in local_size vs technical_size
        """
        
        # print("QUERY:", query)
        
        result = self._tool.pandas_tool(query)
        # return json.dumps({
        # "analysis": str(result),
        # })
        return str(result)