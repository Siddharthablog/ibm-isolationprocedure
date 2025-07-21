from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re

app = FastAPI()

# Input model for uploaded PDF text
class TextInput(BaseModel):
    text: str  # Raw text extracted from the isolation procedure PDF

# Output model for one error code resolution block
class ErrorFixDetail(BaseModel):
    error_code: str
    description: str
    resolution_steps: List[str]

# Output model for API response
class Output(BaseModel):
    original_text: str
    matches: List[ErrorFixDetail]

# Updated endpoint name
@app.post("/search-isolation-procedure", response_model=Output)
async def search_isolation_procedure(input_text: TextInput):
    text = input_text.text.strip()

    # Debug logging to verify incoming data
    print("Received text input length:", len(text))
    print("First 300 characters of input text:")
    print(text[:300])

    matches = []

    # Flexible regex pattern to capture varied formatting
    pattern = re.compile(
        r"Error Code[:\s]+(?P<code>\w+).*?"
        r"Description[:\s]+(?P<desc>.+?)"
        r"Resolution Steps[:\s]*(?P<steps>.*?)(?=Error Code|\Z)",
        re.DOTALL | re.IGNORECASE
    )

    for match in pattern.finditer(text):
        code = match.group("code").strip()
        desc = match.group("desc").strip()

        # Parse and clean resolution steps
        steps_block = match.group("steps").strip()
        steps = [
            step.strip(" -.") 
            for step in re.split(r'\n|\r|\d+\.', steps_block) 
            if step.strip()
        ]

        matches.append(ErrorFixDetail(
            error_code=code,
            description=desc,
            resolution_steps=steps
        ))

    return {
        "original_text": text,
        "matches": matches
    }
