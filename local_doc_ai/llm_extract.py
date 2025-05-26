# llm_extract.py
from pydantic import BaseModel, Field
from typing import List
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama

# 1) Ollama-LLM global registrieren
Settings.llm = Ollama(model="gemma3:27b", request_timeout=300.0)  # :contentReference[oaicite:3]{index=3}

class TaskItem(BaseModel):
    task: str   = Field(..., description="Aufgaben­beschreibung")
    person: str = Field(..., description="Verantwortliche Person")
    due: str | None = Field(None, description="Fälligkeits­datum")

class TaskList(BaseModel):
    tasks: List[TaskItem]

PROMPT = (
    "Extrahiere **alle** Aufgaben in einer JSON-Liste:\n"
    "```json\n"
    "{\n  \"tasks\": [\n    {\"task\": \"…\", \"person\": \"…\", \"due\": \"…\"},\n    …\n  ]\n}\n"
    "```\n"
    "Gib ausschließlich das JSON ohne weitere Kommentare zurück."
)

task_extractor = LLMTextCompletionProgram.from_defaults(
    output_cls=TaskList,
    prompt_template_str=PROMPT,
    strip_json_markdown=True,   # entfernt ```json Blöcke  :contentReference[oaicite:4]{index=4}
)
