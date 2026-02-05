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
    /* Estilos globales de texto */
    h1, h2, h3, p, li { color: #153244; }

    /* Estilo del INPUT del chat */
    .stChatInput textarea {
        background-color: #ffffff !important;
        color: #153244 !important;
        border: 2px solid #34b3a0 !important;
        border-radius: 12px !important;
    }
    
    /* SOLUCIÓN AL PROBLEMA DE COLORES EN CLOUD:
       Usamos 'div[data-testid="stChatMessage"]' para ser muy específicos.
       Usamos '!important' para obligar a Streamlit a respetar el color.
       Usamos 'nth-of-type' en lugar de 'nth-child' para ignorar elementos ocultos.
    */

    /* USUARIO (Siempre es el 1º, 3º, 5º... mensaje de tipo chat) -> VERDE */
    div[data-testid="stChatMessage"]:nth-of-type(odd) {
        background-color: #e8fdfa !important;
        border: 1px solid #d0f0ed !important;
    }

    /* IA (Siempre es el 2º, 4º, 6º... mensaje de tipo chat) -> GRIS/BLANCO */
    div[data-testid="stChatMessage"]:nth-of-type(even) {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
    }

    /* Color del Avatar (Iconos) */
    .stChatMessage .stChatMessageAvatar {
        background-color: #153244 !important;
        color: white !important;
    }
    
    /* Ajuste de texto en código */
    code {
        white-space: pre-wrap !important;
        word-break: break-word !important;
    }

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
        st.title("🤖 IA para Todos")
        st.caption("Tu Copiloto de aprendizaje")
        
        st.divider()
        
        st.markdown("**⚙️ Configuración del 'Cerebro'**")
        
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
        st.subheader("📚 Ejercicios por Módulo")
        
        with st.expander("📝 Módulo 2: Redacción"):
            st.markdown("Probá la fórmula **Contexto + Tarea + Detalle**:")
            
            st.caption("Ejemplo: Salud y Bienestar")
            st.code("Actúa como un nutricionista experto (Contexto). Creame un menú semanal de cenas ligeras (Tarea) que incluyan verduras y sean fáciles de cocinar (Detalle).", language="text")
            
            st.caption("Ejemplo: Historia para nietos")
            st.code("Soy abuela y quiero explicarle a mi nieto de 8 años qué fue la Revolución de Mayo. Explicámelo como si fuera un cuento breve y entretenido.", language="text")

        with st.expander("🎨 Módulo 3: Creatividad"):
            st.markdown("Ideas frescas para jugar y crear:")
            
            st.caption("Ejemplo: Decoración")
            st.code("Tengo un living pequeño con poca luz. Dame 5 ideas de decoración estilo nórdico para que parezca más grande.", language="text")
            
            st.caption("Ejemplo: Juego Mental")
            st.code("Vamos a jugar a 'Adivina el Personaje'. Vos pensá en un personaje histórico y yo te hago preguntas de 'Sí o No'.", language="text")
        
        with st.expander("🛡️ Módulo 4: Seguridad"):
            st.markdown("Detectando trampas y cuidando datos:")
            
            st.caption("Ejemplo: Detectar Estafas")
            st.code("Me llegó un mail diciendo que gané un iPhone y que pague el envío con mi tarjeta. ¿Qué señales debo mirar para saber si es una estafa?", language="text")
            
            st.caption("Ejemplo: Cuidar privacidad")
            st.code("Quiero analizar mis gastos de tarjeta, pero no quiero darte mis datos reales. ¿Cómo puedo pasarte la información de forma segura?", language="text")

# ──────────────────────────────────────────────────────────────────────────────
# 4. INTERFAZ: ÁREA PRINCIPAL (CHAT)
# ──────────────────────────────────────────────────────────────────────────────
def main():
    inicializar_session_state()
    cliente = obtener_cliente_groq()
    render_sidebar()

    # PANTALLA DE BIENVENIDA (Cuando no hay mensajes)
    if not st.session_state.mensajes:
        st.title("¡Hola! Tu Copiloto está listo 👩‍✈️")
        st.markdown("""
        Bienvenida/o al chat de práctica. Recordá los **3 pilares** del curso:
        1.  **Pedir bien:** Usá contexto y detalles.
        2.  **Verificar:** La IA puede "alucinar".
        3.  **Cuidarte:** Nunca compartas claves, DNI ni datos bancarios.
        """)
        
        st.markdown("### ¿Por dónde empezamos hoy?")
        
        # Tarjetas de sugerencia rápida
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("🎂 **Creatividad**\n\n'Dame ideas originales para festejar un cumpleaños de 60...'")
        with c2:
            st.success("📝 **Resumen**\n\n'Te paso un texto largo y resumímelo en 3 puntos clave...'")
        with c3:
            st.warning("⚖️ **Criterio**\n\n'¿Es verdad que el sol gira alrededor de la tierra? Verificalo.'")

    # 1. MOSTRAR HISTORIAL DE CHAT
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"], avatar="👤" if mensaje["role"] == "user" else "🤖"):
            st.markdown(mensaje["content"])

    # 2. CAMPO DE TEXTO (INPUT)
    if prompt := st.chat_input("Escribí tu consulta aquí..."):
        # Guardar mensaje usuario
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Generar respuesta IA
        with st.chat_message("assistant", avatar="🤖"):
            respuesta_completa = st.write_stream(
                generar_stream(cliente, st.session_state.modelo_actual, st.session_state.mensajes)
            )
        
        # Guardar respuesta IA
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_completa})

if __name__ == "__main__":
    main()


