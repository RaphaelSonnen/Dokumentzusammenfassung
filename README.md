"""
Local Document AI – Quickstart
==============================

1.  Clone / copy project files & create virtual env

    $ python -m venv .venv && source .venv/bin/activate
    $ pip install -r requirements.txt
    # spaCy model
    $ python -m spacy download en_core_web_sm

2.  Install and run Ollama, pull Gemma model

    $ curl -fsSL https://ollama.com/install.sh | sh   # or via pkg manager
    $ ollama pull gemma:27b

3.  Provide your Jina API key

    Add `JINA_API_KEY=<your key>` to `.env` or export it in your shell

4.  Ingest & analyse your project folder

    $ python -m local_doc_ai.cli ingest /path/to/project
    $ python -m local_doc_ai.cli analyse

5.  Build vector index

    $ python -m local_doc_ai.cli build-index

6.  Chat with your docs

    $ python -m local_doc_ai.cli chat

   ┌─────────────────────────────────────────┐
   │ > Which tasks is Alice responsible for?│
   │ Answer: Alice Smith must deliver the…  │
   │ Sources: project_plan.docx …           │
   └─────────────────────────────────────────┘

Advanced
--------
* Adjust `.env` to tweak chunk size, models, k‑values.
* Swap Chroma with Qdrant by editing `index_builder.py` & `chat_backend.py`.
* Add a Streamlit UI by calling the same backend functions.
* Extend `analysis.py` with extra LLM prompts to extract KPIs.
"""

.venv\Scripts\Activate.ps1  
python -m local_doc_ai.cli convert-to-pdf
python -m local_doc_ai.cli ingest docs
python -m local_doc_ai.cli analyse
python -m local_doc_ai.cli build-index
python -m local_doc_ai.cli extract-facts 
python -m local_doc_ai.cli chat
