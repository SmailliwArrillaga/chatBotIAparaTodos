import streamlit as st
from groq import Groq
import os

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
# ESTILOS CSS (DEFINITIVOS)
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
# CONSTANTES Y MAPEOS (CON NOMBRES TÉCNICOS VISIBLES)
# ──────────────────────────────────────────────────────────────────────────────
# La clave (izquierda) es lo que ve el alumno. El valor (derecha) es el ID técnico.
MODELOS = {
    "⚡ Rápido (Llama 3.1 8B Instant)": "llama-3.1-8b-instant",
    "🧠 Potente (Llama 3.3 70B Versatile)": "llama-3.3-70b-versatile",
    "✍️ Creativo (Gemma 2 9B IT)": "gemma2-9b-it",
}

# Descripciones explicativas (Deben coincidir exactamente con las claves de arriba)
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
        # Prompt del Sistema: Define la personalidad del Copiloto (Clara)
        system_prompt = """
        Sos el asistente oficial del curso 'IA para Todos'. 
        Tu tono es amable, paciente y motivador (estilo Clara, la mentora del curso).
        Tus objetivos son:
        1. Ayudar al alumno a redactar mejores prompts (Fórmula: Contexto + Tarea + Detalle).
        2. Recordarles siempre verificar la información (regla de oro: 'Confiar pero verificar').
        3. Ayudarles a proteger sus datos sensibles (nunca pedir DNI, claves o tarjetas).
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
        
        # 1. Selector de Modelo con Tooltip de ayuda (?)
        opcion_modelo = st.selectbox(
            "Elegí tu modelo:",
            list(MODELOS.keys()),
            index=0,
            help="Elegí la tecnología detrás del chat:\n\n⚡ Llama 3.1 8B: Rápido y ligero.\n🧠 Llama 3.3 70B: Muy inteligente y detallista.\n✍️ Gemma 2 9B: Creativo y bueno siguiendo instrucciones."
        )
        st.session_state.modelo_actual = MODELOS[opcion_modelo]
        
        # 2. Cajita de Información Dinámica
        st.info(INFO_MODELOS[opcion_modelo], icon="ℹ️")
        
        st.write("") # Espacio vacío

        # 3. Botón de Nuevo Chat (Destacado)
        if st.button("✨ Nuevo Chat (Limpiar Pantalla)", type="primary", use_container_width=True):
            st.session_state.mensajes = []
            st.rerun()

        st.divider()

        # 4. Biblioteca de Prompts (Ejemplos del Curso)
        st.subheader("📚Práctica por módulo")

        with st.expander("🧠 Módulo 1: Primer acercamiento a la IA"):
            st.markdown("""
            **Practicá tus primeros pasos con IA:**  
            Explorá qué es, para qué sirve y cómo hacer una primera interacción simple.
            """)
            st.caption("Ejemplo 1")
            st.code("Explicame qué es la inteligencia artificial con ejemplos de la vida cotidiana.", language="text")

            st.caption("Ejemplo 2")
            st.code("Soy principiante. Decime paso a paso cómo usar un chat de inteligencia artificial por primera vez.", language="text")

            st.caption("Ejemplo 3")
            st.code("Quiero organizar mejor mi semana. Haceme 3 preguntas para ayudarme a pedirte mejor lo que necesito.", language="text")

        with st.expander("✍️ Módulo 2: Formular pedidos claros"):
            st.markdown("""
            **Aprendé a pedir mejor:**  
            Usá contexto, intención y detalle para obtener respuestas más útiles.
            """)
            st.caption("Ejemplo 1")
            st.code("Actuá como un organizador personal y armame una lista de compras para 4 días con comidas simples y económicas.", language="text")

            st.caption("Ejemplo 2")
            st.code("Reescribí este mensaje para que sea más amable y claro: 'No voy a poder ir, avisá al resto'.", language="text")

            st.caption("Ejemplo 3")
            st.code("Explicame paso a paso cómo hacer una receta fácil con arroz, huevo y tomate.", language="text")

        with st.expander("🎨 Módulo 3: Creatividad y entretenimiento"):
            st.markdown("""
            **Usá la IA para crear, imaginar y jugar:**  
            Probá recomendaciones, imágenes, ideas y actividades recreativas.
            """)
            st.caption("Ejemplo 1")
            st.code("Recomendame una película, un libro y una actividad cultural según estos gustos: me gusta el suspenso y las historias reales.", language="text")

            st.caption("Ejemplo 2")
            st.code("Creame una invitación para un cumpleaños con tono alegre, simple y cercana.", language="text")

            st.caption("Ejemplo 3")
            st.code("Hagamos una trivia de 5 preguntas fáciles sobre historia argentina.", language="text")

        with st.expander("🛡️ Módulo 4: Seguridad y 'No creas todo'"):
            st.markdown("""
            **Aprendé a usar IA con criterio y seguridad:**  
            Verificá información, detectá errores y cuidá tus datos personales.
            """)
            st.caption("Ejemplo 1")
            st.code("¿Qué señales debo mirar para detectar si un mensaje puede ser una estafa?", language="text")

            st.caption("Ejemplo 2")
            st.code("Quiero pedir ayuda para analizar mis gastos, pero sin compartir datos sensibles. ¿Cómo puedo hacerlo de forma segura?", language="text")

            st.caption("Ejemplo 3")
            st.code("Dame una checklist simple para verificar si una respuesta de IA puede estar equivocada.", language="text")

# ──────────────────────────────────────────────────────────────────────────────
# 4. INTERFAZ: ÁREA PRINCIPAL (CHAT)
# ──────────────────────────────────────────────────────────────────────────────
def main():
    inicializar_session_state()
    cliente = obtener_cliente_groq()
    render_sidebar()

    # PANTALLA DE BIENVENIDA (cuando no hay mensajes)
    if not st.session_state.mensajes:
        st.title("👋 Hola, estoy para ayudarte a aprender con IA.
        Practicá, explorá y resolvé dudas en cualquier momento")
        st.markdown("""
        Este espacio está pensado para que practiques con inteligencia artificial mientras avanzás en la cursada.
        **Pedí mejor**: sumá contexto, ejemplos y detalles para obtener mejores respuestas.
        **Verificá**: la IA puede equivocarse. Contrastá la información.
        **Cuidá tus datos**: no compartas información personal o sensible.
        """)

        st.markdown("### 🚀 Empezá a practicar")

        with st.expander("👉 Ver actividades sugeridas para empezar", expanded=False):

            c1, c2 = st.columns(2)

            with c1:
                st.markdown("""
                **🧠 Entender la IA**  
                Primeros pasos para usar IA.
                """)

                st.markdown("""
                **🎨 Crear con IA**  
                Generá ideas y contenido.
                """)

            with c2:
                st.markdown("""
                **✍️ Pedir mejor**  
                Instrucciones claras y efectivas.
                """)

                st.markdown("""
                **🛡️ Usar IA con criterio**  
                Verificar y cuidar datos.
                """)

    # 1. MOSTRAR HISTORIAL DE CHAT
    for mensaje in st.session_state.mensajes:
        with st.chat_message(
            mensaje["role"],
            avatar="👤" if mensaje["role"] == "user" else "🤖"
        ):
            st.markdown(mensaje["content"])

    # 2. CAMPO DE TEXTO (INPUT)
    if prompt := st.chat_input("Escribí tu consulta aquí..."):
        # Guardar mensaje del usuario
        st.session_state.mensajes.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generar respuesta IA
        with st.chat_message("assistant", avatar="🤖"):
            respuesta_completa = st.write_stream(
                generar_stream(
                    cliente,
                    st.session_state.modelo_actual,
                    st.session_state.mensajes
                )
            )

        # Guardar respuesta IA
        st.session_state.mensajes.append(
            {"role": "assistant", "content": respuesta_completa}
        )


if __name__ == "__main__":
    main()
