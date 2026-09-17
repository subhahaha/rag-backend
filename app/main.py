from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.services.chunking_service import chunk_text
from app.services.document_service import extract_text
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.api.booking import router as booking_router

from database import engine, Base
import models
from database import SessionLocal
from models import Document
from app.api.chat import router as chat_router

Base.metadata.create_all(bind=engine)




app = FastAPI(title="RAG Backend")
app.include_router(chat_router)
app.include_router(booking_router)

embedding_service = EmbeddingService()
qdrant_service = QdrantService()


@app.get("/")
def root():
    return {"message": "RAG Backend is running"}


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: str = Form("recursive"),
):
    try:
        text = await extract_text(file)

        chunks = chunk_text(text, chunking_strategy)

        embeddings = embedding_service.generate_embeddings(chunks)

        qdrant_service.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
            filename=file.filename or "unknown",
        )

        db = SessionLocal()

        try:
            document = Document(
                filename=file.filename or "unknown",
                file_type=file.content_type or "unknown",
                chunking_strategy=chunking_strategy,
                num_chunks=len(chunks),
            )

            db.add(document)
            db.commit()
            db.refresh(document)

        finally:
            db.close()
            
        return {
            "filename": file.filename,
            "chunking_strategy": chunking_strategy,
            "total_characters": len(text),
            "total_chunks": len(chunks),
            "message": "Document processed and stored successfully",
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

@app.get("/documents/search")
def search_documents(query: str):
    query_embedding = embedding_service.generate_embeddings([query])[0]

    results = qdrant_service.search(
        query_embedding=query_embedding,
        limit=5,
    )

    return {
        "query": query,
        "results": results,
    }