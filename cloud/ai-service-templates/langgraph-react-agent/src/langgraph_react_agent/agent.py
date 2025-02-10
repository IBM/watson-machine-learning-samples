from typing import Callable

from ibm_watsonx_ai import APIClient
from langchain_ibm import ChatWatsonx
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from langgraph_react_agent import TOOLS

def get_graph_closure(client: APIClient, model_id: str) -> Callable:
    """Graph generator closure."""

    # Initialise ChatWatsonx
    chat = ChatWatsonx(model_id=model_id, watsonx_client=client)

    # Define system prompt
    default_system_prompt = "You are a helpful AI Research assistant, please respond to the user's query to the best of your ability! Execute a tool call whenever you see fit. When using tools, make sure to format the URL to an arXiv research paper like 'https://arxiv.org/html/2501.12948v1'"

    # Initialise memory saver
    memory = MemorySaver()

    def get_graph(system_prompt=default_system_prompt) -> CompiledGraph:
        """Get compiled graph with overwritten system prompt, if provided"""

        # Create instance of compiled graph
        return create_react_agent(
            chat, tools=TOOLS, checkpointer=memory, state_modifier=system_prompt
        )

    return get_graph
