from app.core.models import ClaimState, AGENT_DOC_TYPES
from app.utils.pdf_utils import filter_pages_by_types
from app.utils.llm_utils import vision_call

SYSTEM_PROMPT = """You are an identity and insurance data extractor for medical claims.
You will receive one or more pages from a claim bundle that contain identity or claim form information.
Extract all available identity and policy details.

Respond ONLY with valid JSON in this exact format:
{
  "patient_name": "full name or null",
  "date_of_birth": "date string or null",
  "id_numbers": ["list", "of", "any", "ID", "numbers", "found"],
  "policy_number": "policy number or null",
  "patient_id": "patient ID or null",
  "contact": "phone number or null",
  "address": "full address or null",
  "insurance_provider": "insurer name or null",
  "group_number": "group number or null"
}
If a field is not found, use null. Never guess — only extract what is clearly visible.
"""

USER_PROMPT = "Extract all identity and insurance policy information from these pages. Return JSON only."


def id_agent(state: ClaimState) -> ClaimState:
    """
    LangGraph node: ID Agent

    Receives ONLY pages classified as identity_document or claim_forms.
    Extracts: patient name, DOB, ID numbers, policy details.
    """
    relevant_pages = filter_pages_by_types(
        state.page_classifications,
        AGENT_DOC_TYPES["id_agent"],
    )

    if not relevant_pages:
        print("[ID Agent] No identity/claim pages found.")
        state.id_data = {}
        return state

    print(f"[ID Agent] Processing {len(relevant_pages)} page(s): "
          f"{[p.page_number for p in relevant_pages]}")

    images = [p.base64_image for p in relevant_pages]

    try:
        result = vision_call(SYSTEM_PROMPT, USER_PROMPT, images)
        state.id_data = result
        print(f"[ID Agent] Extracted: patient='{result.get('patient_name')}', "
              f"policy='{result.get('policy_number')}'")
    except Exception as e:
        print(f"[ID Agent] Error: {e}")
        state.id_data = {"error": str(e)}

    return state
