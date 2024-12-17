# A LangGraph LLM app template with function calling capabilities  

Table of Contents:  
* [Short introductory description](#deployable-on-ibm-cloud-powered-by-watsonxai)  
* [Prerequisites](#prerequisites)  
* [Cloning and setting up the template locally](#cloning-and-setting-up-the-template-locally)  
* [Modifying and configuring the template](#modifying-and-configuring-the-template)  
  * [Configuration file](#config-file)  
  * [Providing additional key-value data to the app](#)
  * [Handling external credentials](#handling-external-credentials)  
  * [LangGraph's graph architecture](#langgraphs-graph-architecture)  
  * [Core app logic](#core-app-logic)  
  * [Adding new tools](#adding-new-tools)  
  * [Enhancing tests suite](#enhancing-unit-tests-suite)  
* [Unit testing the template](#unit-testing-the-template)  
* [Executing the app locally](#executing-the-app-locally)  
* [Deploying on Cloud](#deploying-on-cloud)
* [Querying the deployment](#querying-the-deployment)  


## Deployable on IBM Cloud, powered by Watsonx.ai

The repository should serve as an easily extensible skeleton for LLM apps deployable as an _ai-service_ on IBM Cloud
environment.

This particular example presents a simple calculator app with external tools covering more advanced maths and statistics
problems and use cases that the model itself might have problems getting right.

The high level structure of the repository is as follows (included are only the most important files):

langgraph-react-agent  
 ┣ src  
 ┃ ┣ langgraph_react_agent [(1)]  
 ┃ ┃ ┣ \_\_init\_\_.py  
 ┃ ┃ ┣ agent.py (2)
 ┣ **ai_service.py**  (3)  
 ┣ config.toml  (4)  
 ┣ pyproject.toml  

(1) any auxiliary files used by the deployed function. Packaged and sent to IBM Cloud during deployment as [package extension](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/ml-create-custom-software-spec.html?context=wx&audience=wdp#custom-wml)  
(2) includes the LangGraph graph, models and agents definition   
(3) includes the core logic of the app --- the function to be deployed on IBM Cloud,   
(4) a configuration file storing deployment metadata and tweaking the model  

We advise following these steps to quickly have the app up & running on IBM Cloud.  

### Prerequisites  
This template uses [Poetry](https://python-poetry.org/) package manager. Due to its recommended [installation procedure](https://python-poetry.org/docs/#installation) a [Pipx](https://github.com/pypa/pipx) should be **installed and available** on the system.  

For tips on how to ensure _Pipx_ on your system please follow [its official docs](https://github.com/pypa/pipx?tab=readme-ov-file#install-pipx).  


### Cloning and setting up the template locally  

In order not to clone the whole `IBM/watson-machine-learning-samples` repository we'll use git's shallow and sparse cloning feature to checkout only the template's directory:  

```sh
git clone --no-tags --depth 1 --single-branch --filter=tree:0 --sparse git@github.com:IBM/watson-machine-learning-samples.git
cd watson-machine-learning-samples
git sparse-checkout add cloud/ai-service-templates/
```

From now on it'll be considered that the working directory is `watson-machine-learning-samples/cloud/ai-service-templates/langgraph-react-agent`  


### Ensure Poetry installation  
```sh
pipx install --python 3.11 poetry
```

### Installing the template  
Running the below commands will install the repository in a separate virtual environment  

```sh
poetry install
```

### Activating the newly created environment in your shell  

```sh
source $(poetry -q env use 3.11 && poetry env info --path)/bin/activate
```

### Exporting PYTHONPATH
Adding working directory to PYTHONPATH is necessary for the next steps. In your terminal execute:  
```sh
export PYTHONPATH=$(pwd):${PYTHONPATH}
```

## Modifying and configuring the template  

### Config file  
There is a [config.toml](config.toml) file that should be filled in before deploying the template on Cloud. It can also be used to customise the model for local runs.  
Possible config parameters are given in the provided file and explained using comments (when necessary).  

### Providing additional key-value data to the app  

There exists a special asset that could be created from within the deployment space called _Parameter Sets_. Instantiating it and later referencing from code can be easily achieved using the _watsonx.ai_ library.  
The implementation and usage is up to the user. For detailed description and API please refer to the [watsonx.ai Parameter Set's docs](https://ibm.github.io/watsonx-ai-python-sdk/core_api.html#parameter-sets).  

### Handling external credentials  

Sensitive data should not be passed unencrypted, e.g. in the configuration file. The recommended way to handle them is to make use of the [IBM Cloud® Secrets Manager](https://cloud.ibm.com/apidocs/secrets-manager/secrets-manager-v2). The exact way of integrating the Secrets Manager's API with the app is for the user to decide on.  

### LangGraph's graph architecture  

The [agent.py](src/langgraph_react_agent/agent.py) file builds app the graph consisting of nodes and edges. The former define the logic for agents while the latter control the logic flow in the whole graph.  

For detailed info on how to modify the graph object please refer to [LangGraph's official docs](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/#create-graph)  

### Core app logic  

The [ai_service.py](ai_service.py) file encompasses the functions to be deployed on IBM Cloud environment.

They make use of the LangGraph's compiled graph and define the app's logic as well as input schema definition for `/ai_service` endpoint query.  
They also include code responsible for authenticating the user to the IBM Cloud, ensure the deployment environment and store its metadata.  

For a detailed breakdown of the ai-service's implementation please refer the [IBM Cloud docs](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/ai-services-create.html?context=wx)  

### Adding new tools  

[tools.py](src/langgraph_react_agent/tools.py) file stores the definition for tools enhancing the chat model's capabilities.  
In order to add new tool create a new function, wrap it with the `@tool` decorator and add to the `TOOLS` list in the `extensions` module's [__init__.py](src/langgraph_react_agent/__init__.py)

For more sophisticated use cases (like async tools), please refer to the [langchain docs](https://python.langchain.com/docs/how_to/custom_tools/#creating-tools-from-runnables).  

### Enhancing unit tests suite  
The `tests/` directory's structure resembles the repository. Adding new tests should follow this convention.  
Currently, for exemplary purposes, tools and some general utility functions are covered with unit tests.  

## Unit-testing the template  
Running the below command will execute the whole tests suite:
```sh
pytest -r 'fEsxX' tests/
```


## Executing the app locally  
It is possible to run (or even debug) the ai-service locally, however it still requires creating the connection to the IBM Cloud.  
In order to execute the function to be deployed within your local environment:  
1) populate the `config.toml` file with any necessary credentials,  
2) run the `examples/execute_ai_service_locally.py` script using:  
    ```sh
    python examples/execute_ai_service_locally.py
    ```
3) choose from some pre-defined questions or ask the model your own  
  Please bear in mind that in order for the model to invoke its tools the questions should revolve around fitting Linear Regression to some user-defined data  


## Deploying on Cloud  

1) populate the `config.toml` file with your necessary credentials (if not already done for the purpose of local testing)  
2) run the `scripts/deploy.py` file using:  
    ```sh
    python scripts/deploy.py
    ```
3) Successfully completed script will print on stdout the `deployment_id` which will be necessary to test the deployment. For further info please refer [to the next section](#querying-the-deployment)  

## Querying the deployment  

The exemplary file [query_existing_deployment.py](examples/query_existing_deployment.py) shows how to test the existing deployment using `watsonx.ai` library.   
In order to do so you'll need to initialise the `deployment_id` variable that can be found at the beginning of the file.  
The _deployment_id_ of your deployment can be obtained from [the previous section](#deploying-on-cloud) by running [scripts/deploy.sh](scripts/deploy.py)  

