import os
from datetime import date, timedelta

import streamlit as st
from dotenv import load_dotenv

from src import conversations
from src.agent import NaoPerdeAgent
from src.expiration import get_expiration_report
from src.inventory import (
    add_food, get_inventory, update_food, mark_as_consumed,
    mark_as_discarded, remove_food,
)

load_dotenv()
st.set_page_config(page_title="NãoPerde | Controle de alimentos", page_icon="🍲", layout="wide")

st.markdown("""
<style>
.stApp { background: #f5f8f5; }
[data-testid="stSidebar"] { background: #173d2d; }
[data-testid="stSidebar"] { color: #ffffff; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #ffffff;
}
/* Botões da barra lateral: seletor abrangente para versões diferentes do Streamlit. */
section[data-testid="stSidebar"] button,
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] [data-testid="stButton"] button,
[data-testid="stSidebar"] [data-testid^="stBaseButton"],
[data-testid="stSidebar"] [class*="st-key-conv_"] button,
[data-testid="stSidebar"] [class*="st-key-delete_conv_"] button {
    background: #27543e !important;
    background-color: #27543e !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid #648d74 !important;
    border-radius: 9px !important;
    opacity: 1 !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] button *,
[data-testid="stSidebar"] button *,
[data-testid="stSidebar"] [data-testid^="stBaseButton"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    fill: #ffffff !important;
    opacity: 1 !important;
}
section[data-testid="stSidebar"] button:hover,
[data-testid="stSidebar"] button:hover,
[data-testid="stSidebar"] [data-testid^="stBaseButton"]:hover {
    background: #367653 !important;
    background-color: #367653 !important;
    border-color: #a3d3b5 !important;
}
section[data-testid="stSidebar"] button:focus-visible,
[data-testid="stSidebar"] button:focus-visible {
    outline: 2px solid #ffffff !important;
    outline-offset: 2px;
}
.block-container { max-width: 1250px; padding-top: 2rem; }
.hero { padding: 1.4rem 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#174b35,#327653); color: white; margin-bottom: 1.2rem; }
.hero h1 { color: white; margin: 0; }
.hero p { color: #e3f2e8; margin: .35rem 0 0; }
.metric-card { background:white; padding:1rem 1.2rem; border:1px solid #e1e9e2; border-radius:14px; }
.small-muted { color:#637568; font-size:.9rem; }
</style>
""", unsafe_allow_html=True)


def get_agent():
    if "agent" not in st.session_state:
        st.session_state.agent = NaoPerdeAgent()
    return st.session_state.agent


def refresh_conversations():
    st.session_state.conversations = conversations.load_conversations()


if "active_conversation_id" not in st.session_state:
    refresh_conversations()
    if st.session_state.conversations:
        st.session_state.active_conversation_id = st.session_state.conversations[0]["id"]
    else:
        new = conversations.create_conversation()
        st.session_state.active_conversation_id = new["id"]

try:
    inventory = get_inventory()
except Exception as exc:
    st.error(f"Não foi possível carregar o estoque: {exc}")
    st.stop()

available = [f for f in inventory if f.get("status") == "disponivel"]
consumed = [f for f in inventory if f.get("status") == "consumido"]
discarded = [f for f in inventory if f.get("status") == "descartado"]
report = get_expiration_report(available) if available else []

with st.sidebar:
    st.markdown("# 🍲 NãoPerde")
    st.caption("Menos desperdício, mais aproveitamento")
    st.divider()
    st.markdown("### 💬 Histórico de conversas")
    if st.button("＋ Nova conversa", use_container_width=True):
        new = conversations.create_conversation()
        st.session_state.active_conversation_id = new["id"]
        st.rerun()
    convs = conversations.load_conversations()
    if not convs:
        st.caption("Nenhuma conversa salva.")
    for conv in convs:
        conv_id = conv["id"]
        label = (conv.get("title") or "Nova conversa")[:32]
        selected = conv_id == st.session_state.active_conversation_id
        open_col, delete_col = st.columns([0.80, 0.20], gap="small")
        with open_col:
            if st.button(("● " if selected else "  ") + label,
                         key=f"conv_{conv_id}", use_container_width=True,
                         help="Abrir conversa"):
                st.session_state.active_conversation_id = conv_id
                st.session_state.pop("conversation_pending_delete", None)
                st.rerun()
        with delete_col:
            if st.button("🗑", key=f"delete_conv_{conv_id}",
                         use_container_width=True,
                         help=f"Excluir conversa: {label}"):
                st.session_state.conversation_pending_delete = conv_id
                st.rerun()

        if st.session_state.get("conversation_pending_delete") == conv_id:
            st.caption(f"Excluir definitivamente «{label}»?")
            confirm_col, cancel_col = st.columns(2)
            if confirm_col.button("Excluir", key=f"confirm_conv_{conv_id}",
                                  use_container_width=True):
                conversations.delete_conversation(conv_id)
                st.session_state.pop("conversation_pending_delete", None)
                if selected:
                    remaining = conversations.load_conversations()
                    st.session_state.active_conversation_id = (
                        remaining[0]["id"] if remaining
                        else conversations.create_conversation()["id"]
                    )
                st.rerun()
            if cancel_col.button("Cancelar", key=f"cancel_conv_{conv_id}",
                                 use_container_width=True):
                st.session_state.pop("conversation_pending_delete", None)
                st.rerun()
    st.divider()
    st.caption("O estoque funciona mesmo sem configurar a API do Groq.")

st.markdown('<div class="hero"><h1>🍲 NãoPerde</h1><p>Organize seus alimentos, acompanhe validades e descubra como aproveitar melhor sua despensa.</p></div>', unsafe_allow_html=True)
tab_dashboard, tab_stock, tab_chat = st.tabs(["📊 Visão geral", "🥬 Meu estoque", "🤖 Assistente IA"])

with tab_dashboard:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Disponíveis", len(available))
    c2.metric("Próximos do vencimento", sum(0 <= x["days_remaining"] <= 7 for x in report))
    c3.metric("Consumidos", len(consumed))
    c4.metric("Descartados", len(discarded))
    st.subheader("⚠️ Atenção às validades")
    if not report:
        st.success("Nenhum alimento disponível cadastrado. Adicione alimentos na aba Meu estoque.")
    else:
        urgent = [x for x in report if x["days_remaining"] <= 7]
        if not urgent:
            st.info("Nenhum alimento cadastrado vence nos próximos 7 dias.")
        for item in urgent:
            days = item["days_remaining"]
            if days < 0:
                st.error(f"**{item['name']}** — data expirada em {item['expiration_date']}.")
            elif days == 0:
                st.warning(f"**{item['name']}** — vence hoje ({item['expiration_date']}).")
            else:
                st.warning(f"**{item['name']}** — vence em {days} dia(s), em {item['expiration_date']}.")
    st.subheader("Estoque disponível")
    if available:
        st.dataframe([{
            "Alimento": f.get("name"), "Quantidade": f"{f.get('quantity')} {f.get('unit')}",
            "Categoria": f.get("category"), "Validade": f.get("expiration_date")
        } for f in sorted(available, key=lambda x: x.get("expiration_date", "9999"))],
            use_container_width=True, hide_index=True)
    else:
        st.caption("Seu estoque está vazio por enquanto.")

with tab_stock:
    st.subheader("Cadastrar alimento")
    with st.form("add_food_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        name = col1.text_input("Nome do alimento *", placeholder="Ex.: Leite")
        quantity = col2.number_input("Quantidade *", min_value=0.01, value=1.0, step=0.5)
        unit = col3.selectbox("Unidade *", ["unidade(s)", "kg", "g", "L", "ml", "pacote(s)", "lata(s)", "porção(ões)"])
        col4, col5 = st.columns(2)
        category = col4.selectbox("Categoria *", ["Hortifruti", "Laticínios", "Carnes", "Grãos e cereais", "Bebidas", "Enlatados", "Padaria", "Outros"])
        expiry = col5.date_input("Data de validade *", value=date.today() + timedelta(days=7), min_value=date(2000, 1, 1))
        submitted = st.form_submit_button("＋ Adicionar ao estoque", type="primary", use_container_width=True)
        if submitted:
            try:
                if not name.strip():
                    st.error("Informe o nome do alimento.")
                else:
                    add_food(name, quantity, unit, expiry, category)
                    st.success(f"{name.strip()} cadastrado com sucesso!")
                    st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível cadastrar: {exc}")

    st.divider()
    st.subheader("Alimentos cadastrados")
    if not inventory:
        st.info("Ainda não há alimentos cadastrados. Use o formulário acima para começar.")
    for food in inventory:
        status = food.get("status", "disponivel")
        with st.expander(f"{'🥬' if status == 'disponivel' else '✅' if status == 'consumido' else '🗑️'} {food.get('name')} — {food.get('quantity')} {food.get('unit')} | {food.get('expiration_date')} | {status}"):
            if status == "disponivel":
                with st.form(f"edit_{food['id']}"):
                    a, b, c = st.columns(3)
                    edit_name = a.text_input("Nome", value=food.get("name", ""))
                    edit_qty = b.number_input("Quantidade", min_value=0.01, value=float(food.get("quantity", 1)), step=0.5)
                    units = [food.get("unit", "unidade(s)"), "unidade(s)", "kg", "g", "L", "ml", "pacote(s)", "lata(s)", "porção(ões)"]
                    edit_unit = c.selectbox("Unidade", list(dict.fromkeys(units)), index=0)
                    d, e = st.columns(2)
                    categories = [food.get("category", "Outros"), "Hortifruti", "Laticínios", "Carnes", "Grãos e cereais", "Bebidas", "Enlatados", "Padaria", "Outros"]
                    edit_category = d.selectbox("Categoria", list(dict.fromkeys(categories)), index=0)
                    edit_expiry = e.date_input("Validade", value=date.fromisoformat(food["expiration_date"]))
                    save_edit = st.form_submit_button("Salvar alterações")
                    if save_edit:
                        try:
                            update_food(food["id"], name=edit_name, quantity=edit_qty, unit=edit_unit,
                                        category=edit_category, expiration_date=edit_expiry)
                            st.success("Alimento atualizado.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
                b1, b2, b3 = st.columns(3)
                if b1.button("Marcar consumido", key=f"consume_{food['id']}"):
                    mark_as_consumed(food["id"]); st.rerun()
                if b2.button("Marcar descartado", key=f"discard_{food['id']}"):
                    mark_as_discarded(food["id"]); st.rerun()
                if b3.button("Excluir", key=f"delete_{food['id']}"):
                    remove_food(food["id"]); st.rerun()
            else:
                st.caption("Este registro não está mais disponível no estoque ativo.")
                if st.button("Excluir registro", key=f"delete_old_{food['id']}"):
                    remove_food(food["id"]); st.rerun()

with tab_chat:
    st.subheader("Converse com seu assistente")
    st.caption("O NãoPerde utiliza os alimentos disponíveis e suas datas cadastradas para contextualizar as respostas.")
    active = conversations.get_conversation(st.session_state.active_conversation_id)
    if active is None:
        active = conversations.create_conversation()
        st.session_state.active_conversation_id = active["id"]
    for msg in active.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    api_ready = bool(os.getenv("GROQ_API_KEY"))
    if not api_ready:
        st.warning("O estoque está disponível, mas o chat com IA está desativado. Configure GROQ_API_KEY no arquivo .env para conversar com o agente.")
    user_prompt = st.chat_input("Pergunte sobre seus alimentos ou peça uma receita...", disabled=not api_ready)
    if user_prompt:
        try:
            conversations.add_message(active["id"], "user", user_prompt)
            with st.chat_message("user"):
                st.markdown(user_prompt)
            with st.chat_message("assistant"):
                with st.spinner("Analisando seu estoque..."):
                    agent = get_agent()
                    current = conversations.get_conversation(active["id"])
                    agent._historicos[active["id"]] = current.get("messages", [])[:-1][-agent.max_history * 2:]
                    answer = agent.chat(user_prompt, estoque=get_inventory(only_available=True), session_id=active["id"])
                    st.markdown(answer)
            conversations.add_message(active["id"], "assistant", answer)
            st.rerun()
        except Exception as exc:
            st.error(f"Não foi possível obter uma resposta do agente: {exc}")

    if st.button("🗑 Excluir esta conversa", type="secondary"):
        st.session_state.conversation_pending_delete = active["id"]
        st.info("Confirme a exclusão no histórico de conversas, na barra lateral.")
        st.rerun()

st.caption("NãoPerde • A data de validade informada não garante, isoladamente, que um alimento esteja próprio para consumo.")
