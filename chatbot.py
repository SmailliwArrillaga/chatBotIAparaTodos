

import streamlit as st
from groq import Groq

# ──────────────────────────────────────────────────────────────
# 1. CONFIGURACIÓN GENERAL
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Asistente - IA para Todos",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────
# 2. ESTILOS CSS
# ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
h1, h2, h3, h4, p, li, label {
    color: #153244;
}

.stApp {
    background: linear-gradient(
        135deg,
        rgba(255,255,255,1) 40%,
        rgba(184,177,216,0.18) 100%
    );
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        rgba(255,255,255,1) 0%,
        rgba(184,177,216,0.18) 100%
    );
    border-right: 1px solid rgba(21,50,68,0.08);
}

.stChatInput textarea {
    background-color: #ffffff !important;
    color: #153244 !important;
    border: 2px solid #7ECBE2 !important;
    border-radius: 14px !important;
}

.stChatInput textarea:focus {
    border: 2px solid #B8B1D8 !important;
    box-shadow: 0 0 0 0.2rem rgba(
        126,203,226,0.20
    ) !important;
}

[data-testid="stChatMessage"]:has(
    span[aria-label="user"]
) {
    background-color: #EEF9FC !important;
    border: 1px solid rgba(
        126,203,226,0.35
    ) !important;
    border-radius: 16px;
}

[data-testid="stChatMessage"]:has(
    span[aria-label="assistant"]
) {
    background-color: #F4F1FA !important;
    border: 1px solid rgba(
        184,177,216,0.45
    ) !important;
    border-radius: 16px;
}

.stChatMessage .stChatMessageAvatar {
    background-color: #153244 !important;
    color: white !important;
}

.stButton > button {
    background-color: #7ECBE2 !important;
    color: #153244 !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #B8B1D8 !important;
    color: #153244 !important;
}

div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 1px solid rgba(
        21,50,68,0.15
    ) !important;
}

[data-testid="stAlert"] {
    border-radius: 14px !important;
}

code {
    white-space: pre-wrap !important;
    word-break: break-word !important;
    color: #153244 !important;
}

pre {
    background-color: #F8FAFC !important;
    border: 1px solid rgba(
        126,203,226,0.25
    ) !important;
    border-radius: 12px !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# 3. MODELOS DE INTELIGENCIA ARTIFICIAL
# ──────────────────────────────────────────────────────────────

# Modelos preferidos.
# Se muestran únicamente si están en el catálogo
# de Groq asociado a la API Key.

MODELOS_PREFERIDOS = {
    "⚡ Rápido (GPT OSS 20B)": "openai/gpt-oss-20b",
    "🧠 Potente (GPT OSS 120B)": "openai/gpt-oss-120b",
    "🚀 Avanzado (Qwen 3 32B)": "qwen/qwen3-32b",
}

INFO_MODELOS = {
    "⚡ Rápido (GPT OSS 20B)": (
        "Modelo ágil para consultas cotidianas, "
        "preguntas frecuentes y explicaciones sencillas."
    ),
    "🧠 Potente (GPT OSS 120B)": (
        "Modelo de mayor capacidad, recomendado "
        "para explicaciones detalladas, análisis "
        "y resolución de problemas complejos."
    ),
    "🚀 Avanzado (Qwen 3 32B)": (
        "Modelo alternativo orientado al razonamiento, "
        "programación y resolución de problemas."
    ),
}


# ──────────────────────────────────────────────────────────────
# 4. CONEXIÓN CON GROQ
# ──────────────────────────────────────────────────────────────

def obtener_cliente_groq():

    api_key = st.secrets.get("clave_api")

    if not api_key:
        st.error(
            "⚠️ No se encontró la API Key de Groq. "
            "Verificá los secretos de Streamlit."
        )
        st.stop()

    return Groq(api_key=api_key)


@st.cache_data(ttl=300, show_spinner=False)
def consultar_modelos_disponibles(api_key):

    cliente = Groq(api_key=api_key)

    respuesta = cliente.models.list()

    return sorted(
        modelo.id
        for modelo in respuesta.data
        if getattr(modelo, "active", True)
    )


def construir_selector_modelos(disponibles):

    modelos = {}

    # Incorporar modelos preferidos disponibles.

    for nombre, identificador in MODELOS_PREFERIDOS.items():

        if identificador in disponibles:
            modelos[nombre] = identificador

    # Completar hasta tres opciones si es necesario.

    if len(modelos) < 3:

        usados = set(modelos.values())

        alternativas = [
            identificador
            for identificador in disponibles
            if identificador not in usados
            and not identificador.startswith("whisper")
            and not identificador.startswith("distil-whisper")
            and not identificador.startswith("playai")
            and not identificador.startswith("canopylabs")
            and "guard" not in identificador.lower()
            and "tts" not in identificador.lower()
            and "transcription" not in identificador.lower()
            and "compound" not in identificador.lower()
        ]

        for identificador in alternativas:

            if len(modelos) >= 3:
                break

            nombre = f"🤖 Alternativo ({identificador})"

            modelos[nombre] = identificador

    return modelos


# ──────────────────────────────────────────────────────────────
# 5. ESTADO DE LA APLICACIÓN
# ──────────────────────────────────────────────────────────────

def inicializar_session_state():

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    if "modelo_actual" not in st.session_state:
        st.session_state.modelo_actual = None


# ──────────────────────────────────────────────────────────────
# 6. PERSONALIDAD DEL ASISTENTE
# ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
Sos IA para Todos, un asistente virtual educativo
diseñado para acompañar a personas que están
aprendiendo inteligencia artificial.

Tu tono es amable, paciente, motivador y claro.

Tu público está formado por personas principiantes
que desean aprender a utilizar herramientas de IA.

Tus objetivos son:

1. Ayudar al estudiante a redactar mejores prompts.
   Fórmula: Contexto + Tarea + Detalle.

2. Recordar la importancia de verificar información.
   Regla de oro: Confiar pero verificar.

3. Ayudar a proteger datos personales y sensibles.
   Nunca solicitar DNI, contraseñas, tarjetas
   bancarias ni información privada innecesaria.

4. Explicar conceptos de forma sencilla y práctica.

5. Utilizar ejemplos cotidianos cuando sea posible.

6. Fomentar el pensamiento crítico y la autonomía.

7. Evitar explicaciones técnicas complejas,
   salvo que el usuario las solicite expresamente.

8. Si no sabés una respuesta, reconocelo.

9. No inventes información ni fuentes.

10. Respondé en español claro, preferentemente
    utilizando expresiones habituales de Argentina.

IDENTIDAD DEL ASISTENTE:

Tu nombre es IA para Todos.

Funcionás mediante modelos de inteligencia
artificial accesibles a través de Groq.

No afirmes que sos ChatGPT, GPT-4 u otro modelo
si esa información no corresponde al modelo activo.

Cuando te pregunten qué modelo sos,
indicá el identificador del modelo activo
proporcionado en estas instrucciones.

No inventes versiones ni características técnicas.

Tu propósito es acompañar el aprendizaje,
no reemplazar el pensamiento del estudiante.
"""


# ──────────────────────────────────────────────────────────────
# 7. GENERACIÓN DE RESPUESTAS
# ──────────────────────────────────────────────────────────────

def generar_stream(cliente, modelo, mensajes):

    try:

        prompt_modelo = (
            SYSTEM_PROMPT
            + "\n\nMODELO ACTIVO: "
            + modelo
            + "\nSi preguntan qué modelo utilizás, "
            + "respondé con este identificador exacto."
        )

        stream = cliente.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": prompt_modelo
                }
            ] + mensajes,
            temperature=0.6,
            max_tokens=1024,
            stream=True
        )

        for chunk in stream:

            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content

    except Exception as e:

        mensaje_error = str(e)

        if (
            "model_not_found" in mensaje_error
            or "does not exist" in mensaje_error
        ):
            raise RuntimeError(
                "El modelo seleccionado no está disponible. "
                "Elegí otro modelo desde la barra lateral."
            ) from e

        if "429" in mensaje_error:
            raise RuntimeError(
                "Se alcanzó temporalmente el límite "
                "de solicitudes. Intentá nuevamente."
            ) from e

        if "401" in mensaje_error:
            raise RuntimeError(
                "No se pudo autenticar la API Key de Groq."
            ) from e

        raise RuntimeError(
            "No se pudo completar la respuesta. "
            "Intentá nuevamente."
        ) from e


# ──────────────────────────────────────────────────────────────
# 8. BARRA LATERAL
# ──────────────────────────────────────────────────────────────

def render_sidebar(modelos):

    with st.sidebar:

        col1, col2 = st.columns([1, 3])

        with col1:
            st.image("logo.png", width=60)

        with col2:
            st.markdown("### IA para Todos")
            st.caption(
                "Tu asistente virtual de aprendizaje"
            )

        # Selector de modelos

        opcion_modelo = st.selectbox(
            "Elegí tu modelo:",
            options=list(modelos.keys()),
            index=0,
            help=(
                "Seleccioná el modelo de inteligencia "
                "artificial que querés utilizar."
            )
        )

        st.session_state.modelo_actual = modelos[
            opcion_modelo
        ]

        descripcion = INFO_MODELOS.get(
            opcion_modelo,
            "Elegí el modelo que mejor se adapte "
            "a tu consulta."
        )

        st.info(
            descripcion,
            icon="ℹ️"
        )

        st.write("")

        # Botón nuevo chat

        if st.button(
            "✨ Nuevo Chat (Limpiar Pantalla)",
            type="primary",
            use_container_width=True
        ):
            st.session_state.mensajes = []
            st.rerun()

        st.divider()

        # ──────────────────────────────────────
        # MÓDULO 1
        # ──────────────────────────────────────

        st.subheader("📚 Práctica por módulo")

        with st.expander(
            "🧠 Módulo 1: Primer acercamiento a la IA"
        ):

            st.markdown("""
**Practicá tus primeros pasos con IA:**

Explorá qué es, para qué sirve y cómo hacer
una primera interacción simple.
""")

            st.caption("Ejemplo 1")

            st.code(
                "Explicame qué es la inteligencia "
                "artificial con ejemplos de la vida cotidiana.",
                language="text"
            )

            st.caption("Ejemplo 2")

            st.code(
                "Soy principiante. Decime paso a paso "
                "cómo usar un chat de inteligencia "
                "artificial por primera vez.",
                language="text"
            )

            st.caption("Ejemplo 3")

            st.code(
                "Quiero organizar mejor mi semana. "
                "Haceme 3 preguntas para ayudarme "
                "a pedirte mejor lo que necesito.",
                language="text"
            )

        # ──────────────────────────────────────
        # MÓDULO 2
        # ──────────────────────────────────────

        with st.expander(
            "✍️ Módulo 2: Formular pedidos claros"
        ):

            st.markdown("""
**Aprendé a pedir mejor:**

Usá contexto, intención y detalle para
obtener respuestas más útiles.
""")

            st.caption("Ejemplo 1")

            st.code(
                "Actuá como un organizador personal "
                "y armame una lista de compras para "
                "4 días con comidas simples y económicas.",
                language="text"
            )

            st.caption("Ejemplo 2")

            st.code(
                "Reescribí este mensaje para que "
                "sea más amable y claro: "
                "'No voy a poder ir, avisá al resto'.",
                language="text"
            )

            st.caption("Ejemplo 3")

            st.code(
                "Explicame paso a paso cómo hacer "
                "una receta fácil con arroz, "
                "huevo y tomate.",
                language="text"
            )

        # ──────────────────────────────────────
        # MÓDULO 3
        # ──────────────────────────────────────

        with st.expander(
            "🎨 Módulo 3: Creatividad y entretenimiento"
        ):

            st.markdown("""
**Usá la IA para crear, imaginar y jugar:**

Probá recomendaciones, ideas y
actividades recreativas.
""")

            st.caption("Ejemplo 1")

            st.code(
                "Recomendame una película, un libro "
                "y una actividad cultural según estos "
                "gustos: me gusta el suspenso y "
                "las historias reales.",
                language="text"
            )

            st.caption("Ejemplo 2")

            st.code(
                "Creame una invitación para un "
                "cumpleaños con tono alegre, "
                "simple y cercano.",
                language="text"
            )

            st.caption("Ejemplo 3")

            st.code(
                "Hagamos una trivia de 5 preguntas "
                "fáciles sobre historia argentina.",
                language="text"
            )

        # ──────────────────────────────────────
        # MÓDULO 4
        # ──────────────────────────────────────

        with st.expander(
            "🛡️ Módulo 4: Seguridad y 'No creas todo'"
        ):

            st.markdown("""
**Aprendé a usar IA con criterio y seguridad:**

Verificá información, detectá errores
y cuidá tus datos personales.
""")

            st.caption("Ejemplo 1")

            st.code(
                "¿Qué señales debo mirar para "
                "detectar si un mensaje puede "
                "ser una estafa?",
                language="text"
            )

            st.caption("Ejemplo 2")

            st.code(
                "Quiero pedir ayuda para analizar "
                "mis gastos, pero sin compartir "
                "datos sensibles. ¿Cómo puedo "
                "hacerlo de forma segura?",
                language="text"
            )

            st.caption("Ejemplo 3")

            st.code(
                "Dame una checklist simple para "
                "verificar si una respuesta de IA "
                "puede estar equivocada.",
                language="text"
            )


# ──────────────────────────────────────────────────────────────
# 9. PANTALLA DE BIENVENIDA
# ──────────────────────────────────────────────────────────────

def render_bienvenida():

    st.title(
        "👋 Hola, estoy para ayudarte a aprender con IA"
    )

    st.caption(
        "Practicá, explorá y resolvé dudas "
        "en cualquier momento"
    )

    col1, col2 = st.columns(
        [1, 1],
        gap="medium"
    )

    with col1:

        st.markdown("""
Este espacio está pensado para que practiques
con inteligencia artificial mientras avanzás
en la cursada.

Tené en cuenta estos **3 principios clave**:

1. **Pedí mejor:** sumá contexto, ejemplos y
   detalles para obtener mejores respuestas.

2. **Verificá:** la IA puede equivocarse.
   Contrastá la información.

3. **Cuidá tus datos:** no compartas
   información personal o sensible.
""")

        st.markdown("""
<div style="
    background-color:#F4F1FA;
    border:1px solid rgba(184,177,216,0.45);
    border-radius:12px;
    padding:14px 16px;
    margin-top:6px;
    color:#153244;
    font-size:15px;
    line-height:1.5;
">
    👉 <b>No hay respuestas correctas
    o incorrectas.</b>
    <p>Es un espacio para aprender haciendo.</p>
</div>
""", unsafe_allow_html=True)

    st.divider()


# ──────────────────────────────────────────────────────────────
# 10. ÁREA PRINCIPAL DEL CHAT
# ──────────────────────────────────────────────────────────────

def main():

    inicializar_session_state()

    cliente = obtener_cliente_groq()

    # Consultar modelos disponibles

    try:

        api_key = st.secrets["clave_api"]

        disponibles = consultar_modelos_disponibles(
            api_key
        )

    except Exception:

        st.error(
            "❌ No fue posible conectar con Groq. "
            "Verificá la API Key y los permisos "
            "de tu cuenta."
        )

        st.stop()

    # Preparar modelos

    modelos = construir_selector_modelos(
        disponibles
    )

    if not modelos:

        st.error(
            "❌ No se encontraron modelos de chat "
            "entre las opciones disponibles."
        )

        st.stop()

    # Mostrar barra lateral

    render_sidebar(modelos)

    # Pantalla inicial

    if not st.session_state.mensajes:
        render_bienvenida()

    # Historial de conversación

    for mensaje in st.session_state.mensajes:

        with st.chat_message(
            mensaje["role"],
            avatar=(
                "👤"
                if mensaje["role"] == "user"
                else "🤖"
            )
        ):

            st.markdown(
                mensaje["content"]
            )

    # Entrada de usuario

    prompt = st.chat_input(
        "Escribí tu consulta aquí..."
    )

    if prompt:

        st.session_state.mensajes.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message(
            "user",
            avatar="👤"
        ):
            st.markdown(prompt)

        # Respuesta de la IA

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            try:

                respuesta_completa = st.write_stream(
                    generar_stream(
                        cliente,
                        st.session_state.modelo_actual,
                        st.session_state.mensajes
                    )
                )

                if respuesta_completa:

                    st.session_state.mensajes.append({
                        "role": "assistant",
                        "content": respuesta_completa
                    })

            except Exception as e:

                st.error(str(e))

                st.info(
                    "Probá seleccionar otro modelo "
                    "desde la barra lateral."
                )


# ──────────────────────────────────────────────────────────────
# 11. EJECUCIÓN
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()


