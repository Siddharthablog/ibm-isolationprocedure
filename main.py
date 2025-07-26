import re
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Input(BaseModel):
    text: str
    query: Optional[str] = None

class Output(BaseModel):
    procedure: Optional[str] = None
    steps: Optional[str] = None
    message: str

# Matches something like FSPSP10 followed by lines of steps
def find_procedure_steps(text: str, procedure_code: str) -> Optional[str]:
    # Normalize input
    procedure_code = procedure_code.strip().upper()

    # Escape for regex safety
    escaped_code = re.escape(procedure_code)

    # Match starting at FSPSP10 and go until next all-caps token (like FSPABC1)
    pattern = re.compile(
        rf"({escaped_code})(.*?)\n(?=[A-Z0-9]{{6,}}(?:\s|$)|\Z)",
        re.DOTALL
    )
    match = pattern.search(text)
    if match:
        return match.group(0).strip()
    return None

@app.post("/search-isolation-procedure", response_model=Output)
def search_isolation_procedure(payload: Input):
    text = payload.text
    query = (payload.query or "").strip()

    if not query:
        return Output(procedure=None, steps=None, message="Please provide a procedure or error code to search.")

    result = find_procedure_steps(text, query)
    if result:
        return Output(procedure=query, steps=result, message="Procedure found.")
    else:
        return Output(procedure=query, steps=None, message="Procedure not found.")

