# database.py  (aktualisiert)
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from contextlib import contextmanager
from .config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

# ───────────────────────── Dokumente ──────────────────────────
class Document(Base):
    __tablename__ = "documents"
    id       = Column(Integer, primary_key=True, index=True)
    path     = Column(String, unique=True, index=True)
    content  = Column(Text)
    summary  = Column(Text)

    entities   = relationship("Entity", back_populates="document",
                              cascade="all, delete-orphan")
    facts      = relationship("Fact", back_populates="document",
                              cascade="all, delete-orphan")
    task_facts = relationship("TaskFact", back_populates="document",
                              cascade="all, delete-orphan")

# ───────────────────────── Einzelne benannte Entitäten ─────────
class Entity(Base):
    __tablename__ = "entities"
    id         = Column(Integer, primary_key=True, index=True)
    doc_id     = Column(Integer, ForeignKey("documents.id"))
    label      = Column(String)   # PERSON, ORG, DATE, …
    text       = Column(String)
    start_char = Column(Integer)
    end_char   = Column(Integer)

    document = relationship("Document", back_populates="entities")

# ───────────────────────── Generische Fakten ──────────────────
class Fact(Base):
    __tablename__ = "facts"
    id         = Column(Integer, primary_key=True)
    doc_id     = Column(Integer, ForeignKey("documents.id"))
    category   = Column(String)   # PERSON, DIMENSION, COST, …
    key        = Column(String)   # z. B. 'Länge', 'Kosten'
    value      = Column(String)   # normalisierter Wert
    unit       = Column(String, nullable=True)
    raw_text   = Column(Text)
    start_char = Column(Integer)
    end_char   = Column(Integer)

    document = relationship("Document", back_populates="facts")

# ───────────────────────── Mehrfach-Aufgaben ───────────────────
class TaskFact(Base):
    __tablename__ = "task_facts"
    id       = Column(Integer, primary_key=True)
    doc_id   = Column(Integer, ForeignKey("documents.id"))
    task     = Column(String)    # Beschreibung
    person   = Column(String)    # Verantwortlicher
    due      = Column(String, nullable=True)  # Fälligkeit (ISO, KW, …)
    raw_text = Column(Text)

    document = relationship("Document", back_populates="task_facts")

# Tabellen (falls noch nicht vorhanden) erzeugen
Base.metadata.create_all(bind=engine)

# ───────────────────────── Session-Helper ──────────────────────
@contextmanager
def get_session():
    sess = SessionLocal()
    try:
        yield sess
        sess.commit()
    except Exception:
        sess.rollback()
        raise
    finally:
        sess.close()
