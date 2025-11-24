from fastapi import FastAPI
from langgraph.graph import StateGraph
from langchain_community.document_loaders import WebBaseLoader
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.vectorStore import setup_vector_store
from utils.state import GraphState , Query
from utils.nodes import retrieve_node, generate_node
from langchain_core.documents import Document
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow all origins - or restrict for safety
    allow_credentials=True,
    allow_methods=["*"],          # allow POST, GET, OPTIONS, etc
    allow_headers=["*"],          # allow all headers
)
@app.post("/ask")
def ask(query: Query):
    loader = WebBaseLoader(query.url)
    data = loader.load()
    html_text = data[0].page_content

    doc = Document(page_content=html_text, metadata={"source": query.url})
    retriever = setup_vector_store([doc], query.url)

    graph = StateGraph(GraphState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_edge("retrieve", "generate")
    graph.set_entry_point("retrieve")
    graph.set_finish_point("generate")

    app_graph = graph.compile()

    state = GraphState(question=query.question, retriever=retriever)
    result = app_graph.invoke(state)

    return StreamingResponse(
        result["stream"],  # generator
        media_type="text/plain"
    )