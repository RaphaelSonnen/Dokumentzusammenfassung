import typer
from pathlib import Path
from rich import print
from .ingest import ingest_folder
from .analysis import analyse_all
from .index_builder import build_vector_index
from .chat_backend import get_query_engine

app = typer.Typer(help="Local Doc AI CLI – ingest, analyse, build index, chat")

@app.command()
def ingest(path: Path):
    """Load & parse all documents in PATH."""
    ingest_folder(path)

@app.command("analyse")
def analyse():
    """Run summarization + NER over newly ingested docs."""
    analyse_all()

@app.command("build-index")
def build_index():
    """Create / update Chroma vector index."""
    build_vector_index()

@app.command("convert-to-pdf")
def convert_to_pdf():
    """Konvertiert alle unterstützten Dateien in PDFs."""
    from .convert_all_to_pdf import main as convert_main
    convert_main()



@app.command("chat")
def chat():
    """Interactive chat with your project docs."""
    engine = get_query_engine()
    print("Type your question (or 'exit'):")

    while True:
        try:
            q = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"exit", "quit"}:
            break
        resp = engine.query(q)
        print("\n[bold yellow]Answer:[/bold yellow]", resp.response)
        if resp.source_nodes:
            print("\n[i]Sources:[/i]")
            for i, n in enumerate(resp.source_nodes, 1):
                meta = n.node.metadata
                print(f" {i}. {Path(meta.get('doc_path','')).name} – score {n.score:.3f}")

@app.command("extract-facts")
def fact_job():
    """spaCy+LLM Fakten-Extraktion."""
    from .extract_facts import extract_facts
    extract_facts()
    print("[Facts] extraction done.")

if __name__ == "__main__":
    app()