import os

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.pipeline import pipeline

app = FastAPI(
    title="Assistant",
    description="Description",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)
try:
    file_size = os.path.getsize("/var/run/llm/roberta-base-squad2/tf_model.h5")
    print(file_size)
except Exception as e:
    print(e)


# Define a request schema
class QueryRequest(BaseModel):
    query: str


@app.post("/search")
async def search(query_request: QueryRequest):
    query = {"text_embedder": {"text": query_request.query}}
    try:
        # Perform the query using Haystack
        result = pipeline.run(query)
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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
