# LegalEase — AI-Powered Legal Document Generator

Complete local project based on the supplied LegalEase documentation.

## Features
- Streamlit frontend
- FastAPI backend
- Google Gemini integration
- Editable generated document
- TXT, DOCX and PDF export
- CORS and health check
- Local demo mode when no Gemini API key is configured
- Automated API tests

## Architecture
Streamlit -> FastAPI -> Gemini AI
                    -> local DOCX/PDF/TXT exporters

## Important
LegalEase creates AI-assisted drafts, not legal advice. Review important documents with a qualified legal professional before signing or relying on them.

## Current Gemini SDK
The supplied documentation names the older `google-generativeai` package and Gemini 1.5 Pro. The current Google Python SDK uses `google-genai` and `from google import genai`. This project uses the current SDK and makes the model configurable through `GEMINI_MODEL`.

## Folder structure
```text
LegalEase/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── run_backend.bat
├── run_frontend.bat
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── models.py
│   ├── ai_core/
│   │   ├── __init__.py
│   │   └── gemini_generator.py
│   └── utils/
│       ├── __init__.py
│       ├── document_export.py
│       └── text_utils.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── assets/
│   └── logo.svg
└── tests/
    ├── __init__.py
    └── test_api.py
```

## VS Code setup — Windows
```powershell
python -m venv .venv
.venv\Scriptsctivate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set:
```env
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Run backend:
```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Run frontend in a second terminal:
```powershell
streamlit run frontend/app.py
```

Open:
- Frontend: `http://localhost:8501`
- Backend: `http://127.0.0.1:8000`
- Swagger API docs: `http://127.0.0.1:8000/docs`

## Test
```powershell
pytest -q
```

The tests do not require a Gemini key.

## Using the application
1. Choose a document type.
2. Enter parties and roles.
3. Enter terms separated by semicolons.
4. Enter the effective date.
5. Optionally enter governing law, company name and instructions.
6. Click Generate Document.
7. Edit the generated text.
8. Preview it.
9. Download TXT, DOCX or PDF.

## API example
POST `/generate`:
```json
{
  "document_type": "Employment Contract",
  "parties": "ABC Pvt Ltd (Employer), Jane Doe (Employee)",
  "terms": "Salary is paid monthly; Working hours are 9 AM to 6 PM; Confidentiality must be maintained",
  "dates": "October 1, 2026",
  "governing_law": "Tamil Nadu, India",
  "company_name": "ABC Pvt Ltd",
  "additional_instructions": "Use a professional formal style."
}
```

## Troubleshooting
If the frontend cannot connect, start FastAPI first.

If Gemini fails, verify the API key, model name, quota and internet connection. The app falls back to a clearly labelled local draft so the UI and export features can still be tested.

Never commit `.env`.
