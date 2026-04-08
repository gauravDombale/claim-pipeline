import traceback
from app.core.models import ClaimState, AGENT_DOC_TYPES
from app.utils.pdf_utils import filter_pages_by_types
from app.utils.llm_utils import vision_call

SYSTEM_PROMPT = """You are a clinical data extractor specializing in hospital discharge summaries.
You will receive one or more pages that are discharge summaries from a medical claim.
Extract all clinical and hospitalization details.

Respond ONLY with valid JSON in this exact format:
{
  "hospital": "hospital name or null",
  "admission_date": "date string or null",
  "discharge_date": "date string or null",
  "length_of_stay": "e.g. '5 days' or null",
  "diagnosis": "primary diagnosis or null",
  "admission_diagnosis": "diagnosis at admission or null",
  "attending_physician": "doctor name and credentials or null",
  "condition_at_discharge": "e.g. 'Stable, improved' or null",
  "discharge_medications": ["list of medications with dosage"],
  "follow_up": "follow-up instructions or null",
  "hospital_course": "brief summary of treatment or null"
}
If a field is not found, use null. Never guess.
"""

USER_PROMPT = "Extract all discharge and clinical information from these pages. Return JSON only."


def discharge_agent(state: ClaimState) -> ClaimState:
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
        result = vision_call(SYSTEM_PROMPT, USER_PROMPT, images)
        state.discharge_data = result
        print(f"[Discharge Agent] Extracted: diagnosis='{result.get('diagnosis')}', "
              f"admit='{result.get('admission_date')}', discharge='{result.get('discharge_date')}'")
    except Exception as e:
        print(f"[Discharge Agent] ERROR: {e}")
        traceback.print_exc()
        state.discharge_data = {"error": str(e)}

    return state
