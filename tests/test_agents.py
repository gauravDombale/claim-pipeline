import pytest
from unittest.mock import AsyncMock, patch
from app.core.models import ClaimState, IDData, PageClassification
from app.agents.id_agent import id_agent


@pytest.mark.asyncio
async def test_id_agent_processes_correctly():
    """
    Test that the ID Agent correctly isolates identity pages
    and maps the structured output into state dict without actually calling OpenAI.
    """
    # Setup initial state with fake data (a mix of ID pages and unrelated pages)
    initial_state = ClaimState(
        claim_id="TEST-ID-001",
        pdf_bytes=b"fake_pdf_bytes",
        page_classifications=[
            PageClassification(page_number=1, doc_type="claim_forms", base64_image="b64_1"),
            PageClassification(page_number=2, doc_type="itemized_bill", base64_image="b64_2"),
        ]
    )

    # Fake expected response from structured output
    fake_response_obj = IDData(
        patient_name="John Doe",
        policy_number="POL-12345"
    )

    # Patch the vision_call helper
    with patch("app.agents.id_agent.vision_call", new_callable=AsyncMock) as mock_vision:
        mock_vision.return_value = fake_response_obj
        
        # Run agent
        new_state = await id_agent(initial_state)

        # Assertions
        assert mock_vision.call_count == 1
        
        # Check that it only evaluated the "claim_forms" page (page 1)
        passed_images = mock_vision.call_args[0][2]
        assert len(passed_images) == 1
        assert passed_images[0] == "b64_1"
        
        # Check the state modification
        assert new_state.id_data is not None
        assert new_state.id_data["patient_name"] == "John Doe"
        assert new_state.id_data["policy_number"] == "POL-12345"
