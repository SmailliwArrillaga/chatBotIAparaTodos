import streamlit as st
from groq import Groq

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Asistente - IA para Todos",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────────────────────
# ESTILOS CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
    /* Texto general */
    h1, h2, h3, h4, p, li, label, div {
        color: #153244;
    }

    /* Fondo principal */
    .stApp {
        background: linear-gradient(135deg, rgba(255,255,255,1) 40%, rgba(184,177,216,0.18) 100%);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(184,177,216,0.18) 100%);
        border-right: 1px solid rgba(21, 50, 68, 0.08);
    }

    /* Input del chat */
    .stChatInput textarea {
        background-color: #ffffff !important;
        color: #153244 !important;
        border: 2px solid #7ECBE2 !important;
        border-radius: 14px !important;
    }

    .stChatInput textarea:focus {
        border: 2px solid #B8B1D8 !important;
        box-shadow: 0 0 0 0.2rem rgba(126, 203, 226, 0.20) !important;
    }

    /* Burbujas del usuario */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #EEF9FC;
        border: 1px solid rgba(126, 203, 226, 0.35);
        border-radius: 16px;
    }

    /* Burbujas de la IA */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #F4F1FA;
        border: 1px solid rgba(184, 177, 216, 0.45);
        border-radius: 16px;
    }

    /* Avatar */
    .stChatMessage .stChatMessageAvatar {
        background-color: #153244 !important;
        color: white !important;
    }

    /* Botones */
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

    /* Selectbox */
    div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border: 1px solid rgba(21, 50, 68, 0.15) !important;
    }

    /* Caja info */
    [data-testid="stAlert"] {
        border-radius: 14px !important;
    }

    /* Bloques de código */
    code {
        white-space: pre-wrap !important;
        word-break: break-word !important;
        color: #153244 !important;
    }

    pre {
        background-color: #F8FAFC !important;
        border: 1px solid rgba(126, 203, 226, 0.25) !important;
        border-radius: 12px !important;
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTES Y MAPEOS
# ──────────────────────────────────────────────────────────────────────────────
MODELOS = {
    "⚡ Rápido (Llama 3.1 8B Instant)": "llama-3.1-8b-instant",
    "🧠 Potente (Llama 3.3 70B Versatile)": "llama-3.3-70b-versatile",
    "✍️ Creativo (Gemma 2 9B IT)": "gemma2-9b-it",
}

INFO_MODELOS = {
    "⚡ Rápido (Llama 3.1 8B Instant)": "Modelo ligero y veloz de Meta. Ideal para saludos, definiciones simples o cuando necesitás una respuesta inmediata.",
    "🧠 Potente (Llama 3.3 70B Versatile)": "Modelo avanzado de gran capacidad. Usalo para razonamiento complejo, redacción detallada, seguridad o análisis de textos.",
    "✍️ Creativo (Gemma 2 9B IT)": "Modelo de Google optimizado para instrucciones. Suele tener un tono más imaginativo, ideal para lluvias de ideas o juegos."
}

# ──────────────────────────────────────────────────────────────────────────────
# 2. FUNCIONES DE LÓGICA
# ──────────────────────────────────────────────────────────────────────────────
def obtener_cliente_groq():
    """Obtiene la API Key de los secretos de Streamlit."""
    api_key = st.secrets.get("clave_api")
    if not api_key:
        st.error("⚠️ Error: No se encontró la API Key. Configura .streamlit/secrets.toml")
        st.stop()
    return Groq(api_key=api_key)

def inicializar_session_state():
    """Inicializa variables de estado si no existen."""
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    if "modelo_actual" not in st.session_state:
        st.session_state.modelo_actual = list(MODELOS.values())[0]

def generar_stream(cliente, modelo, mensajes):
    """Generador de respuesta con la personalidad del Tutor del Curso."""
    try:
        system_prompt = """
        Sos el asistente oficial del curso 'IA para Todos'.
        Tu tono es amable, paciente y motivador.
        Tus objetivos son:
        1. Ayudar al alumno a redactar mejores prompts (Fórmula: Contexto + Tarea + Detalle).
        2. Recordar siempre verificar la información (regla de oro: 'Confiar pero verificar').
        3. Ayudar a proteger datos sensibles (nunca pedir DNI, claves o tarjetas).
        No des respuestas técnicas de programación compleja salvo que te lo pidan explícitamente.
        """

        stream = cliente.chat.completions.create(
            model=modelo,
            messages=[{"role": "system", "content": system_prompt}] + mensajes,
            temperature=0.6,
            max_tokens=1024,
            stream=True
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        yield f"❌ Ups, hubo un error de conexión: {str(e)}"

# ──────────────────────────────────────────────────────────────────────────────
# 3. INTERFAZ: BARRA LATERAL (SIDEBAR)
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image("logo.png", width=60)

        with col2:
            st.markdown("### IA para Todos")
            st.caption("Tu asistente virtual de aprendizaje")

        opcion_modelo = st.selectbox(
            "Elegí tu modelo:",
            list(MODELOS.keys()),
            index=0,
            help="Elegí la tecnología detrás del chat:\n\n⚡ Llama 3.1 8B: Rápido.\n🧠 Llama 3.3 70B: Inteligente.\n✍️ Gemma 2 9B: Creativo."
        )
        st.session_state.modelo_actual = MODELOS[opcion_modelo]
        st.info(INFO_MODELOS[opcion_modelo], icon="ℹ️")

        if st.button("✨ Nuevo Chat (Limpiar Pantalla)", type="primary", use_container_width=True):
            st.session_state.mensajes = []
            st.rerun()

        st.divider()
        st.subheader("📚 Práctica por módulo")

        with st.expander("🧠 Módulo 1"):
            st.caption("Ejemplo:")
            st.code("Explicame qué es la IA con ejemplos cotidianos.", language="text")

        with st.expander("✍️ Módulo 2"):
            st.caption("Ejemplo:")
            st.code("Actuá como un organizador y armame una lista de compras.", language="text")

        with st.expander("🎨 Módulo 3"):
            st.caption("Ejemplo:")
            st.code("Hagamos una trivia de 5 preguntas sobre historia.", language="text")

        with st.expander("🛡️ Módulo 4"):
            st.caption("Ejemplo:")
            st.code("¿Cómo detectar si un mensaje es una estafa?", language="text")

# ──────────────────────────────────────────────────────────────────────────────
# 4. INTERFAZ: ÁREA PRINCIPAL (CHAT)
# ──────────────────────────────────────────────────────────────────────────────
def main():
    inicializar_session_state()
    cliente = obtener_cliente_groq()
    render_sidebar()

    # --- CABECERA COMPACTA EN COLUMNAS ---
    if not st.session_state.mensajes:
        st.title("👋 Hola, aprendamos juntos con IA")
        
        col_main_1, col_main_2 = st.columns([1.2, 1], gap="medium")

        with col_main_1:
            st.markdown("""
            **Principios clave para tu cursada:**
            * **Pedí mejor:** Sumá contexto y detalles.
            * **Verificá:** La IA puede equivocarse.
            * **Cuidá tus datos:** No compartas info sensible.
            """)

        with col_main_2:
            st.markdown("""
            <div style="background-color:#F4F1FA; border:1px solid rgba(184, 177, 216, 0.45); border-radius:12px; padding:12px; color:#153244; font-size:14px; line-height:1.4;">
                🚀 <b>Espacio de práctica</b><br>
                Podés hacer preguntas, probar ideas o resolver actividades. No hay respuestas incorrectas.
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("💡 Ver sugerencias de actividades", expanded=False):
            st.info("Explorá los ejemplos en la barra lateral 👈 para saber cómo empezar cada módulo.")

        st.divider()

    # --- ÁREA DE CHAT ---
    for mensaje in st.session_state.mensajes:
        with st.chat_message(
            mensaje["role"],
            avatar="👤" if mensaje["role"] == "user" else "🤖"
        ):
            st.markdown(mensaje["content"])

    if prompt := st.chat_input("Escribí tu consulta aquí..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            respuesta_completa = st.write_stream(
                generar_stream(
                    cliente,
                    st.session_state.modelo_actual,
                    st.session_state.mensajes
                )
            )

        st.session_state.mensajes.append(
            {"role": "assistant", "content": respuesta_completa}
        )

if __name__ == "__main__":
    main()
