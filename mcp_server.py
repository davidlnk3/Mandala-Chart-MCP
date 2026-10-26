import json
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.prompts import base
from pydantic import Field

mcp = MCPServer("Mandala_Chart", log_level="ERROR")

DOCS_DIR = Path(__file__).parent / "docs"
DOCS_DIR.mkdir(exist_ok=True)

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