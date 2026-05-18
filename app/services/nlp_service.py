import json
import asyncio
from typing import List
from app.rag.pipeline import build_context
from app.services.llm_service import generate_completion
from app.services.cache_service import CacheService


def summarize_text(text: str):
    # 1. Check cache
    cache_key = CacheService.generate_key("summarize", text)
    cached_result = CacheService.get_cached_result(cache_key)
    if cached_result:
        return cached_result

    context = build_context(text)

    prompt = f"""
    Summarize the following text using the provided context.
    Return ONLY a single valid JSON object in this format:
    {{
      "summary": "the summary text"
    }}

    Context:
    {context}
    
    Text:
    {text}
    """

    raw_result = generate_completion(prompt, json_mode=True)
    result = json.loads(raw_result)
    
    # 2. Store in cache
    CacheService.set_cached_result(cache_key, result)
    return result

async def batch_process_task(task_type: str, texts: List[str]):
    """
    Scalable batch processing using thread pools for concurrent LLM requests.
    """
    task_mapping = {
        "summarize": summarize_text,
        "sentiment": sentiment_analysis,
        "classify": classify_text,
        "entities": extract_entities
    }
    func = task_mapping.get(task_type)

    # Convert synchronous function calls to awaitables in a thread pool for efficiency
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, func, text) for text in texts]
    raw_results = await asyncio.gather(*tasks)
    
    formatted_results = []
    for text, res in zip(texts, raw_results):
        item = {"text": text}
        if task_type == "classify":
            item["label"] = res.get("label", "unknown").lower()
        elif task_type == "sentiment":
            item["sentiment"] = res.get("sentiment", "neutral").lower()
        elif task_type == "summarize":
            item["summary"] = res.get("summary", "")
        elif task_type == "entities":
            item["entities"] = res.get("entities", [])
        else:
            # Fallback for generic tasks
            item.update(res if isinstance(res, dict) else {"result": res})
        
        formatted_results.append(item)
    
    return {"results": formatted_results}


def sentiment_analysis(text: str):
    # 1. Check cache
    cache_key = CacheService.generate_key("sentiment", text)
    cached_result = CacheService.get_cached_result(cache_key)
    if cached_result:
        return cached_result

    context = build_context(text)

    prompt = f"""
    Identify ONLY the single most appropriate sentiment (positive, negative, or neutral) for the text below.
    You MUST return a single JSON object. Do NOT return an array or a breakdown of multiple sentiments.
    
    Expected JSON Format:
    {{
      "sentiment": "label"
    }}

    Context:
    {context}

    Text:
    {text}
    """

    raw_result = generate_completion(prompt, json_mode=True)
    result = json.loads(raw_result)
    
    # 2. Store in cache
    CacheService.set_cached_result(cache_key, result)
    return result


def classify_text(text: str):
    # 1. Check cache
    cache_key = CacheService.generate_key("classify", text)
    cached_result = CacheService.get_cached_result(cache_key)
    if cached_result:
        return cached_result

    context = build_context(text)

    prompt = f"""
    Identify the most relevant category (e.g., finance, sports, politics, tech) for the text below.
    Return ONLY a single valid JSON object with a lowercase label.
    
    Expected JSON Format:
    {{
      "label": "category"
    }}

    Context:
    {context}

    Text:
    {text}
    """

    raw_result = generate_completion(prompt, json_mode=True)
    result = json.loads(raw_result)
    
    # 2. Store in cache
    CacheService.set_cached_result(cache_key, result)
    return result


def extract_entities(text: str):
    # 1. Check cache
    cache_key = CacheService.generate_key("entities", text)
    cached_result = CacheService.get_cached_result(cache_key)
    if cached_result:
        return cached_result

    context = build_context(text)

    prompt = f"""
    Extract named entities from the following text. Use the context to better identify specialized or industry-specific terms.
    Return ONLY valid JSON in this format:
    {{
      "entities": [
        {{"text": "entity name", "type": "PERSON/ORG/LOC/etc"}}
      ]
    }}

    Context:
    {context}

    Text:
    {text}
    """

    raw_result = generate_completion(prompt, json_mode=True)
    result = json.loads(raw_result)
    
    # 2. Store in cache
    CacheService.set_cached_result(cache_key, result)
    return result
