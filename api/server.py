from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI 
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
loader = WebBaseLoader(url)
data = loader.load()

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=0,
    openai_api_base="https://openrouter.ai/api/v1",  # OpenRouter endpoint
    openai_api_key=os.getenv("OPENROUTER_API_KEY")   # Your OpenRouter API key from .env
)
prompt = PromptTemplate(

    template="answer the following {question} from the {page_content}", input_variables=["question" , "page_content"]
)
parser = StrOutputParser()

chain = prompt|model|parser

question = input("Enter your question: ")

print(chain.invoke({"page_content": data[0].page_content, "question": {question }}))
