Claim Processing Pipeline Assignment
Sample PDF to process : final_image_protected.pdf
Goal
Build a FastAPI service that processes PDF claims using LangGraph to orchestrate document segregation and multi-agent extraction.

Requirements
API Endpoint
POST /api/process
Input:
claim_id (string)
file (PDF)
Output: Any JSON with extracted data

LangGraph Workflow
Build this exact flow:
START → [Segregator Agent (AI)]   →     [ID Agent]         →              [Aggregator] → END
              ↓                                         → [Discharge Summary Agent] ↗
        (classifies pages                      →             [Itemized Bill Agent] ↗
         into 9 doc types,
         routes to agents)
Nodes:
Segregator Agent (AI-powered)
Takes PDF file
Uses LLM to analyze and classify pages into document types:
claim_forms
cheque_or_bank_details
identity_document
itemized_bill
discharge_summary
prescription
investigation_report
cash_receipt
other
Routes pages to appropriate extraction agents
Extraction Agent Nodes (3 required)
Route the necessary pages to separate agents without passing the whole pdf
ID Agent - Extracts identity information (patient name, DOB, ID numbers, policy details)
Discharge Summary Agent - Extracts diagnosis, admit/discharge dates, physician details
Itemized Bill Agent - Extracts all items with costs and calculates total amount
Each agent processes only the pages assigned to them by segregator
Aggregator Node
Combines all agent results
Returns final JSON with all extracted data
Key Rule: Segregator classifies pages into document types. Only 3 extraction agents process the relevant pages.

Submission
Provide:
Live API URL (Optional) - Deploy if you want (Render/Railway/Fly.io)
Video Explanation (Preffered) - Loom or any video platform explaining:
Your LangGraph workflow
How the segregator agent works
How extraction agents process their assigned pages
The complete process flow
GitHub Repo with README
Send it at advaid@superclaims.ai


Tech Stack
FastAPI
LangGraph


