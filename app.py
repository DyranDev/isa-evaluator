# app.py
import streamlit as st
import requests
from core.interview import generar_pregunta

API_URL = "https://isa-evaluator.onrender.com/evaluate"

st.set_page_config(
    page_title="ISA - Intelligent Screening Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 ISA - *Inteligencia para la Selección de Aspirantes*")

# ---- Selección de rol ----
if "rol" not in st.session_state:
    st.session_state.rol = None

# Inicializar num_preguntas globalmente para toda la app
if "num_preguntas" not in st.session_state:
    st.session_state.num_preguntas = 5
if "prev_num_preguntas" not in st.session_state:
    st.session_state.prev_num_preguntas = st.session_state.num_preguntas


if st.session_state.rol is None:
    st.markdown("### Selecciona tu rol:")
    if st.button("🏢 Entrar como Empresa", key="btn_empresa"):
        st.session_state.rol = "empresa"
        st.rerun()
    if st.button("👤 Entrar como Candidato", key="btn_candidato"):
        st.session_state.rol = "candidato"
        st.rerun()

# =============================
#        VISTA EMPRESA
# =============================
if st.session_state.rol == "empresa":
    st.header("🏢 Panel de Empresa")

    # Inicializar pesos
    if "pesos" not in st.session_state:
        st.session_state.pesos = {
            "comunicacion": 0.25,
            "tecnico": 0.40,
            "razonamiento": 0.25,
            "colaboracion": 0.10,
        }

    st.markdown("### ⚙️ Configuración de criterios")
    for k, v in st.session_state.pesos.items():
        st.slider(
            f"Peso {k}",
            0.0, 1.0,
            value=v,
            step=0.05,
            key=f"peso_{k}"
        )

    # Normalizar pesos
    total = sum(st.session_state.pesos.values())
    if total > 0:
        for k in st.session_state.pesos:
            st.session_state.pesos[k] = round(st.session_state.pesos[k] / total, 2)
    st.success(f"Pesos normalizados: {st.session_state.pesos}")

# ---- Inicialización de num_preguntas antes de usarlo ----
    if "num_preguntas" not in st.session_state:
        st.session_state.num_preguntas = 5
    if "prev_num_preguntas" not in st.session_state:
        st.session_state.prev_num_preguntas = st.session_state.num_preguntas

    # ---- Widget de número de preguntas ----
    nuevo_num = st.number_input(
        "📋 Número de preguntas por entrevista",
        min_value=1,
        max_value=20,
        step=1,
        value=st.session_state.num_preguntas
    )
    # Actualiza session_state solo si cambió
    if nuevo_num != st.session_state.num_preguntas:
        st.session_state.num_preguntas = nuevo_num
        st.session_state.prev_num_preguntas = nuevo_num



    # Guardar número previo para detectar cambios
    if "prev_num_preguntas" not in st.session_state:
        st.session_state.prev_num_preguntas = st.session_state.num_preguntas

    st.info(f"Se configuraron {st.session_state.num_preguntas} preguntas por entrevista.")

    # Ranking de candidatos
    if "ranking" not in st.session_state:
        st.session_state.ranking = []

    st.markdown("### 🏆 Ranking de candidatos")
    if st.session_state.ranking:
        for i, cand in enumerate(
            sorted(st.session_state.ranking, key=lambda x: x['final_score'], reverse=True),
            1
        ):
            st.write(f"**{i}. {cand['nombre']}** — Puntaje: {cand['final_score']}/5")
    else:
        st.info("Aún no hay candidatos evaluados.")

    if st.button("⬅️ Volver al menú principal", key="volver_empresa"):
        st.session_state.rol = None
        st.rerun()

# =============================
#        VISTA CANDIDATO
# =============================
elif st.session_state.rol == "candidato":
    st.markdown("Plataforma de entrevistas con inteligencia artificial para evaluar candidatos en tiempo real.")

        # Regenerar preguntas si cambió el número
    if ("preguntas" not in st.session_state) or (st.session_state.prev_num_preguntas != st.session_state.num_preguntas):
        st.session_state.preguntas = [generar_pregunta() for _ in range(st.session_state.num_preguntas)]
        st.session_state.index = 0
        st.session_state.historial = []
        st.session_state.ultima_eval = None
        st.session_state.result_saved = False
        st.session_state.prev_num_preguntas = st.session_state.num_preguntas


    if "historial" not in st.session_state:
        st.session_state.historial = []

    if "ultima_eval" not in st.session_state:
        st.session_state.ultima_eval = None

    if "result_saved" not in st.session_state:
        st.session_state.result_saved = False

    if "nombre" not in st.session_state:
        st.session_state.nombre = "Candidato Anónimo"

    # Pregunta actual
    if st.session_state.index < len(st.session_state.preguntas):
        pregunta_actual = st.session_state.preguntas[st.session_state.index]

        st.markdown(f"### ❓ **Pregunta {st.session_state.index + 1} de {len(st.session_state.preguntas)}**")
        st.markdown(f"#### {pregunta_actual}")

        respuesta = st.text_area(
            "✍️ Tu respuesta:",
            placeholder="Escribe tu respuesta aquí...",
            key=f"respuesta_{st.session_state.index}"
        )

        if st.button("Evaluar respuesta", key=f"eval_{st.session_state.index}") and respuesta.strip():
            payload = {"pregunta": pregunta_actual, "respuesta": respuesta}
            try:
                r = requests.post(API_URL, json=payload, timeout=180)
                r.raise_for_status()
                evaluacion = r.json()
            except Exception as e:
                evaluacion = {"status": "failed", "error": str(e)}

            st.session_state.ultima_eval = {
                "pregunta": pregunta_actual,
                "respuesta": respuesta,
                "evaluacion": evaluacion
            }

        # Mostrar evaluación
        if st.session_state.ultima_eval:
            turno = st.session_state.ultima_eval
            st.markdown(f"**Respuesta:** {turno['respuesta']}")
            eval_ = turno["evaluacion"]

            if "error" in eval_:
                st.error(eval_["error"])
            elif eval_.get("status") == "failed":
                st.warning(f"⚠️ La evaluación falló: {eval_.get('error')}")
                if st.button("🔄 Reintentar evaluación", key=f"retry_{st.session_state.index}"):
                    try:
                        retry = requests.post(API_URL, json={
                            "pregunta": turno["pregunta"],
                            "respuesta": turno["respuesta"]
                        })
                        retry.raise_for_status()
                        turno["evaluacion"] = retry.json()
                        st.session_state.ultima_eval = turno
                        st.rerun()
                    except Exception as e:
                        st.error(f"Nuevo fallo al reintentar: {e}")
            else:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🗣 Comunicación", eval_["scores"].get("comunicacion", 0))
                col2.metric("💡 Técnico", eval_["scores"].get("tecnico", 0))
                col3.metric("🧠 Razonamiento", eval_["scores"].get("razonamiento", 0))
                col4.metric("🤝 Colaboración", eval_["scores"].get("colaboracion", 0))
                st.progress(min(eval_["final_score"] / 5, 1.0))
                st.info(f"💬 {eval_.get('comment','')}")

            if st.button("➡️ Siguiente pregunta", key=f"siguiente_{st.session_state.index}"):
                st.session_state.historial.append(st.session_state.ultima_eval)
                st.session_state.index += 1
                st.session_state.ultima_eval = None
                st.rerun()

    else:
        st.success("✅ Entrevista finalizada")

    # Evaluación final
    if st.session_state.index >= len(st.session_state.preguntas):
        st.subheader("🏆 Evaluación final del candidato")

        total_scores = {"comunicacion": 0, "tecnico": 0, "razonamiento": 0, "colaboracion": 0}
        n = 0

        for turno in st.session_state.historial:
            eval_ = turno["evaluacion"]
            scores = eval_.get("scores")
            if scores:
                n += 1
                for k in total_scores:
                    try:
                        val = float(scores.get(k, 0) or 0)
                    except (ValueError, TypeError):
                        val = 0
                    total_scores[k] += val

        if n > 0:
            promedios = {k: round(v / n, 2) for k, v in total_scores.items()}
            final_score = round(sum(promedios.values()) / len(promedios), 2)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🗣 Comunicación", promedios["comunicacion"])
            col2.metric("💡 Técnico", promedios["tecnico"])
            col3.metric("🧠 Razonamiento", promedios["razonamiento"])
            col4.metric("🤝 Colaboración", promedios["colaboracion"])

            st.progress(min(final_score / 5, 1.0))
            st.success(f"⭐ Calificación final: {final_score}/5")

            st.text_input(
                "Tu nombre:",
                value=st.session_state.nombre,
                key="input_nombre_final"
            )

            if not st.session_state.result_saved and st.session_state.nombre.strip():
                if "ranking" not in st.session_state:
                    st.session_state.ranking = []
                st.session_state.ranking.append({
                    "nombre": st.session_state.nombre.strip(),
                    "final_score": final_score
                })
                st.session_state.result_saved = True
                st.success("Tus resultados fueron enviados a la empresa ✅")
        else:
            st.error("⚠️ No se pudieron calcular promedios porque todas las evaluaciones fallaron.")

    if st.button("⬅️ Volver al menú principal", key="volver_candidato"):
        st.session_state.rol = None
        for key in ["preguntas", "index", "historial", "ultima_eval", "nombre", "result_saved"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
