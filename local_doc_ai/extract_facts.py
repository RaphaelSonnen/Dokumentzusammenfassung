# extract_facts.py
from .database import get_session, Document, Fact, TaskFact
from .ner import nlp                           # spaCy-Pipeline mit NER + EntityRuler
from .llm_extract import task_extractor , TaskList        # SimpleExtractor o. Ä.; kann None sein
from pint import UnitRegistry
ureg = UnitRegistry()

def extract_facts():
    with get_session() as s:
        for doc in s.query(Document).all():

            # ── 1) Regel- & NER-basierte Fakten ────────────────────────────────
            for ent in nlp(doc.content).ents:

                # Personen, Organisationen, Daten, Beträge
                if ent.label_ in {"PERSON", "ORG", "DATE", "MONEY"}:
                    s.add(
                        Fact(
                            doc_id=doc.id,
                            category=ent.label_,         # PERSON, ORG, …
                            key=ent.label_,
                            value=ent.text,
                            raw_text=ent.text,
                            start_char=ent.start_char,
                            end_char=ent.end_char,
                        )
                    )

                # Maße & Mengen über EntityRuler-Label „DIMENSION“
                elif ent.label_ == "DIMENSION":
                    try:
                        qty = ureg(ent.text.replace(",", "."))   # Komma zulassen
                        magnitude = float(qty.magnitude)
                        unit = str(qty.units)
                    except Exception:
                        # Fallback, falls Pint das Format nicht versteht
                        magnitude, unit = ent.text, None

                    s.add(
                        Fact(
                            doc_id=doc.id,
                            category="DIMENSION",
                            key="dimension",
                            value=str(magnitude),
                            unit=unit,
                            raw_text=ent.text,
                            start_char=ent.start_char,
                            end_char=ent.end_char,
                        )
                    )

                elif ent.label_ in {"COST", "MATERIAL", "PROJECT_META"}:
                    s.add(
                        Fact(
                            doc_id=doc.id,
                            category=ent.label_,
                            key=ent.label_.lower(),
                            value=ent.text,
                            raw_text=ent.text,
                            start_char=ent.start_char,
                            end_char=ent.end_char,
                        )
                    )


            # ── 2) LLM-gestützte Aufgaben-Extraktion ──────────────────────────
            if task_extractor is not None:
                try:
                    tl: TaskList = task_extractor(context=doc.content)  # Callable!
                    for t in tl.tasks:
                        s.add(TaskFact(
                            doc_id=doc.id,
                            task=t.task,
                            person=t.person,
                            due=t.due,
                            raw_text=t.task  # oder eigener Ausschnitt
                        ))
                except Exception as e:
                    print(f"[Facts] LLM parse failed in {doc.path}: {e}")

        s.commit()
        print("[Facts] extraction done.")
