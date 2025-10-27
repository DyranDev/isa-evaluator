# core/evaluator.py
import requests
import json
import re
from functools import lru_cache
from typing import Dict, Any

# Configuración
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:latest"   # Modelo rápido y ligero
REQUEST_TIMEOUT = 200     # ⏳ Tiempo máximo por request

# Rúbrica base
RUBRIC = {
    "criteria": [
        {"id": "comunicacion", "weight": 0.25, "desc": "Claridad, estructura y concreción."},
        {"id": "tecnico", "weight": 0.40, "desc": "Dominio del tema y precisión."},
        {"id": "razonamiento", "weight": 0.25, "desc": "Capacidad analítica y justificación."},
        {"id": "colaboracion", "weight": 0.10, "desc": "Actitud y trabajo en equipo."}
    ],
    "rubric_version": "v1"
}

# Prompt base
PROMPT_TEMPLATE = """
Eres un evaluador de entrevistas de trabajo.
Evalúa la respuesta del candidato a la pregunta dada, usando la siguiente rúbrica:

{rubric_text}

IMPORTANTE:
- Devuelve SOLO un JSON válido.
- No escribas texto fuera del JSON.
- No uses explicaciones fuera de las claves solicitadas.

Formato exacto:
{{
  "scores": {{ "comunicacion": <1-5>, "tecnico": <1-5>, "razonamiento": <1-5>, "colaboracion": <1-5> }},
  "comment": "<feedback breve en español>",
  "confidence": <0.0-1.0>
}}

Pregunta: "{pregunta}"
Respuesta del candidato: "{respuesta}"
"""

def _build_prompt(pregunta: str, respuesta: str) -> str:
    rubric_text = "\n".join(
        [f"- {c['id']} (peso {c['weight']}): {c['desc']}" for c in RUBRIC["criteria"]]
    )
    return PROMPT_TEMPLATE.format(
        pregunta=pregunta.replace('"', "'"),
        respuesta=respuesta.replace('"', "'"),
        rubric_text=rubric_text
    )

def _call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"   # 👈 pedimos JSON directamente
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        resp = r.json()
        return resp.get("response", "").strip()
    except requests.Timeout:
        return json.dumps({"status": "failed", "error": "Timeout"})
    except Exception as e:
        return json.dumps({"status": "failed", "error": str(e)})

def _extract_json(text: str) -> Dict[str, Any]:
    if not text:
        return {"error": "Respuesta vacía"}

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return {"error": "JSON inválido", "raw": text}
        return {"error": "No se encontró JSON", "raw": text}

def _aggregate(parsed: Dict[str, Any]) -> Dict[str, Any]:
    if parsed.get("status") == "failed":
        return parsed

    scores = parsed.get("scores", {})
    total = 0.0
    weight_sum = 0.0
    for c in RUBRIC["criteria"]:
        raw_val = scores.get(c["id"], 0)
        try:
            v = float(raw_val) if raw_val is not None else 0.0
        except (ValueError, TypeError):
            v = 0.0
        total += v * c["weight"]
        weight_sum += c["weight"]

    final_score = round(total / weight_sum, 2) if weight_sum else 0.0
    return {
        "scores": scores,
        "final_score": final_score,
        "comment": parsed.get("comment", ""),
        "confidence": parsed.get("confidence", 0.0),
        "rubric_version": RUBRIC["rubric_version"]
    }

@lru_cache(maxsize=512)
def evaluate_with_cache(pregunta: str, respuesta: str) -> Dict[str, Any]:
    return evaluate(pregunta, respuesta)

def evaluate(pregunta: str, respuesta: str) -> Dict[str, Any]:
    prompt = _build_prompt(pregunta, respuesta)
    raw = _call_ollama(prompt)
    parsed = _extract_json(raw)

    if "error" in parsed:
        return {**parsed, "raw": raw}

    return _aggregate(parsed)
