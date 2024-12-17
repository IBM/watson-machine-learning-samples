def deployable_ai_service(context, **custom):
    from langgraph_react_agent.agent import get_graph
    from ibm_watsonx_ai import APIClient, Credentials
    from langchain_core.messages import BaseMessage

    model_id = custom.get("model_id")
    client = APIClient(credentials=Credentials(url=custom.get("url"), token=context.generate_token()),
                       space_id=custom.get("space_id"))

    graph = get_graph(client, model_id)

    def get_formatted_message(resp: BaseMessage) -> dict:
        role = resp.type
        if role == "ai":
            role = "assistant"
            if kwargs := resp.additional_kwargs:
                return {
                    "role": role,
                    **kwargs
                }
            else:
                return {
                    "role": role,
                    "content": resp.content
                }
        elif role == "tool":
            return {
                "role": role,
                "content": resp.content
            }

    def generate(context) -> dict:
        """
        The `generate` function handles the REST call to the inference endpoint
        POST /ml/v4/deployments/{id_or_name}/ai_service

        The generate function should return a dict
        The following optional keys are supported currently
        - data

        A JSON body sent to the above endpoint should follow the format:
          {
            "question": <your query or prompt to the model>
            "data" [OPTIONAL]: {
                "exog": <explanatory variables (independent variables)>,
                "endog": <dependent variable (response variable)>
            }
          }

        Depending on the <value> of the mode, it will return different response
        """

        client.set_token(context.get_token())

        payload = context.get_json()
        question = str(payload["question"])
        data = payload.get("data")

        # If data is provided, enhance the question string with the data
        if data:
            exog_data = data.get('exog', [])
            endog_data = data.get('endog', [])

            # Append the data information to the question string
            question += f" Explanatory variables (independent): {exog_data}. Dependent variable (response): {endog_data}."

        config = {"configurable": {"thread_id": custom.get("thread_id")}}  # Checkpointer configuration

        prev_checkpoint_n = len(list(graph.checkpointer.list(config)))
        generated_response = graph.invoke({"messages": [("user", question)]}, config)
        new_mess_n = len(list(graph.checkpointer.list(config))) - prev_checkpoint_n - 1

        choices = []
        execute_response = {
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "choices": choices
            }
        }

        for resp in generated_response["messages"][-new_mess_n:]:
            message = get_formatted_message(resp)
            if message is None:
                continue
            choices.append(
                {
                    "index": 0,
                    "message": message
                }
            )


        return execute_response

    def generate_stream(context) -> dict:
        """
        The `generate_stream` function handles the REST call to the Server-Sent Events (SSE) inference endpoint
        POST /ml/v4/deployments/{id_or_name}/ai_service_stream

        The generate function should return a dict
        The following optional keys are supported currently
        - data

        A JSON body sent to the above endpoint should follow the format:
          {
            "question": <your query or prompt to the model>
            "data" [OPTIONAL]: {
                "exog": <explanatory variables (independent variables)>,
                "endog": <dependent variable (response variable)>
            }
          }

        Depending on the <value> of the mode, it will return different streamed responses
        """
        client.set_token(context.get_token())

        payload = context.get_json()
        question = str(payload["question"])
        data = payload.get("data")

        # If data is provided, enhance the question string with the data
        if data:
            exog_data = data.get('exog', [])
            endog_data = data.get('endog', [])

            # Append the data information to the question string
            question += f" Explanatory variables (independent): {exog_data}. Dependent variable (response): {endog_data}."

        config = {"configurable": {"thread_id": custom.get("thread_id")}}  # Checkpointer configuration

        for value in graph.stream({"messages": [("user", f"{question}")]}, config, stream_mode="values"):
            message = get_formatted_message(value["messages"][-1])
            if message is None:
                continue

            yield {
                "choices": [{
                    "index": 0,
                    "message": message
                }]
            }

    return generate, generate_stream
