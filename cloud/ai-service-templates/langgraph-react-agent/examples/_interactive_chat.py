import textwrap
import json
from collections.abc import Generator
from typing import Callable

from statsmodels import datasets


class InteractiveChat:
    def __init__(
        self,
        ai_service_invoke: Callable,
        questions: tuple[str] = None,
        data: dict = None,
        stream: bool = False,
        verbose: bool = True,
    ) -> None:
        self.ai_service_invoke = ai_service_invoke
        self._ordered_list = lambda seq_: "\n".join(f"\t{i}) {k}" for i, k in enumerate(seq_, 1))
        self._delta_start = False
        self.verbose = verbose
        self.stream = stream

        self.questions = (
            (
                "Is the relationship between my data linear?",
                "What statistical tests should I run to verify that the given observations are independent?",
                "Analyse my data to assess its suitability for linear regression. Please give a detailed answer",
                "Is linear regression a proper model for my data? Please provide a brief justification",
                "Try fitting the linear regression model to my data. Summarise the results in one sentence",
                "Can you perform an OLS regression on the following data and with necessary assumptions?",
            )
            if questions is None
            else questions
        )

        self.data = (
            {
                "Breast Cancer Data": datasets.cancer,
                "Statewide Crime Data 2009": datasets.statecrime,
                "Bill Greene credit scoring data": datasets.ccard,
            }
            if data is None
            else data
        )

        self._help_message = textwrap.dedent(
            """
        The following commands are supported:
          --> help | h : prints this help message
          --> quit | q : exits the prompt and ends the program
          --> list_datasets : prints a list of available datasets
          --> list_questions : prints a list of available questions
          --> r | reset : resets the program states allowing choosing different dataset
        """)

    @property
    def questions(self) -> tuple:
        return self._questions

    @questions.setter
    def questions(self, q: tuple) -> None:
        self._questions = q
        self._questions_prompt = (
            f"\tQuestions:\n{self._ordered_list(self._questions)}\n"
        )

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, d: dict) -> None:
        self._data = d
        self._data_names = tuple(sorted(self.data.keys()))
        self._datasets_prompt = f"\tDatasets:\n{self._ordered_list(self._data_names)}\n"

    def _user_input_loop(self) -> Generator[str, bool, None]:
        print(self._help_message)

        print(self._datasets_prompt)
        dataset_chosen = False
        while True:

            if not dataset_chosen:
                d = input("Choose a dataset\n --> ")

                dataset_chosen = yield d, "dataset"

                yield  # give control back to the calling function after receiving data
                if dataset_chosen:
                    print(self._questions_prompt)

            if dataset_chosen:
                q = input("\nChoose a question or ask one of your own.\n --> ")

                dataset_chosen = yield q, "question"

                yield

    def _print_message(self, message: dict) -> None:
        header = f" {message['role'].capitalize()} Message ".center(80, '=')
        if delta := message.get("delta"):
            if not self._delta_start:
                print("\n",header)
                self._delta_start = True
            print(delta, flush=True, end="")
        else:
            # self._delta_start = False
            print("\n", header)
            print(f"{message.get('content', message)}")

    def run(self) -> None:
        # TODO implement signal handling (especially Ctrl-C)
        while True:
            try:
                q, d = None, None

                dataset_chosen = False
                user_loop = self._user_input_loop()

                for action, stage in user_loop:  # unsupported command support!

                    if action == "r" or action == "reset":
                        return

                    if action == "h" or action == "help":
                        print(self._help_message)
                    elif action == "quit" or action == "q":
                        raise EOFError

                    elif action == "list_datasets":
                        print(self._datasets_prompt)
                    elif action == "list_questions":
                        print(self._questions_prompt)

                    elif stage == "dataset":
                        if not action.isdigit():
                            print(
                                f"please provide a valid number corresponding to an existing dataset"
                            )

                        else:
                            number = int(action)
                            print(f"you chose DATASET {number}\n")
                            if number > len(self.data) or number < 0:
                                print(
                                    "provided numbers have to match the available numbers"
                                )
                            else:
                                dataset_chosen = True
                                d = number

                    elif stage == "question":
                        user_message = {}
                        # small caveat -- if user answers to the chat a single digit we'll treat it as trying to choose on of our self.questions
                        if not action.isdigit():  # user defined question
                            user_message["content"] = action.strip()
                        else:
                            number = int(action)

                            print(f"you chose QUESTION {number}\n")
                            if number > len(self.questions) or number < 0:
                                print(
                                    "provided numbers have to match the available numbers"
                                )
                            else:
                                user_message["content"] = self.questions[number - 1]
                                user_message["data"] = {
                                    "exog": self.data[self._data_names[d - 1]]
                                    .load_pandas()
                                    .exog.iloc[:25, 0]
                                    .to_numpy()
                                    .tolist(),
                                    "endog": self.data[self._data_names[d - 1]]
                                    .load_pandas()
                                    .endog.iloc[:25]
                                    .to_numpy()
                                    .tolist(),
                                }

                        request_payload_json = {
                            "messages": [{"role": "user", **user_message}]
                        }

                        resp = self.ai_service_invoke(request_payload_json)

                        if self.stream:
                            for r in resp:
                                if type(r) == str:
                                    r = json.loads(r)
                                for c in r["choices"]:
                                    self._print_message(c["message"])
                            self._delta_start = False
                        else:
                            resp_choices = resp.get("body", resp)["choices"]
                            choices = (
                                resp_choices if self.verbose else resp_choices[-1:]
                            )

                            for c in choices:
                                self._print_message(c["message"])

                    user_loop.send(dataset_chosen)
            except EOFError:
                break
