"""
Módulo de Gerenciamento de Estoque - NãoPerde
Responsável pelo armazenamento local (SQLite) e pelas regras de decisão sobre prazos de validade.
"""

import sqlite3
from datetime import datetime, date

NOME_BANCO = "despensa.db"


def conectar(db_path=NOME_BANCO):
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    return sqlite3.connect(db_path)


def init_db(db_path=NOME_BANCO):
    """
    Inicializa a tabela de alimentos caso ainda não exista.
    Decisão técnica: SQLite nativo, leve e sem dependência de servidores externos.
    """
    with conectar(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade TEXT NOT NULL,
                categoria TEXT NOT NULL,
                data_validade DATE NOT NULL,
                status TEXT DEFAULT 'disponivel', -- disponivel, consumido, descartado
                cadastrado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def calcular_prioridade(data_validade_str):
    """
    REGRAS DE DECISÃO DO NÃO-PERDE:
    - 🔴 Crítico/Urgente: vence hoje, amanhã ou em até 2 dias (ou já vencido).
    - 🟡 Atenção: vence entre 3 e 5 dias.
    - 🟢 Seguro: mais de 5 dias restantes.
    """
    try:
        # Suporta tanto formato ISO (YYYY-MM-DD) quanto formato brasileiro (DD/MM/YYYY)
        if "/" in data_validade_str:
            data_val = datetime.strptime(data_validade_str, "%d/%m/%Y").date()
        else:
            data_val = datetime.strptime(data_validade_str, "%Y-%m-%d").date()
    except Exception:
        return 999, "Data inválida", "⚪"

    hoje = date.today()
    dias_restantes = (data_val - hoje).days

    if dias_restantes < 0:
        return dias_restantes, f"Vencido há {abs(dias_restantes)} dia(s)", "⚫ VENCIDO"
    elif dias_restantes == 0:
        return dias_restantes, "Vence hoje!", "🔴 URGENTE"
    elif dias_restantes == 1:
        return dias_restantes, "Vence amanhã!", "🔴 URGENTE"
    elif dias_restantes <= 2:
        return dias_restantes, f"Vence em {dias_restantes} dias", "🔴 URGENTE"
    elif dias_restantes <= 5:
        return dias_restantes, f"Vence em {dias_restantes} dias", "🟡 ATENÇÃO"
    else:
        return dias_restantes, f"Vence em {dias_restantes} dias", "🟢 SEGURO"


def adicionar_alimento(nome, quantidade, categoria, data_validade, db_path=NOME_BANCO):
    """Cadastra um novo alimento no inventário."""
    init_db(db_path)
    with conectar(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alimentos (nome, quantidade, categoria, data_validade)
            VALUES (?, ?, ?, ?)
        """, (nome.strip(), quantidade.strip(), categoria.strip(), data_validade.strip()))
        conn.commit()
        return cursor.lastrowid


def listar_alimentos(apenas_disponiveis=True, db_path=NOME_BANCO):
    """
    Retorna todos os alimentos com seus respectivos cálculos de urgência.
    Ordena pelos alimentos que vencem primeiro (Regra FEFO).
    """
    init_db(db_path)
    with conectar(db_path) as conn:
        cursor = conn.cursor()
        if apenas_disponiveis:
            cursor.execute("SELECT id, nome, quantidade, categoria, data_validade, status FROM alimentos WHERE status = 'disponivel' ORDER BY data_validade ASC")
        else:
            cursor.execute("SELECT id, nome, quantidade, categoria, data_validade, status FROM alimentos ORDER BY data_validade ASC")
        
        linhas = cursor.fetchall()

    resultado = []
    for linha in linhas:
        id_item, nome, qtd, cat, dt_val, status = linha
        dias, msg_prazo, nivel = calcular_prioridade(dt_val)
        resultado.append({
            "id": id_item,
            "nome": nome,
            "quantidade": qtd,
            "categoria": cat,
            "data_validade": dt_val,
            "dias_restantes": dias,
            "status_prazo": msg_prazo,
            "nivel_urgencia": nivel,
            "status": status
        })
    return resultado


def marcar_como_consumido(alimento_id, db_path=NOME_BANCO):
    """Registra que o alimento foi aproveitado (evitando o desperdício!)."""
    init_db(db_path)
    with conectar(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE alimentos SET status = 'consumido' WHERE id = ?", (alimento_id,))
        conn.commit()


def remover_alimento(alimento_id, db_path=NOME_BANCO):
    """Exclui o registro de um alimento."""
    init_db(db_path)
    with conectar(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alimentos WHERE id = ?", (alimento_id,))
        conn.commit()


def gerar_relatorio_para_o_agente(db_path=NOME_BANCO):
    """
    Prepara o resumo textual da despensa formatado especialmente
    para ser enviado ao Prompt do Agente de IA.
    """
    alimentos = listar_alimentos(apenas_disponiveis=True, db_path=db_path)
    if not alimentos:
        return "A despensa está vazia no momento."

    urgentes = []
    atencao = []
    seguros = []

    for a in alimentos:
        linha = f"- {a['nome']} ({a['quantidade']}, {a['categoria']}) - {a['status_prazo']}"
        if "URGENTE" in a['nivel_urgencia'] or "VENCIDO" in a['nivel_urgencia']:
            urgentes.append(linha)
        elif "ATENÇÃO" in a['nivel_urgencia']:
            atencao.append(linha)
        else:
            seguros.append(linha)

    texto = "=== ESTOQUE ATUAL DA DESPENSA (NÃO PERDE) ===\n"
    if urgentes:
        texto += "\n🔴 ALIMENTOS URGENTES (Consumir primeiro / Prioridade máxima):\n" + "\n".join(urgentes) + "\n"
    if atencao:
        texto += "\n🟡 ALIMENTOS EM ATENÇÃO (Consumir nos próximos dias):\n" + "\n".join(atencao) + "\n"
    if seguros:
        texto += "\n🟢 ALIMENTOS SEGUROS (Maior prazo de conservação):\n" + "\n".join(seguros) + "\n"

    return texto


# Teste rápido se o arquivo for executado diretamente
if __name__ == "__main__":
    print("Iniciando banco de dados de teste...")
    init_db()
    
    # Inserindo alguns exemplos ilustrativos
    print("Cadastrando alimentos de teste...")
    adicionar_alimento("Leite Integral", "1 litro", "Laticínios", date.today().strftime("%Y-%m-%d")) # vence hoje
    adicionar_alimento("Tomate", "3 unidades", "Hortifrúti", date.today().strftime("%Y-%m-%d"))      # vence hoje
    adicionar_alimento("Queijo Prato", "200g", "Laticínios", "2026-11-08")
    adicionar_alimento("Arroz Branco", "1 kg", "Grãos", "2026-12-31")

    print("\nRelatório formatado para o Agente de IA:\n")
    print(gerar_relatorio_para_o_agente())
