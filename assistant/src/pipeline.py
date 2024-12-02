import os

from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import FARMReader  # You can use TransformersReader too
from haystack.nodes import BM25Retriever
from haystack.pipelines import ExtractiveQAPipeline
from src.core.settings import ElasticsearchSettings

# Initialize Elasticsearch Document Store
settings = ElasticsearchSettings()
index = os.environ["ELASTIC_INDEX_NAME_MOVIES"]
document_store = ElasticsearchDocumentStore(
    host=settings.host, port=settings.port, username="", password="", index=index
)

# Initialize Retriever
retriever = BM25Retriever(document_store=document_store)

# Optionally add a Reader for better answers
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2")
pipeline = ExtractiveQAPipeline(reader=reader, retriever=retriever)
