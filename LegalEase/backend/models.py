from pydantic import BaseModel, Field, field_validator

class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=2, max_length=5000)
    terms: str = Field(..., min_length=2, max_length=12000)
    dates: str = Field(..., min_length=2, max_length=500)
    governing_law: str = Field(default="", max_length=500)
    company_name: str = Field(default="", max_length=300)
    additional_instructions: str = Field(default="", max_length=5000)

    @field_validator(
        "document_type","parties","terms","dates",
        "governing_law","company_name","additional_instructions"
    )
    @classmethod
    def clean_whitespace(cls, value: str) -> str:
        return " ".join(value.strip().split())

class DocumentResponse(BaseModel):
    success: bool
    document: str
    model: str
    demo_mode: bool = False
    message: str = ""

class HealthResponse(BaseModel):
    status: str
    app: str
    ai_configured: bool
    model: str
