"""Roteiro da avaliação manual da JOB-0042 (task 5.0): seleção de conquistas do banco por vaga.

Uso, a partir da raiz do repositório:

    PYTHONPATH=src python sdd/specs/recrutamento/geracao-de-curriculo/job-0042-banco-de-conquistas-por-experiencia/avaliar-banco-conquistas.py
    PYTHONPATH=src python .../avaliar-banco-conquistas.py --dry-run   # só mostra o prompt, sem chamar a IA

Exige OPENAI_API_KEY (e OPENAI_MODEL, se não for o padrão), lidas do ambiente ou do arquivo .env da raiz. Usa o `AjustadorExperienciaOpenAIClient` real,
um banco de 8 conquistas e duas vagas de áreas diferentes. Imprime, por vaga: as conquistas escolhidas,
a quantidade, a latência e os números que aparecem na saída e não existem no banco.
"""
from __future__ import annotations

import re
import sys
import time
from unittest.mock import Mock

from dotenv import load_dotenv

from jobsync.curriculo import ContextoVaga, DiretrizesExperiencia, ExperienciaParaAvaliacao
from jobsync.curriculo.adapters.ajustador_experiencia_openai_client import AjustadorExperienciaOpenAIClient
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.vaga import AnaliseVaga

BANCO = (
    "Reduzi o tempo de deploy de 40 para 10 minutos com um pipeline automatizado.",
    "Liderei a migração do banco de dados de um monólito para PostgreSQL sem indisponibilidade.",
    "Atuei junto ao cliente na entrega de um MVP de pagamentos em 6 semanas.",
    "Desenhei APIs REST usadas por 12 serviços internos.",
    "Mentorei 3 pessoas desenvolvedoras juniores em revisão de código.",
    "Implantei observabilidade com métricas e alertas e reduzi incidentes de produção.",
    "Integrei a plataforma a um sistema legado de faturamento por meio de mensageria.",
    "Documentei decisões de arquitetura e padronizei a revisão técnica entre os times.",
)

VAGAS = {
    "Forward Deployed Engineer (cliente, MVP, integração)": (
        "Forward Deployed Engineer Sênior",
        "Atuar junto ao cliente para entender o problema, construir MVPs rápidos, integrar com sistemas "
        "legados e preparar a solução para operação com observabilidade. Mentoria técnica de builders.",
    ),
    "Engenheiro de Dados (fora do foco do banco)": (
        "Engenheiro de Dados Pleno",
        "Construir pipelines de dados em lote e streaming, modelar tabelas analíticas, garantir qualidade "
        "e governança dos dados e otimizar consultas em larga escala.",
    ),
}

DESCRICAO_EXPERIENCIA = "Desenvolvimento backend em Java e PostgreSQL na empresa."
NUMERO = re.compile(r"\d+")


def _experiencia() -> ExperienciaParaAvaliacao:
    return ExperienciaParaAvaliacao(
        cargo="Engenheiro de Software",
        empresa="TechCorp",
        periodo="2020 - Atual",
        descricao=DESCRICAO_EXPERIENCIA,
        conquistas=BANCO,
    )


def _contexto(cargo: str, descricao: str) -> ContextoVaga:
    return ContextoVaga(
        descricao_vaga=descricao,
        idioma_alvo="pt",
        analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original=descricao),
        cargo_alvo=cargo,
    )


def main() -> None:
    load_dotenv()
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        cliente = Mock(spec=ClienteOpenAI)
        cliente.solicitar_json.return_value = {"conquistas": ["(dry-run)"], "contexto": "(dry-run)"}
    else:
        cliente = ClienteOpenAI()
    ajustador = AjustadorExperienciaOpenAIClient(cliente)
    numeros_do_banco = set(NUMERO.findall(" ".join(BANCO) + " " + DESCRICAO_EXPERIENCIA))

    for nome, (cargo, descricao) in VAGAS.items():
        inicio = time.perf_counter()
        resultado = ajustador.ajustar(_experiencia(), _contexto(cargo, descricao), DiretrizesExperiencia())
        segundos = time.perf_counter() - inicio
        if dry_run:
            print(cliente.solicitar_json.call_args.kwargs["prompt_usuario"])
            print("-" * 60)
            continue
        saida = " ".join(resultado.conquistas) + " " + resultado.contexto
        numeros_novos = sorted(set(NUMERO.findall(saida)) - numeros_do_banco)
        print(f"\n=== {nome} ({segundos:.1f}s) ===")
        print(f"Conquistas escolhidas: {len(resultado.conquistas)} (esperado: de 3 a 5)")
        for conquista in resultado.conquistas:
            print(f"  - {conquista}")
        print(f"Contexto: {resultado.contexto}")
        print(f"Números fora do banco: {numeros_novos or 'nenhum'}")


if __name__ == "__main__":
    main()
