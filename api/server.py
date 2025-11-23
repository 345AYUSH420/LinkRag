from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI 
from dotenv import load_dotenv
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.vectorStore import setup_vector_store
import os

load_dotenv()

url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
loader = WebBaseLoader(url)
data = loader.load()

retriever = setup_vector_store(data , url)

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=0,
    openai_api_base="https://openrouter.ai/api/v1", 
    openai_api_key=os.getenv("OPENROUTER_API_KEY")   
)

parser = StrOutputParser()


while True:

    question = input("Enter your question (or type 'exit' to quit): ").strip()

    if question.lower() in ['exit', 'quit']:
        break
    results = retriever.invoke(question)

    prompt = PromptTemplate(

        template="refactor the following answer based on the context provided in just 100 words Context: {context} \n\n Question: {question} \n\n Answer:",
        input_variables=["context" , "question"],
    )

    chain = prompt | model | parser

    for chunk in chain.stream({
        "context": "\n".join([doc.page_content for doc in results]),
        "question": question}):
        print(chunk)






