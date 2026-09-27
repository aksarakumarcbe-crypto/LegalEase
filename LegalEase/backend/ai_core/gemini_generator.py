from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from backend.config import get_settings

@dataclass
class GenerationResult:
    text: str
    model: str
    demo_mode: bool
    message: str = ""

class GeminiDocumentGenerator:
    SYSTEM_INSTRUCTION = """
You are LegalEase, an AI assistant for drafting legal-document templates.

Your job is to produce a clear, professional FIRST DRAFT based only on the
information supplied by the user.

Rules:
1. Never invent names, dates, addresses, amounts, obligations, laws, citations,
   registration numbers, or facts that the user did not provide.
2. If a value is missing, use a neutral placeholder such as [NOT PROVIDED].
3. Do not claim that a draft is legally valid, enforceable, attorney-reviewed,
   or legal advice.
4. Use professional legal drafting language while keeping the structure readable.
5. Include a title, parties, effective date, useful definitions/recitals,
   numbered sections, signature blocks, and a final review note when appropriate.
6. Reflect the user's supplied terms faithfully.
7. Do not add jurisdiction-specific statutory claims unless the user supplies
   the jurisdiction and explicitly asks for them.
8. Return plain text only. Do not use Markdown fences.
"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self._client = None

    def _get_client(self):
        if not self.api_key:
            return None
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    @staticmethod
    def _demo_document(document_type, parties, terms, dates, governing_law,
                       company_name, additional_instructions):
        import re
        items = [x.strip() for x in re.split(r";|\n", terms or "") if x.strip()]
        if not items:
            items = ["[NOT PROVIDED]"]
        terms_block = "\n".join(
            f"{i}. {item}" for i, item in enumerate(items, 1)
        )
        return f"""{document_type.upper()}

DRAFT LEGAL DOCUMENT

1. PARTIES

The parties to this {document_type} are:

{parties}

2. EFFECTIVE DATE

This document is intended to take effect on {dates}.

3. PURPOSE AND SCOPE

The parties intend to establish the rights, responsibilities, and obligations
described in this document. The final wording should be reviewed before execution.

4. TERMS AND CONDITIONS

{terms_block}

5. GOVERNING LAW

Governing law / jurisdiction: {governing_law or "[NOT PROVIDED]"}

6. GENERAL PROVISIONS

6.1 Entire Agreement
This document is intended to represent the agreement between the parties
concerning its stated subject matter, subject to final amendments or schedules.

6.2 Amendments
Any amendment should be recorded in writing and approved by the parties.

6.3 Severability
If a provision is found to be unenforceable, the remaining provisions should
continue to the extent permitted by applicable law.

7. PARTY / BRAND INFORMATION

Company or organization: {company_name or "[NOT PROVIDED]"}

8. ADDITIONAL INSTRUCTIONS

{additional_instructions or "[NONE]"}

9. SIGNATURES

For Party 1:

Name: ______________________________
Signature: _________________________
Date: ______________________________


For Party 2:

Name: ______________________________
Signature: _________________________
Date: ______________________________


REVIEW NOTICE

This is an AI-generated draft prepared from the information supplied to
LegalEase. It is not legal advice and should be reviewed by a qualified legal
professional before signing, filing, or relying on it.
"""

    def generate_document(self, document_type, parties, terms, dates,
                          governing_law="", company_name="",
                          additional_instructions=""):
        client = self._get_client()

        if client is None:
            return GenerationResult(
                text=self._demo_document(
                    document_type, parties, terms, dates,
                    governing_law, company_name, additional_instructions
                ),
                model="local-demo",
                demo_mode=True,
                message="Gemini API key not configured. Showing local demo output."
            )

        prompt = f"""
Create a complete first-draft legal document.

Document type:
{document_type}

Parties:
{parties}

Effective date / dates:
{dates}

Terms and conditions supplied by the user:
{terms}

Governing law / jurisdiction, if supplied:
{governing_law or "[NOT PROVIDED]"}

Company / brand name, if supplied:
{company_name or "[NOT PROVIDED]"}

Additional instructions:
{additional_instructions or "[NONE]"}

Use only supplied facts. Do not invent missing information.
"""

        try:
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "system_instruction": self.SYSTEM_INSTRUCTION,
                    "temperature": 0.25,
                    "max_output_tokens": 7000,
                },
            )
            text = (response.text or "").strip()
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            return GenerationResult(
                text=text,
                model=self.model,
                demo_mode=False,
                message="Generated with Gemini."
            )
        except Exception as exc:
            return GenerationResult(
                text=self._demo_document(
                    document_type, parties, terms, dates,
                    governing_law, company_name, additional_instructions
                ),
                model=self.model,
                demo_mode=True,
                message=(
                    "Gemini request failed, so LegalEase returned a local draft. "
                    f"API error: {type(exc).__name__}: {exc}"
                )
            )
