import spacy, re
nlp = spacy.load("de_core_news_lg")           # ← Option A

ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.add_patterns([
    {"label": "KOSTEN",      "pattern": [{"TEXT": {"REGEX": r"^\d+[.,]?\d*\s?(€|EUR|Euro|Mio\s?€)$"}}]},
    {"label": "MATERIAL",    "pattern": [{"TEXT": {"REGEX": r"^(C\d{2}/\d{2}|S\d{3}[A-Z]{0,2})$"}}]},
    {"label": "PROJEKT_META","pattern": [{"TEXT": {"REGEX": r"^\d{4}[-_]\d{3,4}([-_][A-Z]{1,3})?$"}}]},
    {"label": "DIMENSION", "pattern": [{"TEXT": {"REGEX": r"^Ø?\d+[.,]?\d*\s?(mm|cm|m²|m|t)$"}}]},
])
