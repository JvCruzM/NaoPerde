"""
Módulo de Gerenciamento de Estoque - NãoPerde
Responsável pelo armazenamento local em arquivo JSON e pelas regras de decisão sobre prazos de validade.
"""

import json
import os
from datetime import datetime, date

CAMINHO_JSON = os.path.join(os.path.dirname(__file__), "data", "inventory.json")


def _garantir_diretorio(caminho):
    """Garante que a pasta de destino do arquivo JSON exista."""
    pasta = os.path.dirname(caminho)
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)


def init_storage(caminho_json=CAMINHO_JSON):
    """
    Inicializa o arquivo JSON caso ele ainda não exista.
    Cria uma estrutura com uma lista vazia de alimentos.
    """
    _garantir_diretorio(caminho_json)
    if not os.path.exists(caminho_json):
        dados_iniciais = {"alimentos": []}
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(dados_iniciais, f, ensure_ascii=False, indent=2)


def _carregar_dados(caminho_json=CAMINHO_JSON):
    """Lê os dados salvos no arquivo JSON."""
    init_storage(caminho_json)
    try:
        with open(caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"alimentos": []}


def _salvar_dados(dados, caminho_json=CAMINHO_JSON):
    """Salva os dados no arquivo JSON com formatação legível."""
    _garantir_diretorio(caminho_json)
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def calcular_prioridade(data_validade_str):
    """
    REGRAS DE DECISÃO DO NÃO-PERDE:
    - ⚫ Vencido: data menor que hoje.
    - 🔴 Crítico/Urgente: vence hoje, amanhã ou em até 2 dias.
    - 🟡 Atenção: vence entre 3 e 5 dias.
    - 🟢 Seguro: mais de 5 dias restantes.
    """
    try:
        if "/" in data_validade_str:
            data_val = datetime.strptime(data_validade_str, "%d/%m/%Y").date()
        else:
            data_val = datetime.strptime(data_validade_str, "%Y-%m-%d").date()
    except Exception:
        return 999, "Data inválida", "⚪ INDEFINIDO"

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


def adicionar_alimento(nome, quantidade, categoria, data_validade, caminho_json=CAMINHO_JSON):
    """Cadastra um novo alimento no arquivo JSON."""
    dados = _carregar_dados(caminho_json)
    alimentos = dados.get("alimentos", [])

    # Gera um ID sequencial numérico
    novo_id = max([item["id"] for item in alimentos], default=0) + 1

    novo_alimento = {
        "id": novo_id,
        "nome": nome.strip(),
        "quantidade": quantidade.strip(),
        "categoria": categoria.strip(),
        "data_validade": data_validade.strip(),
        "status": "disponivel",  # disponivel, consumido, descartado
        "cadastrado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    alimentos.append(novo_alimento)
    dados["alimentos"] = alimentos
    _salvar_dados(dados, caminho_json)
    return novo_id


def listar_alimentos(apenas_disponiveis=True, caminho_json=CAMINHO_JSON):
    """
    Retorna todos os alimentos com seus cálculos de urgência.
    Ordena pelos alimentos que vencem primeiro (Regra FEFO).
    """
    dados = _carregar_dados(caminho_json)
    alimentos = dados.get("alimentos", [])

    if apenas_disponiveis:
        alimentos = [a for a in alimentos if a.get("status") == "disponivel"]

    resultado = []
    for item in alimentos:
        dias, msg_prazo, nivel = calcular_prioridade(item["data_validade"])
        resultado.append({
            "id": item["id"],
            "nome": item["nome"],
            "quantidade": item["quantidade"],
            "categoria": item["categoria"],
            "data_validade": item["data_validade"],
            "dias_restantes": dias,
            "status_prazo": msg_prazo,
            "nivel_urgencia": nivel,
            "status": item.get("status", "disponivel")
        })

    # Ordena por data de validade (menor número de dias restantes primeiro)
    resultado.sort(key=lambda x: x["dias_restantes"])
    return resultado


def marcar_como_consumido(alimento_id, caminho_json=CAMINHO_JSON):
    """Atualiza o status do alimento para 'consumido'."""
    dados = _carregar_dados(caminho_json)
    alterado = False

    for item in dados.get("alimentos", []):
        if item["id"] == alimento_id:
            item["status"] = "consumido"
            alterado = True
            break

    if alterado:
        _salvar_dados(dados, caminho_json)
    return alterado


def remover_alimento(alimento_id, caminho_json=CAMINHO_JSON):
    """Remove um alimento da lista JSON pelo ID."""
    dados = _carregar_dados(caminho_json)
    alimentos = dados.get("alimentos", [])
    total_antes = len(alimentos)

    dados["alimentos"] = [item for item in alimentos if item["id"] != alimento_id]

    if len(dados["alimentos"]) < total_antes:
        _salvar_dados(dados, caminho_json)
        return True
    return False


def gerar_relatorio_para_o_agente(caminho_json=CAMINHO_JSON):
    """
    Gera o resumo da despensa formatado para o Prompt do Agente de IA.
    """
    alimentos = listar_alimentos(apenas_disponiveis=True, caminho_json=caminho_json)
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


# Teste rápido se o arquivo for executado
if __name__ == "__main__":
    print("Inicializando armazenamento em JSON...")
    init_storage()

    print("Cadastrando alimentos de teste no JSON...")
    adicionar_alimento("Leite Integral", "1 litro", "Laticínios", date.today().strftime("%Y-%m-%d"))
    adicionar_alimento("Tomate", "3 unidades", "Hortifrúti", date.today().strftime("%Y-%m-%d"))
    adicionar_alimento("Queijo Prato", "200g", "Laticínios", "2026-11-08")
    adicionar_alimento("Arroz Branco", "1 kg", "Grãos", "2026-12-31")

    print("\nRelatório formatado para o Agente de IA:\n")
    print(gerar_relatorio_para_o_agente())
