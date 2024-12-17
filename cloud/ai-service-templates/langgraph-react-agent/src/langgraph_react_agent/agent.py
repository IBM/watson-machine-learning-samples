from ibm_watsonx_ai import APIClient
from langchain_ibm import ChatWatsonx
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from langgraph_react_agent import TOOLS


def get_graph(client: APIClient, model_id: str) -> CompiledGraph:
    """Graph generator function."""

    # Initialise ChatWatsonx
    chat = ChatWatsonx(model_id=model_id, watsonx_client=client)

    system_prompt = "You are a helpful AI assistant, please respond to the user's query to the best of your ability!"

    # Create instance of compiled graph
    graph = create_react_agent(chat, tools=TOOLS, checkpointer=MemorySaver(), state_modifier=system_prompt)
    return graph
