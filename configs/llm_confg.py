import os
from dotenv import load_dotenv
load_dotenv()
api_key = api_key =  os.getenv("OPENAI_API_KEY")

llm_config = {
    "config_list": [{"model": "gpt-4", "api_key": api_key}],
    'seed': 42,
    'temperature': 0,
    'timeout': 600
}