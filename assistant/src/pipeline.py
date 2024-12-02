import os

from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchEmbeddingRetriever,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)
from src.core.settings import ElasticsearchSettings

# Initialize Elasticsearch Document Store
settings = ElasticsearchSettings()
index = os.environ["ELASTIC_INDEX_NAME_MOVIES"]
document_store = ElasticsearchDocumentStore(hosts=settings.url, index=index)

# Initialize Retriever
retriever = ElasticsearchEmbeddingRetriever(document_store=document_store)

# Optionally add a Reader for better answers
# if nothing specified, model will be downloaded on startup
model = os.getenv("ASSISTANT_MODEL", "deepset/roberta-base-squad2")
text_embedder = SentenceTransformersTextEmbedder(model=model)

# Combine Retriever and Reader into a Pipeline
pipeline = Pipeline()
pipeline.add_component("text_embedder", text_embedder)
pipeline.add_component("retriever", retriever)
pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
