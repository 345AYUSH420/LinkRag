from utils.state import GraphState
from utils.graph_config import model, parser
from langchain_core.prompts import PromptTemplate

def retrieve_node(state: GraphState):
    question = state["question"]
    results = state['retriever'].invoke(question)
    state["context"] = "\n".join([doc.page_content for doc in results])
    return state

def generate_node(state: GraphState):
    prompt = PromptTemplate(
        template=(
            "Refactor the answer based on the context in ~100 words. "
            "If the context is missing or irrelevant, respond politely that you cannot help.\n\n"
            "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        ),
        input_variables=["context", "question"]
    )

    chain = prompt | model | parser

    print("\n--- Streaming ---\n")
    for chunk in chain.stream({
        "context": state["context"],
        "question": state["question"]
    }):
        print(chunk, end="", flush=True)
    print("\n-----------------\n")

    return state
