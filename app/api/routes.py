from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from app.core.models import ClaimState
from app.core.pipeline import pipeline

router = APIRouter()


@router.post("/process")
async def process_claim(
    claim_id: str = Form(...),
    file: UploadFile = File(...),
):
    """
    POST /api/process

    Accepts:
        - claim_id (string form field)
        - file     (PDF upload)

    Returns:
        JSON with all extracted claim data
    """
    # Validate file type
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    print(f"\n{'='*60}")
    print(f"New claim received: {claim_id} | File: {file.filename} | Size: {len(pdf_bytes)} bytes")
    print(f"{'='*60}")

    # Build initial state
    initial_state = ClaimState(
        claim_id=claim_id,
        pdf_bytes=pdf_bytes,
    )

    # Run the LangGraph pipeline
    try:
        final_state = pipeline.invoke(initial_state)
    except Exception as e:
        print(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    result = final_state.get("result") if isinstance(final_state, dict) else final_state.result

    if not result:
        raise HTTPException(status_code=500, detail="Pipeline returned no result.")

    return result
