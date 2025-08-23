import sys
import logging
import os
from datetime import datetime
from functools import wraps
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from tabulate import tabulate

from tools import VRVAAutomationTools
import config


# --- Main Agent Class Definition ---

class VRAgent:
    """
    Main class for the VR/VA automation agent.
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tabulate_agent = lambda x: tabulate(x, headers='keys', tablefmt='psql')

        # LLM (Gemini) configuration
        self.llm_brain = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            google_api_key=config.GOOGLE_API_KEY
        )

    def run_agent(self) -> None:
        """
        Main method to run the agent's logic.
        """
        self.logger.info("VR/VA Agent started")

        # --- Tool List ---
        vrva_tools_instance = VRVAAutomationTools()
        tools_list = [
            vrva_tools_instance.consolidate_and_clean_data,
            vrva_tools_instance.read_file
        ]
        print(tools_list)

        # --- Agent Prompt (using ChatPromptTemplate) ---
        agent_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", config.TEMPLATE),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

        # --- Agent Creation and Execution ---
        agent = create_tool_calling_agent(self.llm_brain, tools_list, agent_prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools_list,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
        )

        # --- 6. User Interaction ---
        print("--- VR/VA Benefits Automation Agent ---")
        print("Hello! I am an agent specializing in benefit calculation automation.")
        print("I am ready to process your VR and VA spreadsheets.")
        print("Ask me, for example: 'Automate the monthly VR calculation for May.'")
        print("Type 'exit' to quit.")

        while True:
            user_input = input("\nYour question: ")
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break

            try:
                response = agent_executor.invoke({"input": user_input, "chat_history": []})
                print(f"\nAgent: {response['output']}")
            except Exception as e:
                print(f"An error occurred while processing your question: {e}")
                print("Please try again.")

if __name__ == "__main__":
    agent_instance = VRAgent()
    agent_instance.run_agent()