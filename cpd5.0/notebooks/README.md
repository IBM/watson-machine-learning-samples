# Notebook tutorials
Sample notebooks demonstrating watsonx.ai capabilities like:
- running model building AutoAI or Deep Learning experiments
- deploying 3rd party models as web services or batch jobs (i.e.: scikit-learn, xgboost, keras, PMMl, SPSS etc.)
- monitoring of deployments with OpenScale (drift, bias detection)
- model lifecycle management (update model version, refresh deployment)


Notebooks with python code and python SDK can be found under `python_sdk` folder.
The REST API examples are organized under `rest_api` folder.


## experiments
This folder contains examples of experiments done using **AutoAI** as well as Deep Learning ones.
Notebooks show how to trigger such experiment, work with trained models, do models comparison, refinery, and finally deployment.


## deployments
This folder contains examples of serving different types of models either as online or batch jobs.
The following 3rd party frameworks are covered:
- spark MLlib
- pmml
- SPSS
- scikit-learn
- xgboost
- keras
- tensorflow
- pytorch
- python functions


## monitoring
This folder contains examples of e2e scenarios on how to monitor ML models in production using Watson Machine Learning and Watson OpenScale services.
Notebooks show how you can detect bias and drift in your data and ML models.


## lifecycle management
This folder contains examples of notebooks which shows how to update existing model version and refresh existing deployment in-place.
