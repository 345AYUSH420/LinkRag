from langgraph.graph import StateGraph
from langchain_community.document_loaders import WebBaseLoader
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.vectorStore import setup_vector_store
import utils.graph_config as graph_config
from utils.state import GraphState
from utils.nodes import retrieve_node, generate_node
url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
loader = WebBaseLoader(url)
data = loader.load()

retriever = setup_vector_store(data, url)

graph = StateGraph(GraphState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_edge("retrieve", "generate")
graph.set_entry_point("retrieve")
graph.set_finish_point("generate")

app = graph.compile()
app.get_graph().print_ascii()

while True:
    question = input("Enter your question (or type 'exit' to quit): ").strip()

    if question.lower() in ["exit", "quit"]:
        break

    state = GraphState(question=question , retriever=retriever)
    app.invoke(state)
