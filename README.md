# AgentSec (WIP)
An experimental design for a secure multi-agent system that combines both institutional secrecy practices and programmatic security measures.
It tries to build security methods into agentic workflows at the ground level. 

What's this about? [See the white paper](https://github.com/N8sGit/agent_sec_white_paper). Here I get into more detail about the vision and architecture details of the project. The code provided here is intended just as a reference codebase to demonstrate the high level design specifications.

## High level summary:
I want to see if it's possible to build a multi-agent system like a top-secret organization, that implements multiple layers of security and prevents leaks and provides a framework for handling sensitive data.

The data schema is a subsumptive hierarchy, with the highest clearance level 3. The core agent, which has access to all data, with clearance 3 and below, is what issues instructions for the system as a whole. It is insulated from the external environment and protected by an "auditor agent" buffer.

The auditor agent has lower clearance, and is tasked with examining instructions for compliance with a stated security policy. It will edit and censor any instructions or data that does not comply. 

Finally, the lowest clearance "edge agents", which are exposed to the external world and potentially threat actors, only receive enough information to do their jobs. If compromised, they are isolated and unable to leak any sensitive data.

Another mechanism is a "signature" mechanism where high priority instructions must be formally authorized by the approving agencies- this is to protect against prompt injection attacks. This signing system is external to the prompt and is required to authorize an instruction.

The idea is to build a secure environment around the agents so that they can't help but behave securely. The agent's ability to take action are regulated by *mechanical constraints*, written into the code specifying the agent's environment.  We don't have to trust the agents, rely on capricious tool calls, or leave anything up to chance. 

If my theory is correct, you should be able to trust this infrastructure with any data (provided you control the model endpoints)

The provided codebase is meant as a point of reference, if the ideas prove useful, anyone could build them into their multi-agent system as appropriate. 

My entry for the Berkeley [LLM Agents Hackathon](https://rdi.berkeley.edu/llm-agents-hackathon/)

### To run:
But when it's ready :
1. Create a .env file, add OPENAI_API_KEY.
2. In the terminal at the root directory and run ```python security\generate_rsa``` this will generate rsa keys and save them to security/keys
3. In the root directory run ```python security\generate_secrets.py``` this will generate secret and salt values and log them to the terminal. Add the secret value to the .env as SECRET_KEY and the SALT_VALUE in .env
4. Run ``python -m data.generate_mock_data`` to generate the mock data. This data is "hospital themed" ... I recommend you study the contents of generate_mock_data.py to see what the content is.
5. Have docker installed
6. Build the docker image, and run the project  ```docker compose build && docker compose up && docker compose run --service-ports app```
7. This should expose port 8000 to a flask webserver. 
8. Navigate to localhost:8000 in the browser of your choice. This chat window is meant to be the interface for red teaming. Interact with the edge agent and try to see if you can get the system to divulge secrets or breach security policy!


### Note: I am not a cybersec specialist by trade. The way various authentication measures are handled in this project are for demo purpose only. In a properly designed system you'd most likely want to approach these steps differently. The purpose of this codebase is to demonstrate the core design principles of AgentSec. Everything else is an expedience. 

### Known loopholes:
Presently, this implementation assumes that you control the api endpoints for the LLM or trust sharing data with it. It should do a better job protecting the spaces in between those endpoints. But ultimately, all data must be passed unwrapped and exposed to the LLM for the model to properly tokenize and process it. 

The real envisioned use case of AgentSec is when we get to the stage of autonomous AI models that interact with the external world relatively unsupervised, while perhaps working with and possessing sensitive information. 

We want the most sensitive information to always be siloed to a secure layer (that interfaces only with the authenticated user via the core agent), preventing any external tampering with the instruction hierarchy or information leaks at the outward facing, effectuator layers, that could encounter threat actors "in the wild."

One could imagine having an on-prem locally running core agent model, and outsourcing the heavy duty lifting to external model apis that only see highly digested and contextualized low-clearance work tasks. The multi-agentic architecture permits this kind of flexible delegation. 
