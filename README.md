# AgentSec (WIP)
An experimental specification for a secure multi-agent system that combines both institutional secrecy practices and programmatic security measures.
What's this about? [See the white paper](https://github.com/N8sGit/agent_sec_white_paper)

## tl;dr
I want to see if it's possible to build a multi-agent system like a top-secret organization, that implements multiple layers of security and prevents leaks and provides a framework for handling sensitive data.

For example: certain information points could be labeled "classified", and encrypted, and only read by agents with appropriate clearance levels. 

Another mechanism is a block-chain like "signature" mechanism where high priority instructions must be formally authorized by the approving agencies- this to ostensibly protect against prompt injection attacks... this signing system is external to the prompt.

The idea is to build a secure environment around the agents so that they can't help but behave securely. We don't have to trust the agents or leave anything up to chance. 

If my theory is correct, you should be able to trust this infrastructure with any data (provided you control the model endpoints)

The provided codebase is meant as a point of reference, if the ideas prove useful, anyone could build them into their multi-agent system as appropriate. 

Bit of a moonshot, but worth a try. My entry for the Berkeley [LLM Agents Hackathon](https://rdi.berkeley.edu/llm-agents-hackathon/)

### To run:
(Don't try yet; still working out the details conceptually.)
But when it does:
1. Have docker installed
2. build the docker image ```docker build -f Dockerfile -t autogen_base_img .```
3. Run the dockerfile ```docker run -it -v [path_to_your_directory]:/home/autogen/autogen/myapp autogen_base_img:latest python3 /home/autogen/autogen/myapp/main.py```
