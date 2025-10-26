from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.evaluator import evaluate_with_cache, evaluate
import traceback

app = FastAPI(title="ISA Evaluator", version="0.1")

class EvalRequest(BaseModel):
    pregunta: str
    respuesta: str
    use_cache: bool = True

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/evaluate")
def evaluate_endpoint(req: EvalRequest):
    try:
        if req.use_cache:
            res = evaluate_with_cache(req.pregunta, req.respuesta)
        else:
            res = evaluate(req.pregunta, req.respuesta)
        return res
    except Exception as e:
        print("🔥 Error en evaluate_endpoint:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def warmup_model():
    print("🚀 Cargando modelo en Ollama...")
    try:
        _ = evaluate("Pregunta de prueba", "Respuesta de prueba")
        print("✅ Modelo precargado")
    except Exception as e:
        print(f"⚠️ Error en warmup: {e}")
