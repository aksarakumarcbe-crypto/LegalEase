from fastapi import APIRouter, HTTPException
from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.config import get_settings
from backend.models import DocumentRequest, DocumentResponse, HealthResponse

router = APIRouter()
generator = GeminiDocumentGenerator()

@router.get("/health", response_model=HealthResponse)
def health():
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        ai_configured=bool(settings.gemini_api_key),
        model=settings.gemini_model,
    )

@router.post("/generate", response_model=DocumentResponse)
def generate_document(request: DocumentRequest):
    if not request.document_type.strip():
        raise HTTPException(status_code=422, detail="Document type is required.")

    result = generator.generate_document(
        document_type=request.document_type,
        parties=request.parties,
        terms=request.terms,
        dates=request.dates,
        governing_law=request.governing_law,
        company_name=request.company_name,
        additional_instructions=request.additional_instructions,
    )

    return DocumentResponse(
        success=True,
        document=result.text,
        model=result.model,
        demo_mode=result.demo_mode,
        message=result.message,
    )
