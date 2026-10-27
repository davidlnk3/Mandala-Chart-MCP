import json
from pathlib import Path
from pypdf import PdfReader

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.prompts import base
from pydantic import Field

mcp = MCPServer("Mandala_Chart", log_level="ERROR")

NOTES_DIR = (Path.home() / "Documents" / "notes").resolve()

DOCS_DIR = Path(__file__).parent / "docs"
DOCS_DIR.mkdir(exist_ok=True)

@mcp.tool(
    name="read_notes",
    description="Reads the content of notes that the user wrote in order to know him better."
)
def read_notes(
    path: str = Field(description="Path of the file containing the notes that are relevant to the user.")
):
    full = (NOTES_DIR / path).resolve()
    if not full.is_relative_to(NOTES_DIR):
        raise ValueError(f"Path is outside a 'notes' folder")

    if path.endswith(".txt"):
        try:
            with open(full, "r") as file:
                content = file.read()
                return content
        except Exception:
            raise ValueError(f"File not found")
    elif path.endswith(".pdf"):
        try:
            reader = PdfReader(full)
            return "\n".join(page.extract_text() for page in reader.pages)
        except Exception:
            raise ValueError(f"File not found")


@mcp.resource("docs://documents", mime_type="application/json")
def list_documents() -> str:
    return json.dumps(sorted(path.stem for path in DOCS_DIR.glob("*.md")))


@mcp.resource("docs://documents/{doc_id}", mime_type="text/markdown")
def read_document(doc_id: str) -> str:
    path = (DOCS_DIR / f"{doc_id}.md").resolve()
    if path.parent != DOCS_DIR.resolve() or not path.is_file():
        raise ValueError(f"Document not found: {doc_id}")
    return path.read_text(encoding="utf-8")


@mcp.prompt(
    name="generate_mandalart",
    description="Generates the full Mandala Chart in Markdown format from one goal."
)

def mandalart_gen(
    goal:str = Field(description="The main goal to achieve.")
) -> list[base.Message]:
    prompt = f"""
Generate a Mandala Chart in Markdown format. The most important goal is: <goal>{goal}</goal>.
It will be written first and must start with the character #.

Then second tier goals will appear preceded by ##. 
They are the 8 categories or sub-goals required to achieve the main goal.

In between the second tier goals or categories should be represented the third tier goals. 
They are 8 for each second tier goal and must be preceded by ###. 
These should be presented as small, repeatable, daily or weekly actions that have to be taken in order to achieve its parent (secont tier) goal.
    """
    return [base.UserMessage(prompt)]



if __name__ == "__main__":
    mcp.run(transport="stdio")