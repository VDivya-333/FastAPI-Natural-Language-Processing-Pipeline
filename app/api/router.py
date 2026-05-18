import uuid
import logging
import json
import httpx 
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends

from fastapi.concurrency import run_in_threadpool
from typing import List, Any, Optional
from sqlalchemy.orm import Session

from app.api.request_schema import TextRequest, BatchTextRequest
from app.api.response_schema import NLPResponse, BatchNLPResponse
from app.schemas.response_schema import RagRetrieveRequest, RagRetrieveResponse
from app.services import nlp_service
from app.api.task_model import Task
from app.api.session import get_db, get_session_local
from app.services.cache_service import redis_client, CacheService
from app.rag.retriever import retrieve_documents, store_documents

logger = logging.getLogger(__name__)
api_router = APIRouter()

# Task Status Constants
TASK_STATUS_PENDING = "PENDING"
TASK_STATUS_PROCESSING = "PROCESSING"
TASK_STATUS_COMPLETED = "COMPLETED"
TASK_STATUS_FAILED = "FAILED"

# --- Utility / Health Endpoints ---

@api_router.get("/health")
async def health_check():
    """Basic health check for the API."""
    redis_healthy = CacheService.is_healthy()
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "service": "NLP RAG Pipeline",
        "redis": "connected" if redis_healthy else "disconnected"
    }

async def run_nlp_task(task_id: str, task_type: str, text_data: Any, webhook_url: Optional[str] = None):
    """
    Handles the background execution of NLP tasks.
    """
    logger.info(f"Task {task_id}: Starting {task_type}. Webhook: {webhook_url}")
    session_factory = get_session_local()
    db = session_factory()
    results = None
    try:
        if isinstance(text_data, list):
            results = await nlp_service.batch_process_task(task_type, text_data)
        else:
            mapping = {
                "summarize": nlp_service.summarize_text,
                "sentiment": nlp_service.sentiment_analysis,
                "classify": nlp_service.classify_text,
                "entities": nlp_service.extract_entities
            }
            results = await run_in_threadpool(mapping[task_type], text_data)

        # Update task in DB
        task_record = db.query(Task).filter(Task.task_id == task_id).first()
        if task_record:
            task_record.status = TASK_STATUS_COMPLETED
            task_record.result = json.dumps(results)
            db.commit()

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        task_record = db.query(Task).filter(Task.task_id == task_id).first()
        if task_record:
            task_record.status = TASK_STATUS_FAILED
            task_record.result = json.dumps({"error": str(e)})
            db.commit()
        results = {"error": str(e)}
    finally:
        db.close()

    payload = {
        "task_id": task_id,
        "status": TASK_STATUS_COMPLETED if "error" not in results else TASK_STATUS_FAILED,
        "result": results if "error" not in results else None
    }

    # Trigger Webhook Notification
    if webhook_url:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload, timeout=10.0)
                logger.info(f"Task {task_id}: Webhook sent to {webhook_url}. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Task {task_id}: Webhook failed for {webhook_url}: {e}")

    return payload

# --- Individual NLP Endpoints ---

@api_router.post("/classification", response_model=NLPResponse)
async def classify_endpoint(request: TextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            task_type="classify",
            status=TASK_STATUS_PENDING,
            input_text=request.text[:500]
        )
        db.add(new_task)
        db.commit()

        background_tasks.add_task(run_nlp_task, task_id, "classify", request.text, request.webhook_url)
        return NLPResponse(task_id=task_id, status=TASK_STATUS_PROCESSING)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.post("/entities", response_model=NLPResponse)
async def entities_endpoint(request: TextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            task_type="entities",
            status=TASK_STATUS_PENDING,
            input_text=request.text[:500]
        )
        db.add(new_task)
        db.commit()

        background_tasks.add_task(run_nlp_task, task_id, "entities", request.text, request.webhook_url)
        return NLPResponse(task_id=task_id, status=TASK_STATUS_PROCESSING)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.post("/summarization", response_model=NLPResponse)
async def summarize_endpoint(request: TextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            task_type="summarize",
            status=TASK_STATUS_PENDING,
            input_text=request.text[:500] # store snippet
        )
        db.add(new_task)
        db.commit()

        background_tasks.add_task(run_nlp_task, task_id, "summarize", request.text, request.webhook_url)
        return NLPResponse(task_id=task_id, status=TASK_STATUS_PROCESSING)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.post("/sentiment", response_model=NLPResponse)
async def sentiment_endpoint(request: TextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            task_type="sentiment",
            status=TASK_STATUS_PENDING,
            input_text=request.text[:500]
        )
        db.add(new_task)
        db.commit()

        background_tasks.add_task(run_nlp_task, task_id, "sentiment", request.text, request.webhook_url)
        return NLPResponse(task_id=task_id, status=TASK_STATUS_PROCESSING)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# --- Batch NLP Endpoints --- 

@api_router.post("/batch/classification", response_model=BatchNLPResponse)
async def batch_classify_endpoint(request: BatchTextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            task_type="batch_classify",
            status=TASK_STATUS_PENDING,
            input_text=f"Batch of {len(request.texts)}"
        )
        db.add(new_task)
        db.commit()

        background_tasks.add_task(run_nlp_task, task_id, "classify", request.texts, request.webhook_url)
        return BatchNLPResponse(task_id=task_id, status=TASK_STATUS_PROCESSING, total_processed=len(request.texts))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.post("/batch/sentiment", response_model=BatchNLPResponse)
async def batch_sentiment_endpoint(request: BatchTextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            task_type="batch_sentiment",
            status=TASK_STATUS_PENDING,
            input_text=f"Batch of {len(request.texts)}"
        )
        db.add(new_task)
        db.commit()

        background_tasks.add_task(run_nlp_task, task_id, "sentiment", request.texts, request.webhook_url)
        return BatchNLPResponse(task_id=task_id, status=TASK_STATUS_PROCESSING, total_processed=len(request.texts))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.post("/batch/entities", response_model=BatchNLPResponse)
async def batch_entities_endpoint(request: BatchTextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            task_type="batch_entities",
            status=TASK_STATUS_PENDING,
            input_text=f"Batch of {len(request.texts)}"
        )
        db.add(new_task)
        db.commit()

        background_tasks.add_task(run_nlp_task, task_id, "entities", request.texts, request.webhook_url)
        return BatchNLPResponse(task_id=task_id, status=TASK_STATUS_PROCESSING, total_processed=len(request.texts))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.post("/batch/summarization", response_model=BatchNLPResponse)
async def batch_summarization_endpoint(request: BatchTextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            task_type="batch_summarize",
            status=TASK_STATUS_PENDING,
            input_text=f"Batch of {len(request.texts)}"
        )
        db.add(new_task)
        db.commit()

        background_tasks.add_task(run_nlp_task, task_id, "summarize", request.texts, request.webhook_url)
        return BatchNLPResponse(task_id=task_id, status=TASK_STATUS_PROCESSING, total_processed=len(request.texts))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# --- Generic Task Submit --- 

@api_router.post("/tasks/submit", response_model=NLPResponse)
async def submit_task_generic(task_type: str, request: TextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Generic endpoint to submit any NLP task type asynchronously.
    """
    task_type_mapping = {
        "classification": "classify",
        "classify": "classify",
        "entities": "entities",
        "summarization": "summarize",
        "summarize": "summarize",
        "sentiment": "sentiment",
        "sentiment_analysis": "sentiment"
    }
    
    normalized_task_type = task_type_mapping.get(task_type.lower())
    if not normalized_task_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid task type: {task_type}. Expected one of: {', '.join(task_type_mapping.keys())}")

    try:
        task_id = str(uuid.uuid4())
        new_task = Task(
            task_id=task_id,
            task_type=normalized_task_type, # Store normalized type in DB
            status=TASK_STATUS_PENDING,
            input_text=request.text[:500]
        )
        db.add(new_task)
        db.commit()
        background_tasks.add_task(run_nlp_task, task_id, normalized_task_type, request.text, request.webhook_url)
        return NLPResponse(task_id=task_id, status=TASK_STATUS_PROCESSING)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# --- Task Status Endpoint ---

@api_router.get("/tasks/{task_id}")
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the current status and result of a background task.
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result_data = json.loads(task.result) if task.result else None

    # If it's a completed batch task with the new results format, return it directly
    if task.status == TASK_STATUS_COMPLETED and isinstance(result_data, dict) and "results" in result_data:
        return result_data

    return NLPResponse(
        task_id=task.task_id,
        status=task.status,
        result=result_data
    )

# --- RAG Endpoints ---

@api_router.post("/rag/retrieve", response_model=RagRetrieveResponse)
async def rag_retrieve(request: RagRetrieveRequest):
    """Retrieves similar documents based on the input text."""
    try:
        results = retrieve_documents(request.query, top_k=request.top_k)
        return RagRetrieveResponse(query=request.query, results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@api_router.post("/rag/store")
async def rag_store(request: TextRequest):
    """Stores text embeddings into the vector database."""
    try:
        doc_id = store_documents(request.text)
        return {"status": "success", "message": "Content indexed successfully", "id": doc_id}
    except Exception as e:
        logger.error(f"RAG storage failed: {e}")
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")

# --- Cache Endpoints --- 

@api_router.get("/cache/stats")
async def get_cache_stats():
    """Returns statistics about the Redis cache."""
    try:
        info = redis_client.info()
        return {
            "uptime_in_seconds": info.get("uptime_in_seconds"),
            "used_memory_human": info.get("used_memory_human"),
            "hits": info.get("keyspace_hits"),
            "misses": info.get("keyspace_misses")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}