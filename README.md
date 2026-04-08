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
  "claim_id": "CLM-12345",
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
    "page_10": "itemized_bill",
    "page_11": "investigation_report",
    "page_12": "investigation_report",
    "page_13": "claim_forms",
    "page_14": "other",
    "page_15": "claim_forms",
    "page_16": "other",
    "page_17": "other",
    "page_18": "other"
  },
  "identity_and_policy": {
    "patient_name": "John Michael Smith",
    "date_of_birth": "March 15, 1985",
    "id_numbers": [
      "ID-987-654-321",
      "PAT-789456"
    ],
    "policy_number": "POL-987654321",
    "patient_id": "PAT-789456",
    "contact": "+1-555-0123",
    "address": "456 Oak Street, Apt 12B, Springfield, IL 62701",
    "insurance_provider": "HealthCare Insurance Company",
    "group_number": "GRP-12345"
  },
  "discharge_summary": {
    "admission_date": "January 20, 2025",
    "discharge_date": "January 25, 2025",
    "length_of_stay": "5 days",
    "diagnosis": "Community Acquired Pneumonia (CAP)",
    "attending_physician": "Dr. Sarah Johnson, MD",
    "hospital": "City Medical Center",
    "condition_at_discharge": "Stable, improved",
    "discharge_medications": [
      "Amoxicillin 500mg TID x 7 days",
      "Acetaminophen 500mg PRN for pain"
    ],
    "follow_up": "Outpatient clinic in 1 week"
  },
  "billing": {
    "items": [
      {
        "description": "Consultation Fee - Dr. Sarah Johnson",
        "quantity": null,
        "rate": null,
        "amount": 150
      },
      {
        "description": "Laboratory Tests (CBC, Blood Sugar)",
        "quantity": null,
        "rate": null,
        "amount": 80
      },
      {
        "description": "Medications (Prescription)",
        "quantity": null,
        "rate": null,
        "amount": 45
      },
      {
        "description": "Service Charges",
        "quantity": null,
        "rate": null,
        "amount": 10
      },
      {
        "description": "Room Charges - Semi-Private (5 days)",
        "quantity": 5,
        "rate": 200,
        "amount": 1000
      },
      {
        "description": "Admission Fee",
        "quantity": 1,
        "rate": 150,
        "amount": 150
      },
      {
        "description": "Emergency Room Services",
        "quantity": 1,
        "rate": 500,
        "amount": 500
      },
      {
        "description": "Physician Consultation - Dr. Sarah Johnson",
        "quantity": 5,
        "rate": 150,
        "amount": 750
      },
      {
        "description": "Chest X-Ray",
        "quantity": 2,
        "rate": 120,
        "amount": 240
      },
      {
        "description": "CT Scan - Chest",
        "quantity": 1,
        "rate": 800,
        "amount": 800
      },
      {
        "description": "Complete Blood Count (CBC)",
        "quantity": 3,
        "rate": 45,
        "amount": 135
      },
      {
        "description": "Blood Culture Test",
        "quantity": 2,
        "rate": 80,
        "amount": 160
      },
      {
        "description": "Arterial Blood Gas Analysis",
        "quantity": 1,
        "rate": 95,
        "amount": 95
      },
      {
        "description": "IV Fluids - Normal Saline",
        "quantity": 10,
        "rate": 25,
        "amount": 250
      },
      {
        "description": "Injection - Ceftriaxone 1g",
        "quantity": 5,
        "rate": 30,
        "amount": 150
      },
      {
        "description": "Injection - Paracetamol",
        "quantity": 6,
        "rate": 8,
        "amount": 48
      },
      {
        "description": "Nebulization Treatment",
        "quantity": 4,
        "rate": 35,
        "amount": 140
      },
      {
        "description": "Oxygen Therapy (per hour)",
        "quantity": 48,
        "rate": 5,
        "amount": 240
      },
      {
        "description": "Nursing Care (per day)",
        "quantity": 5,
        "rate": 100,
        "amount": 500
      },
      {
        "description": "ICU Monitoring Equipment",
        "quantity": 2,
        "rate": 200,
        "amount": 400
      },
      {
        "description": "Physiotherapy Session",
        "quantity": 3,
        "rate": 60,
        "amount": 180
      },
      {
        "description": "Medical Supplies & Consumables",
        "quantity": 1,
        "rate": 250,
        "amount": 250
      },
      {
        "description": "Laboratory Processing Fee",
        "quantity": 1,
        "rate": 75,
        "amount": 75
      },
      {
        "description": "Pharmacy Dispensing Fee",
        "quantity": 1,
        "rate": 50,
        "amount": 50
      },
      {
        "description": "Amoxicillin 500mg Capsules",
        "quantity": 21,
        "rate": 1.5,
        "amount": 31.5
      },
      {
        "description": "Acetaminophen 500mg Tablets",
        "quantity": 20,
        "rate": 0.8,
        "amount": 16
      },
      {
        "description": "Cetirizine 10mg Tablets",
        "quantity": 10,
        "rate": 0.9,
        "amount": 9
      },
      {
        "description": "Omeprazole 20mg Capsules",
        "quantity": 14,
        "rate": 1.2,
        "amount": 16.8
      },
      {
        "description": "Albuterol Inhaler",
        "quantity": 1,
        "rate": 35,
        "amount": 35
      },
      {
        "description": "Vitamin D3 1000 IU",
        "quantity": 30,
        "rate": 0.4,
        "amount": 12
      },
      {
        "description": "Probiotic Capsules",
        "quantity": 30,
        "rate": 0.85,
        "amount": 25.5
      },
      {
        "description": "Saline Nasal Spray",
        "quantity": 1,
        "rate": 8.5,
        "amount": 8.5
      },
      {
        "description": "Antiseptic Mouthwash 250ml",
        "quantity": 1,
        "rate": 12,
        "amount": 12
      },
      {
        "description": "Digital Thermometer",
        "quantity": 1,
        "rate": 15,
        "amount": 15
      },
      {
        "description": "Medication Counseling",
        "quantity": 1,
        "rate": 25,
        "amount": 25
      },
      {
        "description": "Home Delivery Service",
        "quantity": 1,
        "rate": 10,
        "amount": 10
      }
    ],
    "subtotal": null,
    "tax": 317.33,
    "total_amount": 909.35,
    "insurance_payment": 5134.92,
    "patient_responsibility": 1283.73,
    "bill_numbers": [
      "RCP-2025-456789",
      "BILL-2025-789456",
      "INV-2025-123789"
    ]
  }
}
```

## Testing Without API

```bash
python tests/test_pipeline.py final_image_protected.pdf
```

## Enterprise-Grade Features 🚀

To ensure this pipeline functions like a true production system, it features:
- **Full Asynchronous Architecture:** Uses `AsyncOpenAI` within LangGraph to ensure the heavy GPT-4o Vision calls never block the FastAPI event loop, enabling extreme concurrency.
- **Native Structured Outputs:** Instead of fragile text prompts asking for JSON, the LLM is tightly bound to `Pydantic` models via OpenAI's `.parse()` method. This guarantees the extracted keys and data types evaluate perfectly every time.
- **Mocked Unit Testing:** A local `pytest` suite uses `unittest.mock.AsyncMock` to independently verify agent logic and routing behavior instantly, without consuming API credits.

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
