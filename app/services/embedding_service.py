from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self) -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts)

        return embeddings.tolist()



