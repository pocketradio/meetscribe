from langchain_aws import ChatBedrock
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    return ChatBedrock(
        model_id="us.meta.llama3-2-90b-instruct-v1:0",
        region_name="us-east-1"
    )