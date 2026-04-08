import traceback
from app.core.models import ClaimState, AGENT_DOC_TYPES, BillData
from app.utils.pdf_utils import filter_pages_by_types
from app.utils.llm_utils import vision_call

SYSTEM_PROMPT = """You are a medical billing data extractor for insurance claims.
You will receive one or more pages containing itemized bills, hospital bills, pharmacy bills, or cash receipts.
Extract every line item and all totals.

- Extract EVERY line item — do not skip any.
- Use null/placeholder for numeric fields only if genuinely not present (not 0).
- If multiple bills are present, combine all items into one list and sum the totals.
"""

USER_PROMPT = "Extract all itemized charges and totals from these billing pages."


async def bill_agent(state: ClaimState) -> ClaimState:
    """
    LangGraph node: Itemized Bill Agent

    Receives ONLY pages classified as itemized_bill or cash_receipt.
    Extracts every line item, subtotals, tax, insurance payments, and patient responsibility.
    """
    relevant_pages = filter_pages_by_types(
        state.page_classifications,
        AGENT_DOC_TYPES["bill_agent"],
    )

    if not relevant_pages:
        print("[Bill Agent] No billing pages found.")
        state.bill_data = {}
        return state

    print(f"[Bill Agent] Processing {len(relevant_pages)} page(s): "
          f"{[p.page_number for p in relevant_pages]}")

    images = [p.base64_image for p in relevant_pages]

    try:
        result = await vision_call(SYSTEM_PROMPT, USER_PROMPT, images, response_model=BillData)
        state.bill_data = result.model_dump()

        item_count = len(result.items)
        total = result.total_amount
        print(f"[Bill Agent] Extracted {item_count} items. Total: ${total}")
    except Exception as e:
        print(f"[Bill Agent] ERROR: {e}")
        traceback.print_exc()
        state.bill_data = {"error": str(e)}

    return state
