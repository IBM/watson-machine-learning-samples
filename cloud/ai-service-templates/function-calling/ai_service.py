def deployable_ai_service(context, **custom):
    from ai_service_function_calling.agent import get_graph
    from ibm_watsonx_ai import APIClient, Credentials

    model_id = custom.get("model_id")
    client = APIClient(credentials=Credentials(url=custom.get("url"), token=context.generate_token()),
                       space_id=custom.get("space_id"))

    graph = get_graph(client, model_id)

    def generate(context) -> dict:
        """
        The `generate` function handles the REST call to the inference endpoint
        POST /ml/v4/deployments/{id_or_name}/ai_service

        The generate function should return a dict
        The following optional keys are supported currently
        - data

        A json body sent to the above endpoint should follow the format:
          {
            "question": <anything you'd like to say to the model>
            "data" [OPTIONAL]: {
                "exog": <explanatory variables (independent variables)>,
                "endog": <dependent variable (response variable>
            }
          }

        Depending on the <value> of the mode, it will return different response
        """

        client.set_token(context.get_token())

        payload = context.get_json()
        question = str(payload["question"])
        data = payload.get("data")  # Using get() to avoid KeyError if 'data' is missing

        # If data is provided, enhance the question string with the data
        if data:
            exog_data = data.get('exog', [])
            endog_data = data.get('endog', [])

            # Append the data information to the question string
            question += f" Explanatory variables (independent): {exog_data}. Dependent variable (response): {endog_data}."

        response = graph.invoke({"messages": [("user", question)]})

        json_messages = [msg.to_json() for msg in response['messages']]

        return {
            "body": json_messages
        }

    return generate
