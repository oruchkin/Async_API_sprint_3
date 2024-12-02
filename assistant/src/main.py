from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .pipeline import pipeline

app = FastAPI()


# Define a request schema
class QueryRequest(BaseModel):
    query: str


@app.post("/search")
async def search(query_request: QueryRequest):
    query = query_request.query
    try:
        # Perform the query using Haystack
        result = pipeline.run(query=query, params={"Retriever": {"top_k": 10}})
        return {
            "query": query,
            "answers": [
                {
                    "answer": answer.answer,
                    "score": answer.score,
                    "context": answer.context,
                }
                for answer in result["answers"]
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
