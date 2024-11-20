# AgentSec (WIP)
An experimental specification for a secure multi-agent system that combines both institutional secrecy practices and programmatic security measures.
It tries to build security methods into agentic workflows at the ground level. 

What's this about? [See the white paper](https://github.com/N8sGit/agent_sec_white_paper)

## tl;dr
I want to see if it's possible to build a multi-agent system like a top-secret organization, that implements multiple layers of security and prevents leaks and provides a framework for handling sensitive data.

For example: certain information points could be labeled "classified", and encrypted, and only read by agents with appropriate clearance levels. 

Another mechanism is a block-chain like "signature" mechanism where high priority instructions must be formally authorized by the approving agencies- this is to protect against prompt injection attacks. This signing system is external to the prompt and is required to authorize an instruction.

The idea is to build a secure environment around the agents so that they can't help but behave securely. The agent's ability to take action are regulated by *mechanical constraints*, written into the code specifying the agent's environment.  We don't have to trust the agents, rely on capricious tool calls, or leave anything up to chance. 

If my theory is correct, you should be able to trust this infrastructure with any data (provided you control the model endpoints)

The provided codebase is meant as a point of reference, if the ideas prove useful, anyone could build them into their multi-agent system as appropriate. 

Bit of a moonshot, but worth a try. My entry for the Berkeley [LLM Agents Hackathon](https://rdi.berkeley.edu/llm-agents-hackathon/)

### To run:
(Running the code is not recommended yet; still working out the details.) But if you wish to, for the authenticated user the the username is n and the password is p
But when it's ready :
1. Create a .env file, add OPEN_API_KEY for whatever model you wish to use. (Currently using OpenAI but will change this to be generic soon as it shouldn't matter)
2. In the terminal at the root directory and run ```python security\generate_rsa``` this will generate rsa keys and save them to security/keys
3. In the root directory run ```python security\generate_secrets.py``` this will generate secret and salt values and log them to the terminal. Add the secret value to the .env as SECRET_KEY and the SALT_VALUE in .env
4. Have docker installed
5. build the docker image ```docker build -f Dockerfile -t autogen_base_img .```
6. Run the dockerfile ```docker run -it -v [path_to_your_directory]:/home/autogen/autogen/myapp autogen_base_img:latest python3 /home/autogen/autogen/myapp/main.py```
7. Log in as the user, current username is n, password is p. Issue your command and specify a clearance level

### Note: I am not a cybersec specialist. The way various authentication measures are handled in this project are for demo purpose only. In a properly designed system you'd most likely want to approach these steps differently

### Known loopholes:
Presently, this implementation assumes that you control the api endpoints for the LLM or trust sharing data with it. It should do a better job protecting the spaces in between those endpoints. But ultimately, all data must be passed unwrapped and exposed to the LLM for the model to properly tokenize and process it. 

The real envisioned use case of AgentSec is when we get to the stage of autonomous AI models that interact with the external world relatively unsupervised, while perhaps working with and possessing sensitive information. 

We want the most sensitive information to always be siloed to a secure kernel layer (that interfaces only with the authenticated user via the core agent), preventing any external tampering with the instruction hierarchy or information leaks at the outward facing, effectuator layers, that could encounter threat actors "in the wild."

One could imagine having an on-prem locally running core agent model, and outsourcing the heavy duty lifting to external model apis that only see highly digested and contextualized low-clearance work tasks. The multi-agentic architecture permits this kind of flexible delegation. 
