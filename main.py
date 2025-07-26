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

def find_procedure_steps(text: str, procedure_code: str) -> Optional[str]:
    # Normalize input
    procedure_code = procedure_code.strip().upper()

    # Escape for regex safety
    escaped_code = re.escape(procedure_code)

    # A more flexible pattern:
    # 1. Matches the escaped_code.
    # 2. Captures any characters (including newlines due to re.DOTALL).
    # 3. Stops when it encounters:
    #    - A newline followed by a potential procedure code pattern (e.g., FSPxxxx)
    #    - Or the very end of the string.
    #    The lookahead for the next procedure code is made more general (FSP followed by digits)
    #    or any common pattern for the start of a new section.
    pattern = re.compile(
        rf"({escaped_code}.*?)(?=\n[A-Z]{{3}}[A-Z0-9]{{3,}}|\Z)", 
        re.DOTALL | re.MULTILINE
    )
    match = pattern.search(text)
    if match:
        # Return the captured group (the procedure code and its steps)
        return match.group(1).strip()
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
