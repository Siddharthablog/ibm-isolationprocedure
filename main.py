from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import re

app = FastAPI()

class TextInput(BaseModel):
    text: str

class ProcedureDetail(BaseModel):
    code: str
    title: str
    page_number: Optional[int]  # Populate if you parse TOC
    excerpt: str

class Output(BaseModel):
    original_text: str
    matches: List[ProcedureDetail]

# EXAMPLE: You would typically extract this index from the PDF TOC at startup
ISOLATION_CODE_INDEX = {
    "DSKIP03": {"title": "Disk unit isolation procedure", "page": 7},
    "BMC0006": {"title": "eBMC isolation procedures", "page": 13},
    "HB00008": {"title": "Host boot isolation procedures", "page": 38},
    # ...add more codes as parsed from the real PDF
}

@app.post("/search-isolation-procedure", response_model=Output)
async def search_isolation_procedure(input_text: TextInput):
    text = input_text.text.strip()
    matches = []

    # Regex to find known procedure/error codes or keywords like "disk failure"
    code_pattern = re.compile(r"\b([A-Z]{3,5}\d{2,5})\b", re.IGNORECASE)
    codes_found = code_pattern.findall(text)

    # Simple match for keywords in TOC index if codes not found
    keywords = ['disk', 'bmc', 'boot', 'expansion', 'console', 'power', 'network', 'drawer']
    found_keyword = next((k for k in keywords if k in text.lower()), None)

    if codes_found:
        for code in codes_found:
            norm_code = code.upper()
            if norm_code in ISOLATION_CODE_INDEX:
                title = ISOLATION_CODE_INDEX[norm_code]['title']
                page = ISOLATION_CODE_INDEX[norm_code]['page']
                # TODO: Actually extract excerpt for this code from PDF text using pdfminer, PyPDF2, etc.
                excerpt = f"See procedure '{title}' on page {page}."
                matches.append(ProcedureDetail(code=norm_code, title=title, page_number=page, excerpt=excerpt))
    elif found_keyword:
        # Keyword fallback if no code match
        for code, v in ISOLATION_CODE_INDEX.items():
            if found_keyword in v['title'].lower():
                matches.append(ProcedureDetail(code=code, title=v['title'], page_number=v['page'],
                                               excerpt=f"See '{v['title']}' on page {v['page']}."))
    # Optionally return a fallback message if no matches found
    return {"original_text": text, "matches": matches}

