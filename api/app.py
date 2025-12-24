from fastapi import FastAPI
from llm import run_strategicky_nakupci

app = FastAPI(title="AI Strategický Nákupčí API")

@app.post("/analyze")
def analyze():
    result = run_strategicky_nakupci()
    return {
        "status": "ok",
        "result": result
    }