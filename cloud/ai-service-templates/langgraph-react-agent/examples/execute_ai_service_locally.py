from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.deployments import RuntimeContext
from statsmodels import datasets

from ai_service import deployable_ai_service
from utils import load_config

config = load_config()
dep_config = config["deployment"]

client = APIClient(credentials=Credentials(url=dep_config["watsonx_url"], api_key=dep_config["watsonx_apikey"]))

custom = {
    "model_id": config["ai_service"]["model_id"],
    "space_id": dep_config["space_id"],
    "url": client.credentials.url,
}

context = RuntimeContext(api_client=client)

questions = (
    "Is the relationship between my data linear?",
    "What statistical tests should I run to verify that the given observations are independent?",
    "Analyse my data to assess its suitability for linear regression. Please give a detailed answer",
    "Is linear regression a proper model for my data? Please provide a brief justification",
    "Try fitting the linear regression model to my data. Summarise the results in one sentence",
    "Can you perform an OLS regression on the following data and with necessary assumptions?",
)

data = {
    "Breast Cancer Data": datasets.cancer,
    "Statewide Crime Data 2009": datasets.statecrime,
    "Bill Greene credit scoring data": datasets.ccard
}
data_names = tuple(sorted(data.keys()))

ai_service_generate_resp_func = deployable_ai_service(context=context, **custom)

ordered_list = lambda seq_: "\n".join(f"\t{i}) {k}" for i, k in enumerate(seq_, 1))

questions_prompt = f"""\
    Questions:
{ordered_list(questions)}
"""

datasets_prompt = f"""\
    Datasets:
{ordered_list(data_names)}
"""

help_message = """
The following commands are supported:
  --> help | h : prints this help message
  --> quit | q : exits the prompt and ends the program
  --> list_datasets : prints a list of available datasets
  --> list_questions : prints a list of available questions
  --> r | reset : resets the program states allowing choosing different dataset

"""


def user_input_loop():
    print(help_message)

    print(datasets_prompt)
    dataset_chosen = False
    while True:

        if not dataset_chosen:
            d = input("Choose a dataset\n --> ")

            dataset_chosen = yield d, "dataset"

            yield  # give control back to the calling function after receiving data
            if dataset_chosen:
                print(questions_prompt)

        if dataset_chosen:
            q = input("Choose a question or ask one of your own.\n --> ")

            dataset_chosen = yield q, "question"

            yield


def main():
    q, d = None, None

    dataset_chosen = False
    user_loop = user_input_loop()

    for action, stage in user_loop:  # unsupported command support! 

        if action == "r" or action == "reset": 
            return

        if action == "h" or action == "help":
            print(help_message)
        elif action == "quit" or action == "q":
            raise EOFError

        elif action == "list_datasets":
            print(datasets_prompt)
        elif action == "list_questions":
            print(questions_prompt)
        

        elif stage == "dataset":
            if not action.isdigit():
                print(f"please provide a valid number corresponding to an existing dataset")

            else:        
                number = int(action)
                print(f"you chose DATASET {number}\n")
                if number > len(data) or number < 0:
                    print("provided numbers have to match the available numbers")
                else:
                    dataset_chosen = True
                    d = number

        elif stage == "question":
            # small caveat -- if user answers to the chat a single digit we'll treat it as trying to choose on of our questions
            if not action.isdigit():  # user defined question
                context.request_payload_json = {
                    "question":  action.strip()
                }

            else:
                number = int(action)

                print(f"you chose QUESTION {number}\n")
                if number > len(questions) or number < 0:
                    print("provided numbers have to match the available numbers")
                else:
                    context.request_payload_json = {
                        "question": questions[number - 1],
                        "data": {
                            "exog": data[data_names[d - 1]].load_pandas().exog.iloc[:25, 0].to_numpy().tolist(),
                            "endog": data[data_names[d - 1]].load_pandas().endog.iloc[:25].to_numpy().tolist(),
                        }
                    }

            resp = ai_service_generate_resp_func(context)
            print(f"{' Ai Message '.center(80, '=')}")
            print(context.request_payload_json)
            print(resp["body"]["choices"][0]["message"]["content"])


        user_loop.send(dataset_chosen)


# TODO implement signal handling (especially Ctrl-C)
while True:
    try:
        main()
    except EOFError:
        break
