# consola.py
import requests
from core.interview import generar_pregunta

EVAL_URL = "http://127.0.0.1:8001/evaluate"

def iniciar_consola():
    print("🤖 ISA - Entrevistas de trabajo\n")
    while True:
        pregunta = generar_pregunta()
        print(f"❓ {pregunta}")
        respuesta = input("📝 Tu respuesta: ")

        if respuesta.lower() in ["salir", "exit", "quit"]:
            print("👋 Entrevista finalizada.")
            break

        payload = {"pregunta": pregunta, "respuesta": respuesta, "use_cache": True}
        try:
            r = requests.post(EVAL_URL, json=payload, timeout=180)
            r.raise_for_status()
            evaluacion = r.json()
        except Exception as e:
            evaluacion = {"error": f"No se pudo evaluar: {e}"}

        print(f"📊 Evaluación: {evaluacion}\n")

if __name__ == "__main__":
    iniciar_consola()
