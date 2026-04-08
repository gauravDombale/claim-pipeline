import traceback
from app.core.models import ClaimState, AGENT_DOC_TYPES, IDData
from app.utils.pdf_utils import filter_pages_by_types
from app.utils.llm_utils import vision_call

SYSTEM_PROMPT = """You are an identity and insurance data extractor for medical claims.
You will receive one or more pages from a claim bundle that contain identity or claim form information.
Extract all available identity and policy details.
If a field is not found, use null or leave empty. Never guess — only extract what is clearly visible.
"""

USER_PROMPT = "Extract all identity and insurance policy information from these pages."


async def id_agent(state: ClaimState) -> ClaimState:
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
        result = await vision_call(SYSTEM_PROMPT, USER_PROMPT, images, response_model=IDData)
        state.id_data = result.model_dump()
        print(f"[ID Agent] Extracted: patient='{result.patient_name}', "
              f"policy='{result.policy_number}'")
    except Exception as e:
        print(f"[ID Agent] Error: {e}")
        state.id_data = {"error": str(e)}

    return state
