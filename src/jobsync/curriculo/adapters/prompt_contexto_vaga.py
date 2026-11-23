"""Trechos de prompt comuns aos adapters de IA que recebem um ContextoVaga."""
from __future__ import annotations

from jobsync.curriculo.domain.contexto_vaga import ContextoVaga


def linha_cargo_alvo(contexto: ContextoVaga) -> str:
    """Linha com o cargo-alvo, seguida de linha em branco; vazia quando não há cargo-alvo."""
    if not contexto.cargo_alvo:
        return ""
    return f"Cargo-alvo (título da vaga): {contexto.cargo_alvo}\n\n"


REGRA_RESPONSABILIDADES_IMPLICITAS = (
    "Se a vaga pedir uma responsabilidade essencial da vaga que seja comum ao cargo desta "
    "experiência (ex.: code review para um desenvolvedor, gestão de backlog para um PO) e ela "
    "não estiver no texto, cite-a em uma conquista ou no contexto. Não cite responsabilidades "
    "atípicas para o cargo exercido e não invente métricas para elas."
)
"""Regra genérica (JOB-0037): o que é implícito ao cargo exercido pode aparecer no currículo."""


REGRA_RESUMO_ADERENTE_A_VAGA = (
    "Reescreva o resumo profissional em um único parágrafo de até 60 palavras e até 3 frases, "
    "na mesma voz do resumo original. Apresente o candidato na linha do cargo-alvo, com a atuação "
    "típica desse cargo que o histórico do candidato sustenta, sem declarar como título um cargo "
    "que ele não exerceu. Escolha no máximo 3 temas centrais da vaga e escreva-os como ações do "
    "candidato, com frases próprias: não copie trechos da vaga, não faça listas de termos, não use "
    "ponto e vírgula e não fale da vaga nem da oportunidade. Omita o tema que o histórico não "
    "sustenta. Mantenha-se fiel aos fatos originais: não invente anos de experiência, cargos, "
    "empresas, tecnologias, práticas nem métricas, exceto as tecnologias equivalentes indicadas "
    "nesta instrução."
)
"""Regra do resumo (JOB-0040): curto, no eixo do cargo-alvo, sem copiar a vaga nem inventar fatos."""


REGRA_SELECAO_DE_CONQUISTAS = (
    "Há conquistas cadastradas pelo usuário para esta experiência. Escolha de 3 a 5 delas, as mais "
    "aderentes à vaga e ao cargo-alvo, com a mais relevante primeiro; esta faixa substitui a de 2 a 6 "
    "conquistas. Reescreva a redação para adequar o vocabulário à vaga, sem acrescentar fato, número, "
    "resultado, tecnologia ou prática que a conquista não tenha; esta regra prevalece sobre a permissão "
    "de propor métricas. Se houver menos de 3 conquistas cadastradas, use todas e complete as demais a "
    "partir da descrição original. Se nenhuma se relacionar com a vaga, escolha as 3 mais próximas, sem "
    "forçar uma relação inexistente."
)
"""Regra da seleção (JOB-0042): escolhe de 3 a 5 conquistas do banco sem acrescentar fato."""
