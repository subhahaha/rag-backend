from uuid import uuid4


from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

qdrant_client = QdrantClient(path="./qdrant_data")


class QdrantService:
    def __init__(self) -> None:
        self.client = qdrant_client

        self.collection_name = "documents"

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE,
                ),
            )

    def add_chunks(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        filename: str,
    ) -> None:
        points = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "filename": filename,
                        "chunk_index": index,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[dict]:
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit,
        ).points

        return [
            {
                "text": point.payload.get("text", ""),
                "filename": point.payload.get("filename", ""),
                "chunk_index": point.payload.get("chunk_index", 0),
                "score": point.score,
            }
            for point in results
        ]