import json
import tomllib
from pathlib import Path


def print_message(message: dict) -> None:
    """
    Display the output of an AI service

    :param message: The dictionary containing the message to be printed.
    :type message: dict
    :return: None. This function only prints the output.
    """

    print(f" ===== {message['id'][-1]} =====")
    if message["id"][-1] == "AIMessage":
        content = message["kwargs"].get("additional_kwargs", message["kwargs"].get("content"))
        if isinstance(content, dict):
            print(json.dumps(content, indent=2) + "\n")
        else:
            print(content + "\n")
    elif message["id"][-1] == "ToolMessage":
        print(f'Tool: {message["kwargs"]["name"]}')
        print(f'Result: {message["kwargs"]["content"]}\n')
    else:
        print(message["kwargs"]["content"] + "\n")


def load_config(section: str | None = None) -> dict:
    config = tomllib.loads((Path(__file__).parent / "config.toml").read_text())
    if section is not None:
        return config[section]
    else:
        return config
