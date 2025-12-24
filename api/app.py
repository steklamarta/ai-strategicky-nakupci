from fastapi import FastAPI
from pydantic import BaseModel
from llm import StrategicBuyerEngine

app = FastAPI(title="AI Strategický Nákupčí API")

engine = StrategicBuyerEngine()


class AnalysisRequest(BaseModel):
    vyzva: str
    nabidky: str


@app.post("/analyze")
def analyze(request: AnalysisRequest):
    return engine.run_full_analysis(
        vyzva_text=request.vyzva,
        nabidky_text=request.nabidky
    )
