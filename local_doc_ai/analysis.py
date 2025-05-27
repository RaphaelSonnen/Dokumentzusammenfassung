# local_doc_ai/analysis.py
from pathlib import Path
import spacy, ollama, json

from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import Document as LlamaDoc

from .database import Document, Entity, get_session, Fact
from .config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    LLM_MODEL,
    SYSTEM_PROMPT_DE,       # ← kommt aus config.py
)

# ---------------------------------------------------------------------
# spaCy-Modell (deutsch)
nlp = spacy.load("de_core_news_sm")

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

# ---------------------------------------------------------------------
# Hilfs-Wrapper: sorgt dafür, dass **immer** SYSTEM_PROMPT_DE gesetzt ist
def _chat_llm(messages: list[dict]) -> str:
    """
    Führt einen Ollama-Chat-Call mit deutschem System-Prompt aus
    und liefert den reinen Antwort-Text zurück.
    """
    resp = ollama.chat(model=LLM_MODEL, messages=messages, stream=False)
    return resp["message"]["content"]

# ---------------------------------------------------------------------
def extract_kpis(text: str) -> dict[str, str]:
    answer = _chat_llm([
        {"role": "system", "content": SYSTEM_PROMPT_DE},
        {"role": "user",
         "content": f"{KPI_PROMPT}{text[:4000]}\n### KPIs:"}
    ])
    try:
        return json.loads(answer)["kpis"]
    except Exception:
        return {}

def summarize(text: str) -> str:
    answer = _chat_llm([
        {"role": "system", "content": SYSTEM_PROMPT_DE},
        {"role": "user",
         "content": f"{SUMMARY_PROMPT}\n\n{text}\n\n### Zusammenfassung:"}
    ])
    return answer.strip()




def analyse_and_store(doc: Document, session):
    """Alle Analyseschritte für **ein** Dokument ausführen."""
    # Zusammenfassung
    if not doc.summary and doc.content:
        doc.summary = summarize(doc.content[:4000])

    # NER
    if doc.content:
        for ent in nlp(doc.content).ents:
            session.add(Entity(
                document=doc,
                label=ent.label_,
                text=ent.text,
                start_char=ent.start_char,
                end_char=ent.end_char,
            ))

    # KPI-Extraktion
    kpis = {}
    try:
        kpis = extract_kpis(doc.content or "")
    except Exception as e:
        print(f"[KPI] Extraction failed in doc {doc.id}: {e}")

    for k, v in kpis.items():
        session.add(Fact(
            doc_id=doc.id,
            category="KENNZAHL",
            key=k,
            value=str(v),
        ))


# ─────────────────────────────────────────────────────────────
def analyse_all():
    """Alle gespeicherten Dokumente durch­analysieren."""
    with get_session() as session:
        docs = session.query(Document).all()
        for d in docs:
            analyse_and_store(d, session)
        session.commit()
    print("[Analysis] Completed summarization + NER.")
