from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from app.utils.bedrock import get_llm

@CrewBase
class MeetscribeCrew():
    """Meetscribe crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config['summarizer'], 
            verbose=True,
            llm="bedrock/us.meta.llama3-2-90b-instruct-v1:0"
        )

    @agent
    def action_item_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['action_item_extractor'], 
            verbose=True,
            llm="bedrock/us.meta.llama3-2-90b-instruct-v1:0"
        )

    @agent
    def email_drafter(self) -> Agent:
        return Agent(
            config=self.agents_config['email_drafter'],
            verbose=True,
            llm="bedrock/us.meta.llama3-2-90b-instruct-v1:0"
        )
    
    @task
    def summary_task(self) -> Task:
        return Task(
            config=self.tasks_config['summary_task'],
        )

    @task
    def action_items_task(self) -> Task:
        return Task(
            config=self.tasks_config['action_items_task'],
        )

    @task
    def email_task(self) -> Task:
        return Task(
            config=self.tasks_config['email_task'],
            output_file='follow_up_email.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
        

# process.seq -> each agent runs one after the other ( ie. tasks run in order since they're assigned to each agent in tasks.yaml )
# Outputs do NOT get overwritten, they are stored in results array one after the other. results[0].raw for eg. 