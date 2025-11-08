# 🤖 ISA - Inteligencia para la Selección de Aspirantes

**Autor:** Dylan Vargas  
**Versión:** 1.0  
**Lenguajes:** Python · Java  
**Frameworks:** Streamlit · FastAPI · JUnit5  
**IA:** Ollama (Modelos locales: LLaMA3 / Phi3)  
**Despliegue:** Render · Ngrok  

---

## 🧠 Descripción del Proyecto

ISA (Inteligencia para la Selección de Aspirantes) es una plataforma inteligente de evaluación de candidatos, diseñada para asistir a empresas durante procesos de selección de personal.  
El sistema permite realizar **entrevistas automáticas**, analizar respuestas con **inteligencia artificial**, y generar un **puntaje global** por competencias.

ISA cuenta con dos vistas principales:
- 🏢 **Panel de Empresa:** configuración de criterios de evaluación, número de preguntas y visualización del ranking.
- 👤 **Plataforma de Candidato:** entrevistas guiadas por IA, análisis de respuestas y puntuaciones automáticas.

---

## 🧩 Arquitectura General

ISA está compuesto por tres módulos principales:

| Componente | Descripción |
|-------------|-------------|
| `app.py` | Interfaz principal en **Streamlit** (Frontend). |
| `services/evaluator_service.py` | API en **FastAPI** que comunica con el modelo de IA. |
| `core/` | Lógica interna (generación de preguntas, autenticación, caché). |

También incluye una versión Java experimental con hilos (`ISA-java-Threads`) para pruebas multihilo y automatización.

---

## ⚙️ Funcionalidades Principales

- 🔐 **Autenticación local** con cifrado de contraseñas (bcrypt) y JWT.
- 🧩 **Evaluación automática** de respuestas con IA.
- 🧮 **Cálculo ponderado** de puntajes por áreas (técnico, comunicación, razonamiento, colaboración).
- 🏆 **Ranking de candidatos** con guardado local.
- 🕓 **Modo empresa/candidato** completamente separados.
- 💾 **Persistencia en JSON** local (usuarios, configuraciones, resultados).
- ⚙️ **Configuración dinámica** del número de preguntas.
- ☁️ **Despliegue remoto** con Render y acceso externo con Ngrok.

---

## 🧠 Arquitectura Técnica

```plaintext
┌──────────────────────────────┐
│        Streamlit (UI)        │
│  app.py                      │
│  ├─ Empresa / Candidato      │
│  └─ Autenticación            │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│   FastAPI (services/)        │
│  evaluator_service.py        │
│  ├─ Recibe pregunta/respuesta│
│  ├─ Llama al modelo IA (Ollama)
│  └─ Devuelve puntajes JSON   │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│      Core (Lógica IA)        │
│  ├─ interview.py (preguntas) │
│  ├─ cache.py (optimizaciones)│
│  └─ auth.py (usuarios JWT)   │
└──────────────────────────────┘
🧪 Pruebas Unitarias (Java + Maven + JUnit5)
En la versión ISA-java-Threads, se implementaron 15 pruebas unitarias que validan la lógica del evaluador y sus hilos concurrentes.

Ejecutar las pruebas:

bash
Copiar código
mvn clean test
Resultado esperado:

yaml
Copiar código
BUILD SUCCESS
Tests run: 15, Failures: 0, Errors: 0
🚀 Despliegue y Ejecución
🔧 Requisitos
Python 3.10 o superior

Ollama (para ejecutar modelos locales, opcional)

Java 17 (para módulo Java)

Maven

Git

🧰 Instalación (modo local)
1️⃣ Clonar el repositorio:

bash
Copiar código
git clone https://github.com/DyranDev/ISA-evaluator.git
cd ISA-evaluator
2️⃣ Instalar dependencias:

bash
Copiar código
pip install -r requirements.txt
3️⃣ Ejecutar el backend (API):

bash
Copiar código
uvicorn services.evaluator_service:app --host 127.0.0.1 --port 8001
4️⃣ Ejecutar el frontend (Streamlit):

bash
Copiar código
streamlit run app.py
5️⃣ Abrir en el navegador:

arduino
Copiar código
http://localhost:8501
☁️ Despliegue remoto (Render / Streamlit Cloud)
Opción 1: Render
Crear un nuevo servicio Web Service.

Vincular el repositorio de GitHub.

En el campo Start Command, escribir:

bash
Copiar código
uvicorn services.evaluator_service:app --host 0.0.0.0 --port 8000
Guardar y desplegar.
→ Render asignará una URL pública del tipo:

arduino
Copiar código
https://isa-evaluator.onrender.com
Opción 2: Ngrok (local temporal)
bash
Copiar código
ngrok http 8501
Ngrok generará un enlace temporal público para tu Streamlit local.

🔒 Autenticación y Seguridad
ISA incluye un sistema de usuarios con:

Registro y login local

Contraseñas cifradas con bcrypt

Tokens de sesión JWT

Base JSON local (users.json)

Ejemplo de estructura:

json
Copiar código
{
  "username": "empresa1",
  "password": "$2b$12$u4...",
  "role": "empresa"
}
🧑‍💻 Créditos
Proyecto desarrollado por:
👨‍💻 Dylan Vargas
Estudiante de Ingeniería de Sistemas
Proyecto de Inteligencia Artificial aplicada a procesos de selección automatizados.

🏁 Conclusión
ISA demuestra cómo integrar IA, multihilos, autenticación y despliegue web en un mismo entorno.
Su arquitectura híbrida entre Python y Java permite flexibilidad, escalabilidad y eficiencia en tiempo real.