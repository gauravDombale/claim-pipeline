"""
Quick smoke test — run this directly to test the pipeline without starting FastAPI.

Usage:
    python tests/test_pipeline.py

Requires:
    - OPENAI_API_KEY in .env
    - The sample PDF at the path below
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import json
from app.core.models import ClaimState
from app.core.pipeline import pipeline


import asyncio

async def test_pipeline(pdf_path: str, claim_id: str = "TEST-001"):
    print(f"\nLoading PDF: {pdf_path}")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    print(f"PDF size: {len(pdf_bytes)} bytes")

    state = ClaimState(claim_id=claim_id, pdf_bytes=pdf_bytes)
    final_state = await pipeline.ainvoke(state)

    result = final_state.get("result") if isinstance(final_state, dict) else final_state.result
    print("\n" + "="*60)
    print("FINAL RESULT:")
    print("="*60)
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "final_image_protected.pdf"
    asyncio.run(test_pipeline(pdf_path))
