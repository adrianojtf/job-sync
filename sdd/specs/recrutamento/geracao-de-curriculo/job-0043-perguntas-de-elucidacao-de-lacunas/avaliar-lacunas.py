"""Roteiro da avaliação manual da JOB-0043 (task 7.0): lacunas da vaga e redação da conquista.

Uso, a partir da raiz do repositório:

    PYTHONPATH=src python sdd/specs/recrutamento/geracao-de-curriculo/job-0043-perguntas-de-elucidacao-de-lacunas/avaliar-lacunas.py
    PYTHONPATH=src python .../avaliar-lacunas.py --dry-run   # só mostra os prompts, sem chamar a IA

Exige OPENAI_API_KEY (e OPENAI_MODEL, se não for o padrão), lidas do ambiente ou do .env da raiz.
Para cada vaga, usa o `IdentificadorLacunasOpenAIClient` real com um histórico sintético de backend
Java, imprime as lacunas (esperado: até 5, só temas que o histórico não sustenta) e a latência. Depois
pede ao `RedatorConquistaOpenAIClient` a conquista da primeira lacuna a partir de um caso de exemplo e
lista os números e as tecnologias da saída que não estão no caso.
"""
from __future__ import annotations

import re
import sys
import time
from unittest.mock import Mock

from dotenv import load_dotenv

from jobsync.curriculo import ContextoVaga, ExperienciaParaAvaliacao
from jobsync.curriculo.adapters.identificador_lacunas_openai_client import IdentificadorLacunasOpenAIClient
from jobsync.curriculo.adapters.redator_conquista_openai_client import RedatorConquistaOpenAIClient
from jobsync.curriculo.domain.lacuna_da_vaga import HistoricoDoCandidato, LacunaDaVaga, principais
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI
from jobsync.vaga import AnaliseVaga

HISTORICO = HistoricoDoCandidato(
    resumo="Engenheiro de software backend com foco em integrações e sistemas distribuídos.",
    experiencias=(
        ExperienciaParaAvaliacao(
            cargo="Engenheiro de Software",
            empresa="TechCorp",
            periodo="2020 - Atual",
            descricao="Backend em Java e PostgreSQL para o setor financeiro.",
            conquistas=(
                "Reduzi o tempo de deploy de 40 para 10 minutos com um pipeline automatizado.",
                "Integrei a plataforma a um sistema legado de faturamento por meio de mensageria.",
            ),
        ),
    ),
    tecnologias=("Java", "PostgreSQL", "Kafka"),
)

VAGAS = {
    "Forward Deployed Engineer (cliente, MVP, agentes de IA)": (
        "Forward Deployed Engineer Sênior",
        "Atuar junto ao cliente para entender o problema, construir MVPs rápidos, criar agentes de IA com "
        "avaliações automatizadas e preparar a solução para operação com observabilidade e aprovação humana.",
    ),
    "Engenheiro de Software (aderente ao histórico)": (
        "Engenheiro de Software Backend",
        "Desenvolver APIs em Java com PostgreSQL e integrações por mensageria com Kafka em sistemas financeiros.",
    ),
}

CASO = "Fiquei dois meses no cliente e entreguei o MVP de conciliação com a equipe deles."
NUMERO = re.compile(r"\d+")


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
        cliente.solicitar_json.return_value = {"lacunas": [{"tema": "(dry-run)", "pergunta": "(dry-run)"}], "conquista": "(dry-run)"}
    else:
        cliente = ClienteOpenAI()
    identificador = IdentificadorLacunasOpenAIClient(cliente)
    redator = RedatorConquistaOpenAIClient(cliente)

    for nome, (cargo, descricao) in VAGAS.items():
        inicio = time.perf_counter()
        lacunas = principais(identificador.identificar(HISTORICO, _contexto(cargo, descricao)))
        segundos = time.perf_counter() - inicio
        if dry_run:
            print(cliente.solicitar_json.call_args_list[-1].kwargs["prompt_usuario"])
            print("-" * 60)
            continue
        print(f"\n=== {nome} ({segundos:.1f}s) ===")
        print(f"Lacunas: {len(lacunas)} (esperado: até 5)")
        for lacuna in lacunas:
            print(f"  - [{lacuna.tema}] {lacuna.pergunta}")
        if not lacunas:
            continue
        texto = redator.redigir(LacunaDaVaga(lacunas[0].tema, lacunas[0].pergunta), CASO, "Engenheiro de Software", "pt")
        novos = sorted(set(NUMERO.findall(texto)) - set(NUMERO.findall(CASO)))
        print(f"Conquista escrita a partir do caso: {texto}")
        print(f"Números fora do caso: {novos or 'nenhum'}")


if __name__ == "__main__":
    main()
