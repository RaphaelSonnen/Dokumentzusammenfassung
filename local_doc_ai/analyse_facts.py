
from .database import Fact, Document, get_session
from .ner import nlp  # spaCy + EntityRuler
from .llm_extract import task_extractor  # LlamaIndex Extractor
from pint import UnitRegistry

ureg = UnitRegistry()

def extract_facts(doc: Document, session):
    # 1) spaCy-NER
    for ent in nlp(doc.content).ents:
        if ent.label_ in {"PERSON", "ORG", "DATE", "MONEY"}:
            session.add(Fact(doc_id=doc.id,
                             category=ent.label_,
                             key=ent.label_,
                             value=ent.text,
                             raw_text=doc.content[ent.start_char:ent.end_char],
                             start_char=ent.start_char,
                             end_char=ent.end_char))
        elif ent.label_ == "DIMENSION":
            qty = ureg(ent.text)
            session.add(Fact(doc_id=doc.id,
                             category="DIMENSION",
                             key="dimension",
                             value=str(qty.magnitude),
                             unit=str(qty.units)))

    # 2) LLM (Aufgaben/Verantwortungen)
    tasks = task_extractor.extract(doc.content)
    for t in tasks:
        session.add(Fact(doc_id=doc.id,
                         category="TASK",
                         key=t["task"],
                         value=t["person"],
                         raw_text=t["raw_fragment"]))
