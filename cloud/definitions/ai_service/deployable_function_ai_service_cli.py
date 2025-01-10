def deployable_ai_service(context, model_id="meta-llama/llama-3-1-70b-instruct", space_id="", url=""):
    from ibm_watsonx_ai import APIClient, Credentials
    from langchain_ibm import ChatWatsonx
    from langchain_core.tools import tool
    from langgraph.prebuilt import create_react_agent

    def prepare_graph(context):
        payload = context.get_json()

        api_client = APIClient(
            credentials=Credentials(
                url=url or payload.get("url"), token=context.get_token()
            ),
            space_id=space_id or payload.get("space_id")
        )

        chat = ChatWatsonx(
            watsonx_client=api_client,
            model_id=payload.get("model_id") or model_id,
            params={"temperature": 0.1}
        )

        return create_react_agent(chat, tools=tools)

    @tool
    def add(a: float, b: float) -> float:
        """Add a and b."""
        return a + b

    @tool
    def subtract(a: float, b: float) -> float:
        """Subtract a and b."""
        return a - b

    @tool
    def multiply(a: float, b: float) -> float:
        """Multiply a and b."""
        return a * b

    @tool
    def divide(a: float, b: float) -> float:
        """Divide a and b."""
        return a / b

    tools = [add, subtract, multiply, divide]

    def generate(context) -> dict:
        graph = prepare_graph(context)

        payload = context.get_json()
        question = payload["question"]

        response = graph.invoke({"messages": [("user", f"{question}")]})

        json_messages = [msg.to_json() for msg in response['messages']]

        response['messages'] = json_messages

        return {"body": response}

    def generate_stream(context):
        graph = prepare_graph(context)

        payload = context.get_json()
        question = payload["question"]

        for el in graph.stream({"messages": [("user", f"{question}")]}, stream_mode="values"):
            json_messages = [msg.to_json() for msg in el['messages']]
            el['messages'] = json_messages
            yield el

    return generate, generate_stream
