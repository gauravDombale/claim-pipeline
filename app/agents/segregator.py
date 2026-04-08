import traceback
from pydantic import BaseModel
from app.core.models import ClaimState, PageClassification, DOC_TYPES
from app.utils.pdf_utils import pdf_to_page_images
from app.utils.llm_utils import vision_call_single

SYSTEM_PROMPT = """You are a medical document classifier for insurance claims.
You will be shown a single page from a PDF claim bundle.
Classify it into EXACTLY ONE of these document types:

- claim_forms          : Medical claim forms, patient registration, insurance verification, consent forms
- cheque_or_bank_details : Cheque images, bank account details, payment slips
- identity_document    : Government ID, passport, driver's licence, any photo ID
- itemized_bill        : Hospital bills, pharmacy bills, itemized charges with costs
- discharge_summary    : Hospital discharge summaries with admission/discharge dates
- prescription         : Doctor's prescription / Rx with medications
- investigation_report : Lab reports, blood tests, radiology reports, diagnostic results
- cash_receipt         : Cash payment receipts from hospital or clinic
- other                : Anything that doesn't fit the above (referral letters, appointment letters, questionnaires)
"""

USER_PROMPT = "Classify this document page."


class SegregatorResponse(BaseModel):
    doc_type: str
    confidence: str
    reason: str


async def segregator_agent(state: ClaimState) -> ClaimState:
    """
    LangGraph node: Segregator Agent

    - Converts every PDF page to an image (handles image-protected PDFs)
    - Sends each page to GPT-4o Vision for classification
    - Populates state.page_classifications
    """
    print(f"[Segregator] Processing PDF for claim: {state.claim_id}")

    # DPI=100 keeps each page ~300-500 KB (safe for OpenAI); 150 can exceed limits
    pages = pdf_to_page_images(state.pdf_bytes, dpi=100)
    classifications = []

    for page in pages:
        page_num = page["page_number"]
        b64 = page["base64_image"]

        print(f"[Segregator] Classifying page {page_num}/{len(pages)}...")

        try:
            result = await vision_call_single(
                SYSTEM_PROMPT, 
                USER_PROMPT, 
                b64, 
                response_model=SegregatorResponse
            )
            doc_type = result.doc_type

            # Validate — fallback to "other" if LLM returns something unexpected
            if doc_type not in DOC_TYPES:
                print(f"[Segregator] Unknown type '{doc_type}' on page {page_num}, defaulting to 'other'")
                doc_type = "other"

            print(f"[Segregator] Page {page_num} → {doc_type} ({result.confidence})")

        except Exception as e:
            print(f"[Segregator] ERROR on page {page_num}: {e}")
            traceback.print_exc()   # ← full stack trace in server logs
            doc_type = "other"

        classifications.append(PageClassification(
            page_number=page_num,
            doc_type=doc_type,
            base64_image=b64,
        ))

    state.page_classifications = classifications
    print(f"[Segregator] Done. Classified {len(classifications)} pages.")
    return state
