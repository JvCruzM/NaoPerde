import uuid
import streamlit as st

from src.agent import NaoperdeAgent

st.set_page_config(
    page_title="NãoPerde | Seu assistente contra o desperdício",
    page_icon="🍲",
    layout="wide"
)


if "agent" not in st.session_state:
    st.session_state.agent = NaoperdeAgent()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


st.markdown("""
<style>

.stApp {
    background: #F8F9FA;
    color: #263445;
}

.main .block-container {
    max-width: 1100px;
    padding-top: 2.5rem;
    padding-bottom: 7rem;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E3D2F 0%, #11261D 100%);
}

[data-testid="stSidebar"] * {
    color: #FFFFFF;
}

.sidebar-logo {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 0;
}

.sidebar-subtitle {
    color: #A3C9B8 !important;
    font-size: 14px;
    margin-top: -8px;
}

.sidebar-section {
    color: #8EBDA5 !important;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 15px;
}

.main-title {
    color: #1E3D2F !important;
    font-size: 38px;
    font-weight: 800;
    letter-spacing: -1.5px;
    margin-bottom: 4px;
}

.main-subtitle {
    color: #64748B !important;
    font-size: 16px;
    margin-bottom: 25px;
}

.welcome-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #EBF4F0 100%);
    border: 1px solid #D1E5DC;
    border-radius: 20px;
    padding: 38px 25px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(30, 61, 47, 0.05);
    margin-top: 15px;
    margin-bottom: 30px;
}

.welcome-icon {
    font-size: 48px;
    margin-bottom: 10px;
}

.welcome-title {
    color: #1E3D2F !important;
    font-size: 27px;
    font-weight: 800;
    margin-bottom: 8px;
}

.welcome-description {
    color: #64748B !important;
    font-size: 15px;
    margin-bottom: 15px;
}

.welcome-highlight {
    color: #2D6A4F !important;
    font-size: 15px;
    font-weight: 700;
}

.suggestion-title {
    color: #1E3D2F !important;
    font-size: 19px;
    font-weight: 750;
    margin-bottom: 12px;
}

.stButton > button {
    background: #FFFFFF;
    color: #2D6A4F !important;
    border: 1px solid #D1E5DC;
    border-radius: 13px;
    padding: 12px 10px;
    min-height: 48px;
    font-weight: 700;
    transition: all 0.2s ease;
    box-shadow: 0 2px 7px rgba(30, 61, 47, 0.04);
}

.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #2D6A4F !important;
    font-weight: 700;
}

.stButton > button:hover {
    background: #E8F5E9;
    border-color: #2D6A4F;
    transform: translateY(-2px);
}

.stButton > button:active {
    background: #C8E6C9;
}

[data-testid="stSidebar"] .stButton > button {
    background: #2D6A4F;
    border: 1px solid #40916C;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #40916C;
    border-color: #52B788;
}

[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 12px;
    box-shadow: 0 3px 10px rgba(30, 61, 47, 0.035);
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: #263445;
    line-height: 1.7;
}

[data-testid="stChatInput"] {
    border-color: #D1E5DC;
}

[data-testid="stChatInput"] textarea {
    color: #263445 !important;
    background: #FFFFFF !important;
    caret-color: #2D6A4F;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #94A3B8 !important;
    opacity: 1;
}

[data-testid="stSpinner"] p {
    color: #2D6A4F !important;
    font-weight: 600;
}

hr {
    border-color: rgba(255, 255, 255, 0.15);
}

@media (max-width: 768px) {
    .main .block-container {
        padding-top: 1.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .main-title {
        font-size: 29px;
    }

    .welcome-card {
        padding: 25px 15px;
    }

    .welcome-title {
        font-size: 22px;
    }
}

</style>
""", unsafe_allow_html=True)


with st.sidebar:

    st.markdown(
        '<div class="sidebar-logo">🍲 NãoPerde</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">Seu assistente contra o desperdício</div>',
        unsafe_allow_html=True
    )

    st.divider()

    if st.button("＋  Nova conversa", use_container_width=True):

        st.session_state.agent.clear_conversation(
            st.session_state.session_id
        )

        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())

        st.rerun()

    st.markdown(
        '<div class="sidebar-section">Sua cozinha inteligente</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Reduza desperdícios, aproveite ingredientes e crie refeições deliciosas."
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-section">O que você pode fazer</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    🥦  Aproveitar sobras de alimentos

    📋  Organizar a geladeira e despensa

    🍳  Criar receitas com o que tem em casa

    💡  Dicas de conservação e armazenamento
    """)

    st.divider()

    st.caption("NÃOPERDE • PROJETO DE SUSTENTABILIDADE")


st.markdown(
    '<div class="main-title">Olá! O que tem na geladeira? 🥗</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Evitar o desperdício fica mais fácil quando você sabe '
    'o que preparar. Me conte o que você tem por aí!'
    '</div>',
    unsafe_allow_html=True
)


if not st.session_state.messages:

    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-icon">🍲</div>
        <div class="welcome-title">Bem-vindo ao NãoPerde!</div>
        <div class="welcome-description">
            Seu assistente inteligente está pronto para
            ajudar a organizar sua despensa e criar receitas incríveis.
        </div>
        <div class="welcome-highlight">
            O que você gostaria de aproveitar hoje?
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="suggestion-title">💡 Experimente começar por:</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "🍅  Sobra de vegetais",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Tenho tomates maduros e abobrinha sobrando. O que posso fazer?"
            )
            st.rerun()

    with col2:
        if st.button(
            "🧊  Organizar geladeira",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Como devo organizar os alimentos na geladeira para durarem mais?"
            )
            st.rerun()

    with col3:
        if st.button(
            "🍗  Frango e arroz",
            use_container_width=True
        ):
            st.session_state.pending_prompt = (
                "Tenho arroz cozido de ontem e frango desfiado. Me dê uma ideia de receita rápida."
            )
            st.rerun()


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


prompt = st.chat_input(
    "Digite os ingredientes ou sua dúvida..."
)

if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")


if prompt and prompt.strip():

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("O NãoPerde está criando sua sugestão..."):

            try:

                response = st.session_state.agent.chat(
                    prompt,
                    session_id=st.session_state.session_id
                )

                st.markdown(
                    response,
                    unsafe_allow_html=False
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as error:

                st.error(
                    "Não foi possível obter uma resposta. "
                    "Verifique sua conexão e tente novamente."
                )

                st.caption(str(error))