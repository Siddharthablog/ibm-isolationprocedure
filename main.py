from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import re

app = FastAPI()

# Input model: same style as adapter-ai
class TextInput(BaseModel):
    text: str  # Raw PDF text input

# Output model: error code and its resolution steps
class ErrorFixDetail(BaseModel):
    error_code: str
    description: str
    resolution_steps: List[str]

class Output(BaseModel):
    original_text: str
    matches: List[ErrorFixDetail]

@app.post("/search-error-fix", response_model=Output)
async def search_error_fix(input_text: TextInput):
    text = input_text.text.strip()
    matches = []

    # Regex to find error blocks
    pattern = re.compile(
        r"Error Code[:\s]+(?P<code>MEXI\w+)[\r\n]+"
        r"Description[:\s]+(?P<desc>.+?)[\r\n]+"
        r"Resolution Steps:(?P<steps>.*?)(?=\n---|\Z)",
        re.DOTALL
    )

    for match in pattern.finditer(text):
        code = match.group("code").strip()
        desc = match.group("desc").strip()

        steps_block = match.group("steps").strip()
        # Split steps by line numbers or dashes
        steps = [step.strip(" -.") for step in re.split(r'\n\d+\.\s+|\n-\s+|\n', steps_block) if step.strip()]

        matches.append(ErrorFixDetail(
            error_code=code,
            description=desc,
            resolution_steps=steps
        ))

    return {"original_text": text, "matches": matches}
