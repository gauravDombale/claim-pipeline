# Video Explanation Script: AI-Powered Claim Processing Pipeline

**Goal of this video:** To clearly explain your architectural choices, the LangGraph workflow, how your Segregator Agent works, and demonstrate the complete process flow as requested in the assignment.

---

## 🎬 Section 1: Introduction (0:00 - 0:45)
**Visual:** Have the project `README.md` or a high-level architecture diagram visible on the screen. 
**Script:**
> "Hi everyone, thank you for taking the time to review my assignment. Today I'm going to walk you through my AI-Powered Insurance Claim Processing Pipeline. For this project, I built a fast and reliable FastAPI backend orchestrated by a multi-agent LangGraph workflow. The primary goal was to take complex, unstructured medical claim PDFs, accurately segregate the pages by document type, and extract structured JSON data using specialized AI agents."

## 🎬 Section 2: Overcoming the Image-Protected PDF Challenge (0:45 - 1:15)
**Visual:** Show the `final_image_protected.pdf` file open, demonstrating that the text cannot be highlighted. Then, show a quick glimpse of `app/utils/pdf_utils.py`.
**Script:**
> "Before diving into the LangGraph flow, I want to highlight a crucial design decision. The provided sample PDF is 'image-protected'—meaning standard text-extraction tools like `pdfplumber` or `pypdf` simply return empty strings. To solve this in a robust way that works for *any* scanned document, my pipeline uses `PyMuPDF` to render each page as a pixel image. I then pass these images directly to GPT-4o Vision for all classification and data extraction tasks."

## 🎬 Section 3: The LangGraph Workflow (1:15 - 2:00)
**Visual:** Open `app/core/pipeline.py` and highlight the `build_pipeline()` function where the nodes and edges are added.
**Script:**
> "Let’s look at the LangGraph architecture. The workflow begins at the `START` node which passes the raw PDF bytes into our **Segregator Agent**. From the Segregator, the graph fans out to three specialized extraction agents running in parallel: the **ID Agent**, the **Discharge Summary Agent**, and the **Itemized Bill Agent**. Because LangGraph natively supports parallel execution for independent nodes sharing an output edge, this severely cuts down processing time. Finally, all three feed into the **Aggregator** node which terminates the graph."

## 🎬 Section 4: The Segregator Agent (2:00 - 2:45)
**Visual:** Show `app/agents/segregator.py`. Highlight the `SYSTEM_PROMPT` containing the 9 document types.
**Script:**
> "The heart of the routing logic is the **Segregator Agent**. This node takes the converted PDF page images and queries the LLM to classify each individual page into one of nine distinct categories—such as `claim_forms`, `discharge_summary`, or `itemized_bill`. It then populates the application state with a list of classified pages. The key rule of the assignment was that extraction agents should only process relevant pages, so this step ensures we don't spam our subsequent agents with unnecessary context window bloat."

## 🎬 Section 5: The Extraction Agents (2:45 - 3:30)
**Visual:** Open `app/agents/id_agent.py` or `bill_agent.py`. Highlight the `filter_pages_by_types` method at the top of the function.
**Script:**
> "Next, we have our three extraction nodes. Let's look at the ID Agent as an example. Instead of receiving the whole PDF, the very first thing it does is call a helper function `filter_pages_by_types`. This queries the LangGraph state so that the ID Agent *only* receives images classified as `identity_document` or `claim_forms`. Once isolated, the agent extracts targeted points like patient name, dates of birth, and policy numbers into a strict JSON schema. The Discharge Agent and Bill Agent follow the exact same pattern for their respective clinical and financial domains."

## 🎬 Section 6: Enterprise-Grade Architecture (3:30 - 4:15)
**Visual:** Show `app/utils/llm_utils.py` highlighting `AsyncOpenAI` and `.parse()`, or run `pytest` in your terminal.
**Script:**
> "I also want to quickly highlight how this setup is built for production. First, the entire pipeline is completely asynchronous. This means these heavy LLM vision tasks won't block the core FastAPI event loop under load. Second, I didn't rely on 'prompt hacking' to convince the model to output JSON. Instead, I securely map my extractions to `Pydantic` models using OpenAI's native Structured Outputs. This guarantees 100% type reliability. Finally, the project includes lightweight mocked unit tests using `pytest` to validate the LangGraph routing logic instantly without racking up API charges."

## 🎬 Section 7: The Aggregator (4:15 - 4:30)
**Visual:** Open `app/agents/aggregator.py`.
**Script:**
> "Once the parallel extraction finishes, the state merges at the **Aggregator node**. This node simply takes the structured Pydantic models produced by the agents, maps out the page classification history for transparency, and bundles everything into the exact JSON payload demanded by the requirements."

## 🎬 Section 8: Live Demonstration (4:30 - End)
**Visual:** Open `http://localhost:8000/docs` (Swagger UI). Execute the `POST /api/process` endpoint using the sample PDF.
**Script:**
> "Finally, let's see it in action. I'm using FastAPI’s auto-generated Swagger UI. I'll pass in a standard claim ID and upload the `final_image_protected.pdf`. 
> *(Click Execute and let the screen record the terminal running in the background if possible, showing the agent logs).*
> As you can see, the API successfully processes the document and returns a highly structured, perfectly validated JSON response. It gives us a map of exactly how each page was classified, alongside the neatly extracted Identity, Discharge, and Billing details. 
> 
> That concludes my walkthrough. The full code is available in my GitHub repository. Thank you for your time!"

---
### 💡 Quick Tips for Recording:
- Use **Loom** or **OBS** to record. Loom makes it very easy to just generate a link.
- Have all your files (`pipeline.py`, `segregator.py`, `bill_agent.py`, Swagger UI) open in tabs before you start recording so you can click between them quickly without pausing.
- Do a practice "dry run" clicking all the buttons first.
