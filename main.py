from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re

app = FastAPI()

class PDFInput(BaseModel):
    text: str  # PDF extracted text as input

class IsolationProcedure(BaseModel):
    code: str
    title: str
    description: str

class Output(BaseModel):
    original_text: str
    procedures: List[IsolationProcedure]

@app.post("/search-isolation-procedures", response_model=Output)
async def search_isolation_procedures(pdf_input: PDFInput):
    text = pdf_input.text.strip()
    procedures = []

    # Regex explanation:
    # - (FSPSP\d{2}) : matches codes like FSPSP01
    # - \s+(.+?)      : matches the title after the code (stops at period OR first new line)
    # - (.*?)(?=FSPSP\d{2}|\Z): matches description until next code or end of text
    pattern = re.compile(
        r'(FSPSP\d{2})\s+([^\n]+)\n?(.*?)(?=(FSPSP\d{2})|\Z)',
        re.DOTALL | re.MULTILINE
    )

    for match in pattern.finditer(text):
        code = match.group(1).strip()
        title = match.group(2).strip()
        description = match.group(3).strip()
        # Optionally, collapse excessive whitespace in description
        description = re.sub(r'\n\s*', '\n', description).strip()
        procedures.append(IsolationProcedure(
            code=code,
            title=title,
            description=description
        ))

    return {"original_text": text, "procedures": procedures}
