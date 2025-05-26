from pathlib import Path
import spacy
import ollama
import json
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import Document as LlamaDoc
from .database import Document, Entity, get_session, Fact
from .config import CHUNK_SIZE, CHUNK_OVERLAP, LLM_MODEL

nlp = spacy.load("en_core_web_sm")
node_parser = SimpleNodeParser.from_defaults(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)

SUMMARY_PROMPT = (
    "Du bist ein Assistent, der interne Projekt­unterlagen "
    "für ein Ingenieur­büro zusammenfasst.\n"
    "Gib maximal acht Stichpunkte (je ≤ 20 Wörter) auf Deutsch zurück:"
)

KPI_PROMPT = (
    "Extrahiere ein JSON-Objekt namens \"kpis\" mit deutschen Schlüsseln "
    "für wichtige Kennzahlen (z. B. Budget, Kosten, Termine, "
    "Materialmengen, Projekt­nummer, Planstand) aus dem folgenden Text. "
    "Gib ausschließlich das JSON zurück.\n\n"
)


def extract_kpis(text: str) -> dict[str, str]:
    resp = ollama.generate(
        model=LLM_MODEL,
        prompt=f"{KPI_PROMPT}{text[:4000]}\n### KPIs:"
    )
    try:
        return json.loads(resp["response"])["kpis"]
    except Exception:
        return {}


def summarize(text: str) -> str:
    resp = ollama.generate(model=LLM_MODEL, prompt=f"{SUMMARY_PROMPT}\n\n{text}\n\n### Summary:")
    return resp["response"].strip()


def analyse_and_store(doc: Document, session):
    # summarization
    if not doc.summary and doc.content:
        doc.summary = summarize(doc.content[:4000])  # limit to first ~4k chars
    # NER
    if doc.content:
        for ent in nlp(doc.content).ents:
            entity = Entity(
                document=doc,
                label=ent.label_,
                text=ent.text,
                start_char=ent.start_char,
                end_char=ent.end_char,
            )
            session.add(entity)
        kpis = extract_kpis(doc.content or "")


    try:
        kpis = extract_kpis(doc.content or "")
    except Exception as e:
        print(f"[KPI] Extraction failed in doc {doc.id}: {e}")
        kpis = {}                 # garantiert definiert

    for k, v in kpis.items():
        session.add(
            Fact(
                doc_id=doc.id,
                category="KENNZAHL",   # deutsch
                key=k,
                value=str(v)
            )
        )


def analyse_all():
    with get_session() as session:
        docs = session.query(Document).all()
        for d in docs:
            analyse_and_store(d, session)
        session.commit()
    print("[Analysis] Completed summarization + NER.")