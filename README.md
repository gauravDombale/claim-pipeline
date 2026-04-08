# Claim Processing Pipeline

AI-powered FastAPI service that processes insurance claim PDFs using LangGraph multi-agent orchestration.

## Architecture

```
POST /api/process (PDF upload)
        ↓
┌─────────────────────┐
│   Segregator Agent  │  ← GPT-4o Vision classifies each page into 9 doc types
│   (AI-powered)      │
└──────┬──────┬───────┘
       │      │      │
       ↓      ↓      ↓       (parallel execution)
  ┌────┐  ┌──────┐  ┌──────┐
  │ ID │  │Disch.│  │ Bill │  ← Each agent gets ONLY its relevant pages
  │Agent│  │Agent │  │Agent │
  └────┘  └──────┘  └──────┘
       │      │      │
       └──────┴──────┘
              ↓
       ┌────────────┐
       │ Aggregator │  ← Merges all results into final JSON
       └────────────┘
              ↓
         JSON Response
```

## Document Types (9)

| Type | Description |
|------|-------------|
| `claim_forms` | Medical claim forms, patient registration, insurance verification |
| `cheque_or_bank_details` | Cheque images, bank account details |
| `identity_document` | Government ID, passport, driver's licence |
| `itemized_bill` | Hospital/pharmacy bills with line items |
| `discharge_summary` | Hospital discharge summaries |
| `prescription` | Doctor Rx with medications |
| `investigation_report` | Lab reports, blood tests, radiology |
| `cash_receipt` | Payment receipts from hospital/clinic |
| `other` | Referral letters, consent forms, questionnaires |

## Extraction Agents

| Agent | Processes Pages Of Type | Extracts |
|-------|------------------------|---------|
| ID Agent | `identity_document`, `claim_forms` | Name, DOB, ID numbers, policy details |
| Discharge Agent | `discharge_summary` | Diagnosis, admit/discharge dates, physician, medications |
| Bill Agent | `itemized_bill`, `cash_receipt` | All line items, subtotal, tax, total, insurance payment |

## Setup

### 1. Clone & install

```bash
git clone <repo-url>
cd claim-pipeline
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-...
```

### 3. Run the server

```bash
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

## API Usage

### POST /api/process

```bash
curl -X POST http://localhost:8000/api/process \
  -F "claim_id=CLM-2024-789456" \
  -F "file=@final_image_protected.pdf"
```

### Sample Response

```json
{
  "claim_id": "CLM-2024-789456",
  "total_pages_processed": 18,
  "page_classification": {
    "page_1": "claim_forms",
    "page_2": "cheque_or_bank_details",
    "page_3": "identity_document",
    "page_4": "discharge_summary",
    "page_5": "prescription",
    "page_6": "investigation_report",
    "page_7": "cash_receipt",
    "page_8": "claim_forms",
    "page_9": "itemized_bill",
    "page_10": "itemized_bill"
  },
  "identity_and_policy": {
    "patient_name": "John Michael Smith",
    "date_of_birth": "March 15, 1985",
    "policy_number": "POL-987654321",
    "patient_id": "PAT-789456",
    "insurance_provider": "HealthCare Insurance Company"
  },
  "discharge_summary": {
    "hospital": "City Medical Center",
    "admission_date": "January 20, 2025",
    "discharge_date": "January 25, 2025",
    "diagnosis": "Community Acquired Pneumonia (CAP)",
    "attending_physician": "Dr. Sarah Johnson, MD",
    "condition_at_discharge": "Stable, improved"
  },
  "billing": {
    "total_amount": 6418.65,
    "insurance_payment": 5134.92,
    "patient_responsibility": 1283.73,
    "items": [...]
  }
}
```

## Testing Without API

```bash
python tests/test_pipeline.py final_image_protected.pdf
```

## Tech Stack

- **FastAPI** — REST API layer
- **LangGraph** — Multi-agent workflow orchestration
- **GPT-4o Vision** — Page classification + data extraction
- **PyMuPDF (fitz)** — PDF → image rendering (handles image-protected PDFs)
- **Pydantic** — Data validation and state modeling

## Key Design Decision: Image-Protected PDFs

The sample PDF (`final_image_protected.pdf`) has no extractable text — it's rendered as images. Standard text extraction tools (`pdfplumber`, `pypdf`) return empty strings on such files.

**Solution:** PyMuPDF renders each page as a pixel image (PNG), which is then sent to GPT-4o Vision. This works on ALL PDFs regardless of protection or scan quality.

## Project Structure

```
claim-pipeline/
├── main.py                     # FastAPI app entry point
├── requirements.txt
├── .env.example
├── app/
│   ├── api/
│   │   └── routes.py           # POST /api/process endpoint
│   ├── core/
│   │   ├── models.py           # Pydantic state + data models
│   │   └── pipeline.py         # LangGraph graph definition
│   ├── agents/
│   │   ├── segregator.py       # Page classifier (AI-powered)
│   │   ├── id_agent.py         # Identity extractor
│   │   ├── discharge_agent.py  # Clinical data extractor
│   │   ├── bill_agent.py       # Billing extractor
│   │   └── aggregator.py       # Result merger
│   └── utils/
│       ├── pdf_utils.py        # PDF → image conversion
│       └── llm_utils.py        # GPT-4o Vision wrapper
└── tests/
    └── test_pipeline.py        # End-to-end smoke test
```
