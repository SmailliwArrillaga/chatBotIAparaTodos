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
# ESTILOS CSS (MEJORADO: AJUSTE DE TEXTO AUTOMÁTICO)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
    /* Estilos globales de texto */
    h1, h2, h3, p, li { color: #153244; }

    /* Input del chat */
    .stChatInput textarea {
        background-color: #ffffff !important;
        color: #153244 !important;
        border: 2px solid #34b3a0 !important;
        border-radius: 12px !important;
    }
    
    /* Burbujas de Chat: USUARIO (Verde muy suave) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #e8fdfa;
        border: 1px solid #d0f0ed;
    }

    /* Burbujas de Chat: IA (Gris muy suave) */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
    }

    /* Avatar */
    .stChatMessage .stChatMessageAvatar {
        background-color: #153244 !important;
        color: white !important;
    }
    
    /* SOLUCIÓN AL SCROLL: Esto obliga al código a bajar de línea */
    code {
        white-space: pre-wrap !important;
        word-break: break-word !important;
    }

    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Mapeo de Modelos
MODELOS = {
    "⚡ Rápido (Consultas cortas)": "llama-3.1-8b-instant",
    "🧠 Potente (Redacción y Análisis)": "llama-3.3-70b-versatile",
    "✍️ Creativo (Ideas y Juegos)": "gemma2-9b-it",
}

# ──────────────────────────────────────────────────────────────────────────────
# 2. FUNCIONES DE LÓGICA
# ──────────────────────────────────────────────────────────────────────────────
def obtener_cliente_groq():
    api_key = st.secrets.get("clave_api")
    if not api_key:
        st.error("⚠️ Falta configurar la API Key.")
        st.stop()
    return Groq(api_key=api_key)

def inicializar_session_state():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
    if "modelo_actual" not in st.session_state:
        st.session_state.modelo_actual = list(MODELOS.values())[0]

def generar_stream(cliente, modelo, mensajes):
    """Generador de respuesta con personalidad de Tutor del curso."""
    try:
        # Prompt del Sistema: Define la personalidad del Copiloto
        system_prompt = """
        Sos el asistente oficial del curso 'IA para Todos'. 
        Tu tono es amable, paciente y motivador (estilo Clara, la mentora del curso).
        Tus objetivos son:
        1. Ayudar al alumno a redactar mejores prompts (Fórmula: Contexto + Tarea + Detalle).
        2. Recordarles siempre verificar la información (regla de oro: 'Confiar pero verificar').
        3. Ayudarles a proteger sus datos sensibles (nunca pedir DNI ni claves).
        No des respuestas técnicas de programación salvo que te lo pidan explícitamente.
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
# 3. INTERFAZ: SIDEBAR (BIBLIOTECA DEL CURSO - NUEVOS EJEMPLOS)
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Título y Logo
        st.title("🤖 IA para Todos")
        st.caption("Tu Copiloto de aprendizaje")
        
        st.divider()
        
        # Selector de Modelo
        st.markdown("**⚙️ Configuración**")
        opcion_modelo = st.selectbox(
            "Elegí tu modelo:",
            list(MODELOS.keys()),
            index=0
        )
        st.session_state.modelo_actual = MODELOS[opcion_modelo]
        
        # Botón Limpiar
        if st.button("🗑️ Borrar Historial", use_container_width=True):
            st.session_state.mensajes = []
            st.rerun()

        st.divider()

        # BIBLIOTECA DE PROMPTS (Ejemplos 100% Nuevos y sin scroll horizontal)
        st.subheader("📚 Ejercicios por Módulo")
        
        with st.expander("📝 Módulo 2: Redacción"):
            st.markdown("Probá la fórmula **Contexto + Tarea + Detalle** con estos casos nuevos:")
            
            st.caption("Ejemplo: Salud y Bienestar")
            st.code("Actúa como un nutricionista experto (Contexto). Creame un menú semanal de cenas ligeras (Tarea) que incluyan verduras y sean fáciles de cocinar en 15 minutos (Detalle).", language="text")
            
            st.caption("Ejemplo: Historia para nietos")
            st.code("Soy abuela y quiero explicarle a mi nieto de 8 años qué fue la Revolución de Mayo. Explicámelo como si fuera un cuento breve y entretenido.", language="text")

        with st.expander("🎨 Módulo 3: Creatividad"):
            st.markdown("Ideas frescas para jugar y crear:")
            
            st.caption("Ejemplo: Decoración")
            st.code("Tengo un living pequeño con poca luz. Dame 5 ideas de decoración estilo nórdico para que parezca más grande y luminoso.", language="text")
            
            st.caption("Ejemplo: Juego Mental")
            st.code("Vamos a jugar a 'Adivina el Personaje'. Vos pensá en un personaje histórico famoso y yo te hago preguntas de 'Sí o No' para adivinarlo. ¡No me digas quién es!", language="text")
        
        with st.expander("🛡️ Módulo 4: Seguridad"):
            st.markdown("Detectando trampas y cuidando datos:")
            
            st.caption("Ejemplo: Detectar Estafas")
            st.code("Me llegó un mail diciendo que gané un iPhone y que pague el envío con mi tarjeta. ¿Qué señales debo mirar para saber si es una estafa (Phishing)?", language="text")
            
            st.caption("Ejemplo: Cuidar privacidad")
            st.code("Quiero analizar mis gastos de tarjeta, pero no quiero darte mis datos reales. ¿Cómo puedo pasarte la información de forma segura usando la 'Bolsa Verde'?", language="text")

# ──────────────────────────────────────────────────────────────────────────────
# 4. INTERFAZ: ÁREA PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────
def main():
    inicializar_session_state()
    cliente = obtener_cliente_groq()
    render_sidebar()

    # ESTADO VACÍO (Bienvenida del Curso)
    if not st.session_state.mensajes:
        st.title("¡Hola! Tu Copiloto está listo 👩‍✈️")
        st.markdown("""
        Bienvenida/o al chat de práctica. Recordá los **3 pilares** que vimos:
        1.  **Pedir bien:** Usá contexto y detalles.
        2.  **Verificar:** La IA puede "alucinar".
        3.  **Cuidarte:** Nunca compartas claves ni DNI.
        """)
        
        st.markdown("### ¿Por dónde empezamos?")
        
        # Tarjetas de acción rápida (Nuevas)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("🎂 **Creatividad**\n\n'Dame ideas originales para festejar un cumpleaños de 60...'")
        with c2:
            st.success("📝 **Resumen**\n\n'Te paso un texto largo y resumímelo en 3 puntos clave...'")
        with c3:
            st.warning("⚖️ **Criterio**\n\n'¿Es verdad que el sol gira alrededor de la tierra? Verificalo.'")

    # 1. Mostrar historial
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"], avatar="👤" if mensaje["role"] == "user" else "🤖"):
            st.markdown(mensaje["content"])

    # 2. Input del usuario
    if prompt := st.chat_input("Escribí tu consulta aquí..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # 3. Respuesta de la IA
        with st.chat_message("assistant", avatar="🤖"):
            respuesta_completa = st.write_stream(
                generar_stream(cliente, st.session_state.modelo_actual, st.session_state.mensajes)
            )
        
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_completa})

if __name__ == "__main__":
    main()