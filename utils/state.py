
from pydantic import BaseModel


class GraphState(dict):
    question: str
    context: str
    stream: str
    retriever: any

class Query(BaseModel):
    url: str
    question: str
