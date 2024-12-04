Version 0.1.2
-------------
Addressed general feedback received on the template:

- changed template name to `langgraph-react-agent`
- enhanced documentation, mainly added more links and elaborated on some aspects (like credential management), 
- added a possibility to keep the conversation going with the WatsonxChat after asking the first question
- WatsonxChat now should remember previous conversations (within same deployment)

Version 0.1.1
-------------
- enhanced logging in scripts 
- restructured template files' hierarchy -- it's recommended now to define your graph implementation in `src/*/agent.py` file
- the script for testing the ai-service function locally is now much more interactive allowing to choose from multiple exemplary questions and datasets
- small fixes to code and docs

Version 0.1.0
-------------

Initial release