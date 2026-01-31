"""
FastAPI application for dialog generation.

Provides REST API endpoints for generating dialogs,
comparing models, and managing the generation process.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings
from .models import (
    Subject, GenerateRequest, GeneratedDialog, SingleResponseRequest, DialogMessage,
    ModelInfo, CompareRequest, CompareResult
)
from .ollama_client import ollama
from .generator import DialogGenerator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    yield
    await ollama.close()


app = FastAPI(
    title="Dialog Generator API",
    description="Generate natural Telegram-style dialogs with brand mentions using local LLMs",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint.

    Returns:
        Status dict indicating service health.
    """
    return {"status": "ok"}


@app.get("/models", response_model=list[ModelInfo])
async def list_models():
    """List available Ollama models.

    Returns:
        List of installed models with metadata.

    Raises:
        HTTPException: If Ollama server is unavailable.
    """
    try:
        return await ollama.list_models()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama not available: {e}")


@app.post("/generate", response_model=GeneratedDialog)
async def generate_dialog(request: GenerateRequest):
    """Generate a complete dialog.

    Creates a multi-turn conversation that naturally incorporates
    the specified brand mention.

    Args:
        request: Generation parameters including brand info and settings.

    Returns:
        Generated dialog with messages and metadata.

    Raises:
        HTTPException: If model not found or generation fails.
    """
    generator = DialogGenerator(model=request.model)

    if request.model and not await ollama.model_exists(request.model):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model}' not found. Use GET /models to list available."
        )

    try:
        return await generator.generate_dialog(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/respond", response_model=DialogMessage)
async def generate_response(request: SingleResponseRequest):
    """Generate a single response in conversation context.

    Continues an existing conversation with a contextually
    appropriate response.

    Args:
        request: Context and settings for response generation.

    Returns:
        Single response message.

    Raises:
        HTTPException: If model not found or generation fails.
    """
    generator = DialogGenerator(model=request.model)

    if request.model and not await ollama.model_exists(request.model):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model}' not found."
        )

    try:
        return await generator.generate_single_response(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare", response_model=list[CompareResult])
async def compare_models(request: CompareRequest):
    """Compare dialog generation across multiple models.

    Runs the same generation task across different models
    and returns comparative results.

    Args:
        request: Brand info and list of models to compare.

    Returns:
        List of results, one per model.
    """
    results = []

    for model_name in request.models:
        if not await ollama.model_exists(model_name):
            results.append(CompareResult(
                model=model_name,
                dialog=GeneratedDialog(
                    messages=[],
                    model_used=model_name,
                    generation_params={"error": "Model not found"}
                ),
                generation_time_ms=0
            ))
            continue

        generator = DialogGenerator(model=model_name)
        gen_request = GenerateRequest(
            subject=request.subject,
            context=request.context,
            num_turns=request.num_turns,
            model=model_name,
            language=request.language
        )

        start_time = time.time()
        try:
            dialog = await generator.generate_dialog(gen_request)
            gen_time = int((time.time() - start_time) * 1000)

            results.append(CompareResult(
                model=model_name,
                dialog=dialog,
                generation_time_ms=gen_time
            ))
        except Exception as e:
            results.append(CompareResult(
                model=model_name,
                dialog=GeneratedDialog(
                    messages=[],
                    model_used=model_name,
                    generation_params={"error": str(e)}
                ),
                generation_time_ms=0
            ))

    return results


def run():
    """Run the API server with settings from config."""
    import uvicorn
    uvicorn.run(
        "dialog_gen.api:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=True
    )
