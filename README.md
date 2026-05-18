# Test-A_FastAPI-Natural-Language-Processing-Pipeline
# NLP RAG Pipeline

A high-performance, asynchronous NLP and Retrieval-Augmented Generation (RAG) API built with FastAPI. This service provides specialized NLP tasks (classification, sentiment analysis, entity extraction, summarization) and a robust vector search system using ChromaDB.

## Features

*   **Asynchronous NLP Tasks:** Background execution for long-running NLP processes using FastAPI BackgroundTasks.
*   **Batch Processing:** Support for processing multiple text inputs in a single request.
*   **Retrieval-Augmented Generation (RAG):** Document ingestion and similarity search powered by ChromaDB and OpenAI embeddings.
*   **Webhooks:** Automated notification system to alert external services upon task completion.
*   **Caching:** Redis-backed caching service for improved performance.
*   **Persistence:** Task tracking and status management using MySQL and SQLAlchemy.
*   **Degraded Mode:** Graceful startup even if the database is temporarily unavailable.

## Tech Stack

*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
*   **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
*   **Database:** MySQL
*   **Vector Store:** [ChromaDB](https://www.trychroma.com/)
*   **Cache:** Redis
*   **LLM/Embeddings:** OpenAI API

## Prerequisites

*   Python 3.9+
*   MySQL Server
*   Redis Server
*   ChromaDB (running as a service or local instance)
*   OpenAI API Key

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd testA_nlp_RAG
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=your_openai_key
    OPENAI_BASE_URL=https:
    
    MYSQL_DB=nlp_db
    MYSQL_USER=user
    MYSQL_PASSWORD=password
    MYSQL_HOST=localhost
    MYSQL_PORT=3306
    
    REDIS_HOST=localhost
    REDIS_PORT=6379

    CHROMA_HOST=localhost
    CHROMA_PORT=8001
    ```

## Running the Application

Start the API server using uvicorn:

```bash
uvicorn app.api.main:app --reload
```

The API will be available at `http://localhost:8000`. You can access the interactive Swagger documentation at `http://localhost:8000/docs`.

## API Endpoints

### NLP Tasks
Submit tasks for asynchronous processing.
*   `POST /classification`: Classify text content.
*   `POST /sentiment`: Analyze sentiment of text.
*   `POST /summarization`: Generate text summaries.
*   `POST /entities`: Extract named entities.
*   `POST /batch/*`: Batch versions of the above endpoints.

### RAG Operations
*   `POST /rag/store`: Index text documents into the vector database.
*   `POST /rag/retrieve`: Search for relevant documents based on a query.

### Task Management
*   `GET /tasks/{task_id}`: Check the status and retrieve results of a background task.

### System Health
*   `GET /health`: Check the status of API and Redis connection.
*   `GET /cache/stats`: View Redis cache performance metrics.

## Project Structure

```text
app/
├── api/            # API routes, schemas, and database models
├── core/           # Configuration, logging, and constants
├── db/             # Database session management
├── rag/            # Vector store and retrieval logic
├── services/       # External service integrations (LLM, Embedding, Cache)
└── schemas/        # Pydantic data models
```

## License

MIT License
