from app.core.models import ClaimState


async def aggregator(state: ClaimState) -> ClaimState:
    """
    LangGraph node: Aggregator

    Final node in the pipeline. Combines outputs from all 3 extraction
    agents into a single clean JSON result attached to state.result.
    """
    print("[Aggregator] Combining all agent results...")

    # Build a page map for transparency (which pages were what)
    page_map = {}
    for p in state.page_classifications:
        page_map[f"page_{p.page_number}"] = p.doc_type

    state.result = {
        "claim_id": state.claim_id,
        "total_pages_processed": len(state.page_classifications),
        "page_classification": page_map,
        "identity_and_policy": state.id_data or {},
        "discharge_summary": state.discharge_data or {},
        "billing": state.bill_data or {},
    }

    print(f"[Aggregator] Done. Result assembled for claim '{state.claim_id}'.")
    return state
