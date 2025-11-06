import random

PREGUNTAS_BASE = [
    "Cuéntame sobre ti y tu experiencia laboral.",
    "¿Cuál ha sido tu mayor logro profesional?",
    "¿Cómo manejas el trabajo bajo presión?",
    "Descríbeme una situación en la que resolviste un problema difícil.",
    "¿Por qué deberíamos contratarte para este puesto?"
]

def generar_pregunta():
    """Devuelve una pregunta de entrevista aleatoria."""
    return random.choice(PREGUNTAS_BASE)
