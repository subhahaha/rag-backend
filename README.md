# RAG Backend

A backend-only Retrieval-Augmented Generation (RAG) application built with FastAPI. The system supports document ingestion, vector-based retrieval, conversational question answering, Redis-backed chat memory, and LLM-powered interview booking.

## Features

### Document Ingestion API

* Upload `.pdf` and `.txt` documents
* Extract text from uploaded files
* Select between two chunking strategies:

  * Recursive character chunking
  * Sentence-based chunking
* Generate embeddings using `all-MiniLM-L6-v2`
* Store embeddings and chunks in Qdrant
* Store document metadata in SQLite using SQLAlchemy
* Persist Qdrant data locally

### Conversational RAG API

* Custom RAG pipeline implemented
* Semantic retrieval from Qdrant
* LLM-generated answers using Groq
* Redis-backed conversation memory
* Multi-turn conversations using a `conversation_id`
* LLM-powered interview booking
* Collects:

  * Name
  * Email
  * Date
  * Time
* Stores completed bookings in SQLite

## Architecture

```text
                    ┌─────────────────────┐
                    │       FastAPI       │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
        Document Ingestion              Conversational RAG
                │                             │
                ▼                             ▼
         Text Extraction              Redis Chat Memory
                │                             │
                ▼                             ▼
            Chunking                  Booking Intent
                │                     & Field Extraction
                ▼                             │
           Embeddings                         │
                │                             ▼
                ▼                        SQLite Booking
             Qdrant
                │
                ▼
          Retrieved Context
                │
                ▼
             Groq LLM
                │
                ▼
              Answer
```

## Project Structure

```text
.
├── app/
│   ├── api/
│   │   ├── booking.py
│   │   └── chat.py
│   │
│   ├── llm/
│   │   └── client.py
│   │
│   ├── schemas/
│   │   ├── booking.py
│   │   └── chat.py
│   │
│   ├── services/
│   │   ├── booking_service.py
│   │   ├── chat_memory.py
│   │   ├── chunking_service.py
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── qdrant_service.py
│   │   ├── rag_service.py
│   │   └── retrieval_service.py
│   │
│   ├── config.py
│   └── main.py
│
├── database.py
├── models.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Technologies

* **Python 3.11**
* **FastAPI** — REST API framework
* **PyMuPDF** — PDF text extraction
* **LangChain Text Splitters** — recursive chunking
* **Sentence Transformers** — text embeddings
* **Qdrant** — vector database
* **SQLAlchemy + SQLite** — metadata and booking persistence
* **Redis / Memurai** — conversational memory
* **Groq** — LLM inference
* **Pydantic** — request schemas

## Setup

### 1. Clone or copy the project

Open a terminal in the project directory.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
source venv/Scripts/activate
```

Or in PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
GROQ_API_KEY=your_groq_api_key
```


### 5. Start Redis-compatible server

On Windows, this project was tested using Memurai.

Make sure the Redis-compatible server is running on:

```text
localhost:6379
```

### 6. Start the FastAPI server

From the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

```http
GET /
```

Returns:

```json
{
  "message": "RAG Backend is running"
}
```

### Document Upload

```http
POST /documents/upload
```

Form fields:

* `file` — `.pdf` or `.txt`
* `chunking_strategy` — `recursive` or `sentence`

Example:

```text
chunking_strategy=recursive
```

The document is:

1. Read and converted to text
2. Split into chunks
3. Converted into embeddings
4. Stored in Qdrant
5. Recorded in the SQL metadata database

### Document Search

```http
GET /documents/search?query=your question
```

Returns the most semantically similar document chunks from Qdrant.

### Conversational RAG

```http
POST /chat/
```

Request:

```json
{
  "conversation_id": "conversation-1",
  "question": "How many days of annual leave do employees get?"
}
```

The `conversation_id` identifies the conversation and allows previous messages to be retrieved from Redis.

### Interview Booking

Interview booking is handled conversationally through:

```http
POST /chat/
```

Example flow:

```text
User:
I'd like to arrange an interview. My name is abc and my email is abc@example.com.

Assistant:
What date would you like to schedule the interview?

User:
September 20, 2026

Assistant:
What time would you prefer?

User:
10:00 AM

Assistant:
Thank you! Your interview has been booked successfully.
```

The LLM is used to:

* Detect booking intent
* Extract booking fields from natural-language messages

Redis temporarily stores the booking information during the conversation.

Once all required fields are collected, the booking is persisted in SQLite.

## RAG Flow

The conversational RAG pipeline follows this process:

```text
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Qdrant Similarity Search
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Combine Retrieved Context
      │
      ▼
Add Conversation History
      │
      ▼
Send Context + Question to LLM
      │
      ▼
Generate Answer
      │
      ▼
Store Conversation in Redis
```

The RAG pipeline is implemented manually.

## Chunking Strategies

### Recursive Chunking

Uses a recursive text splitter with:

* Chunk size: 500 characters
* Chunk overlap: 50 characters

This attempts to preserve meaningful text boundaries while keeping chunks within the configured size.

### Sentence Chunking

The document is split into individual sentences using sentence-ending punctuation.

The strategy can be selected when uploading the document.

## Data Storage

### Qdrant

Stores:

* Chunk text
* Embedding vectors
* Filename
* Chunk index

The local Qdrant data is stored in:

```text
qdrant_data/
```

### SQLite

Stores document metadata:

* Filename
* File type
* Chunking strategy
* Number of chunks
* Creation timestamp

It also stores completed interview bookings:

* Name
* Email
* Date
* Time
* Creation timestamp

### Redis

Stores:

* Conversation messages
* Temporary interview booking fields

Completed booking information is persisted to SQLite and the temporary booking state is removed from Redis.



The application uses Qdrant for vector retrieval and a custom RAG pipeline.

## Future Improvements

Possible future improvements include:

* Stronger email/date/time validation for interview bookings
* More robust handling of ambiguous dates and times
* Automated tests for API endpoints and services
* Dockerization for easier deployment
* Production Redis/Qdrant configuration

## Security Notes

* API keys are loaded from environment variables.
* `.env` is excluded from version control.
* Local databases and Qdrant runtime data are excluded from version control.

