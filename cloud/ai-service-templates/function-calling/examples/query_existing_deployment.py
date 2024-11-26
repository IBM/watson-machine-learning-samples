import ibm_watsonx_ai

from utils import load_config, print_message

config = load_config("deployment")

client = ibm_watsonx_ai.APIClient(
    credentials=ibm_watsonx_ai.Credentials(url=config["watsonx_url"], api_key=config["watsonx_apikey"]),
    space_id=config["space_id"])

# Scoring data
ai_service_payload = {
    "question": "Can you perform an OLS regression on the following data and with necessary assumptions?",
    "data": {
        "exog": [1, 2, 3, 4, 5, 6, 7, 8],  # Explanatory variables (independent variables)
        "endog": [2, 4, 6, 8, 10, 12, 14, 16]  # Dependent variable (response variable)
    }
}

# Executing deployed AI service with provided scoring data
response_content = client.deployments.run_ai_service(config["deployment_id"], ai_service_payload)

for r in response_content:
    print_message(r)
