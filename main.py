import autogen
import os
from dotenv import load_dotenv
load_dotenv()

api_key =  os.getenv("OPENAI_API_KEY")
llm_config = {
    "config_list": [{"model": "gpt-4", "api_key": api_key}],
    'seed': 42,
    'temperature': 0,
    'timeout': 600
}

assistant = autogen.AssistantAgent(
    name='assistant',
    llm_config=llm_config,
    system_message='This is a dry run to see if everything works: confirm that you have received this message'
)
# Team of agents. 

user_proxy = autogen.UserProxyAgent(
    name='user_proxy',
    human_input_mode='TERMINATE',
    max_consecutive_auto_reply=5,
    is_termination_msg=lambda x: x.get("content", '').rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": 'web' , "use_docker": False},
    llm_config=llm_config,
    system_message='example'
)

task = """
anything
"""

user_proxy.initiate_chat(assistant, message=task)
