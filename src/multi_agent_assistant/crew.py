from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
from src.multi_agent_assistant.tools.prediction_tool import PredictionTools
from src.multi_agent_assistant.tools.pipeline_tool import JenkinsTriggerTool
from langchain.llms import OpenAI

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class MultiAgentAssistant():
    """MultiAgentAssistant crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    # Set your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    jenkins_key = os.getenv("JENKINS_API_KEY")
    model = os.getenv("MODEL")
    
    # Create the prediction tool
    pred_tool = PredictionTools(
        data_path="knowledge/ds_sizepro_output.csv",
        api_key=api_key
    )
    
    jenkins_tool = JenkinsTriggerTool(jenkins_key)
    
    @agent
    def manager_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['manager_agent'],
            verbose=True,
            tools = [self.pred_tool, self.jenkins_tool],
            allow_delegation=True,
            max_iter=1
        )
    
        
    # @agent
    # def size_curve_forecasting_analyst(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['size_curve_forecasting_analyst'],
    #         verbose=True,
    #         tools = [self.pred_tool],
    #         allow_delegation=False,
    #         max_iter = 1
    #     )
        
    # @agent
    # def mlops_expert(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['mlops_expert'],           
    #         tools=[self.jenins_tool],
    #         verbose=True,
    #         allow_delegation=False,
    #         max_iter = 1
    #     )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
        
    @task
    def size_curve_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['size_curve_analysis_task'], # type: ignore[index]
            # human_input=True,
        )
        
    # # @task
    # def trigger_pipeline_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['trigger_pipeline_task'], # type: ignore[index]
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the MultiAgentAssistant crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            verbose=True,
            memory=True,
            process=Process.sequential,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
            manager_llm=self.model,
            # handle_parsing_errors=True,
            # manager_agent=self.manager_agent()
        )
        
    
