from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

class RetrievalService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict]:
        query_embedding = self.embedding_service.generate_embeddings(
            [query]
        )[0]

        return self.qdrant_service.search(
            query_embedding=query_embedding,
            limit=limit,
        )