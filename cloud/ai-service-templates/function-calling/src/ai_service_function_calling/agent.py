from ibm_watsonx_ai import APIClient
from langchain_ibm import ChatWatsonx
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent

from ai_service_function_calling import TOOLS


def get_graph(client: APIClient, model_id: str) -> CompiledGraph:
    """Graph generator function."""

    # Initialise ChatWatsonx
    chat = ChatWatsonx(model_id=model_id, watsonx_client=client)

    # Create instance of compiled graph
    graph = create_react_agent(chat, tools=TOOLS)
    return graph
