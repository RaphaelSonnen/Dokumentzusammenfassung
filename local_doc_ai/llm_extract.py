from pydantic import BaseModel, Field
from typing import List
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from .config import SYSTEM_PROMPT_DE

# Ollama-LLM global registrieren (Deutsch)
Settings.llm = Ollama(
    model="gemma3:27b",
    request_timeout=300.0,
    system_prompt=SYSTEM_PROMPT_DE,
)

class TaskItem(BaseModel):
    task: str   = Field(..., description="Aufgabenbeschreibung")
    person: str = Field(..., description="Verantwortliche Person")
    due: str | None = Field(None, description="Fälligkeitsdatum")

class TaskList(BaseModel):
    tasks: List[TaskItem]

PROMPT = (
    "Identifiziere alle **Aufgaben** (To-Dos, Maßnahmen) im folgenden Text. "
    "Gib sie als JSON-Objekt mit dem Feld \"tasks\" zurück. "
    "Jede Aufgabe soll enthalten:\n"
    "- \"task\": Kurzbeschreibung (was ist zu tun?)\n"
    "- \"person\": zuständige Person oder Organisation (falls genannt)\n"
    "- \"due\": Fälligkeits- oder Terminangabe (falls vorhanden)\n\n"
    "Beispiel:\n"
    "{\n"
    "  \"tasks\": [\n"
    "    {\"task\": \"Schalungsplan prüfen\", \"person\": \"Ingenieurbüro ABC\", \"due\": \"2024-06-15\"}\n"
    "  ]\n"
    "}\n\n"
    "Falls keine Aufgaben vorkommen, gib \"tasks\": [] zurück. "
    "**Antworte ausschließlich mit dem JSON, ohne jede Erklärung.**"
)


task_extractor = LLMTextCompletionProgram.from_defaults(
    output_cls=TaskList,
    prompt_template_str=PROMPT,
    strip_json_markdown=True,
)
