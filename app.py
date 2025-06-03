from fastapi import FastAPI
from pydantic import BaseModel
from retriever import retrieve_context
from scrape_dom import run_scraper_on_url
from fastapi.middleware.cors import CORSMiddleware

import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to the origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLInput(BaseModel):
    url: str

@app.post("/scan")
def scan_page(input: URLInput):
    try:
        result = run_scraper_on_url(input.url)
        return {"status": "success", "message": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}




# Request schema
class PatternRequest(BaseModel):
    summary: str  # e.g. "Clicking 'X' opened a subscription popup"

@app.post("/detect")
async def detect_bait_switch(req: PatternRequest):
    summary = req.summary
    retrieved_examples = retrieve_context(summary)

    # Construct the prompt
    prompt = f"""
You are a consumer protection expert. The following user interaction was observed:

User Action Summary:
{summary}

Here are previously documented bait-and-switch examples:
{chr(10).join('- ' + r for r in retrieved_examples)}

Does this qualify as a bait-and-switch dark pattern?
Reply with a simple Yes or No and a short reason.
"""

    # Call DeepSeek via Ollama
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek",
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json().get("response", "").strip()
    except Exception as e:
        return {"error": str(e)}

    return {
        "summary": summary,
        "retrieved_examples": retrieved_examples,
        "classification": result
    }
