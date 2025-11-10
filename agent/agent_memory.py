"""
# Arquivo de teste para o modelo de memória do agente.
Este script não será usado no projeto final, mas é mantido para referência e testes locais.
Modelo de teste de memória do agente. Neste caso, não foi utilizado devido ao consumo de recursos e à integração nativa que o CrewAI 
oferece com Mem0 + Qdrant. Este formato não foi testado, mas com base em análises teóricas, apresenta um consumo maior de recursos.


from crewai.memory.storage.interface import Storage
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, SearchParams
from sentence_transformers import SentenceTransformer
import uuid

class QdrantChatStorage(Storage):
    def __init__(self, user_id: str, host: str = "localhost", port: int = 6333):
        self.user_id = user_id
        self.client = QdrantClient(host=host, port=port)
        self.collection = "chat_memories"
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.client.collection_exists(self.collection):
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config={"size": 384, "distance": "Cosine"}
            )

    def save(self, value, metadata=None, agent=None):
        metadata = metadata or {}
        metadata["user_id"] = self.user_id
        metadata["agent"] = agent
        vector = self.embedder.encode(value).tolist()
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "value": value,
                "metadata": metadata,
                "user_id": self.user_id,
                "agent": agent
            }
        )
        self.client.upsert(collection_name=self.collection, points=[point])

    def search(self, query, limit=10, score_threshold=0.5):
        vector = self.embedder.encode(query).tolist()
        filter_by_user = Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=self.user_id)
                )
            ]
        )
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=filter_by_user,
            search_params=SearchParams(hnsw_ef=128)
        )
        return [
            {
                "value": r.payload.get("value"),
                "metadata": r.payload.get("metadata"),
                "agent": r.payload.get("agent")
            }
            for r in results
        ]

    def reset(self):
        self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=self.user_id)
                    )
                ]
            )
        )
"""