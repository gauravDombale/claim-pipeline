import traceback
from app.core.models import ClaimState, AGENT_DOC_TYPES, DischargeData
from app.utils.pdf_utils import filter_pages_by_types
from app.utils.llm_utils import vision_call

SYSTEM_PROMPT = """You are a clinical data extractor specializing in hospital discharge summaries.
You will receive one or more pages that are discharge summaries from a medical claim.
Extract all clinical and hospitalization details.
If a field is not found, use null or leave empty. Never guess.
"""

USER_PROMPT = "Extract all discharge and clinical information from these pages."


async def discharge_agent(state: ClaimState) -> ClaimState:
    """
    LangGraph node: Discharge Summary Agent

    Receives ONLY pages classified as discharge_summary.
    Extracts: diagnosis, admit/discharge dates, physician, medications.
    """
    relevant_pages = filter_pages_by_types(
        state.page_classifications,
        AGENT_DOC_TYPES["discharge_agent"],
    )

    if not relevant_pages:
        print("[Discharge Agent] No discharge summary pages found.")
        state.discharge_data = {}
        return state

    print(f"[Discharge Agent] Processing {len(relevant_pages)} page(s): "
          f"{[p.page_number for p in relevant_pages]}")

    images = [p.base64_image for p in relevant_pages]

    try:
        result = await vision_call(SYSTEM_PROMPT, USER_PROMPT, images, response_model=DischargeData)
        state.discharge_data = result.model_dump()
        print(f"[Discharge Agent] Extracted: diagnosis='{result.diagnosis}', "
              f"admit='{result.admission_date}', discharge='{result.discharge_date}'")
    except Exception as e:
        print(f"[Discharge Agent] ERROR: {e}")
        traceback.print_exc()
        state.discharge_data = {"error": str(e)}

    return state
