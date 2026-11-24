"""Roteiro da avaliação manual da JOB-0045 (task 10.0): reconhecimento e geração dos quatro blocos.

Uso, a partir da raiz do repositório:

    PYTHONPATH=src python sdd/specs/recrutamento/plataforma-base/job-0045-contexto-responsabilidades-realizacoes-e-skills-por-experiencia/avaliar-blocos.py
    PYTHONPATH=src python .../avaliar-blocos.py --dry-run   # a IA é simulada, sem chamar a OpenAI

Exige OPENAI_API_KEY (e OPENAI_MODEL, se não for o padrão), lidas do ambiente ou do .env da raiz.

Três verificações, com o exemplo da Starian do PRD:
1. Reconhecimento: o texto completo é separado nos quatro blocos sem chamar a IA e sem alterar nada.
2. Geração: com só a linha "Technologies:", a IA completa os outros três blocos; o roteiro mostra o
   resultado, confere se as skills reconhecidas ficaram intactas e lista os números gerados (estimativas).
3. Tempo: estrutura seis experiências de uma vez (4 chamadas em paralelo, no máximo) e mostra a latência,
   que precisa ficar dentro do aviso de até 1 minuto.
"""
from __future__ import annotations

import re
import sys
import time
from unittest.mock import Mock

from dotenv import load_dotenv

from jobsync.perfil_estruturado.adapters.completador_blocos_experiencia_openai_client import (
    CompletadorBlocosExperienciaOpenAIClient,
)
from jobsync.perfil_estruturado.domain.estruturar_experiencia_service import EstruturarExperienciaService
from jobsync.perfil_estruturado.domain.perfil_estruturado import ExperienciaProfissional
from jobsync.shared_kernel.adapters.cliente_openai_client import ClienteOpenAI

COMPLETA = """\
Context: At Starian, one of Brazil's leading ERP companies for the construction industry, I am responsible for developing and maintaining critical features in a corporate ERP system, with a focus on financial modules such as Accounts Receivable.
Key Responsibilities:
- End-to-end ownership of features within an enterprise ERP platform, with a focus on Accounts Receivable and financial processes.
- Acting as Feature Lead, coordinating technical decisions and collaborating with Product, QA, and a cross-functional team of 10 professionals.
Key Achievements:
- Contributed to the evolution of ERP financial capabilities supporting more than 1,000 users.
Technologies: Java | PostgreSQL | SQL | REST APIs | React | JavaScript | JSP | WildFly | Flyway | ERP | Accounts Receivable | SDD"""

SO_SKILLS = "Technologies: Java | PostgreSQL | SQL | REST APIs | React | WildFly | Flyway"

NUMERO = re.compile(r"\d[\d.,]*%?")


def _experiencia(descricao: str, empresa: str = "Starian") -> ExperienciaProfissional:
    return ExperienciaProfissional(empresa=empresa, cargo="Software Engineer", periodo="2024 - Atual", descricao=descricao)


def _blocos(experiencia: ExperienciaProfissional) -> None:
    print(f"  Contexto: {experiencia.contexto}")
    print(f"  Responsabilidades ({len(experiencia.responsabilidades)}):")
    for item in experiencia.responsabilidades:
        print(f"    - {item}")
    print(f"  Realizações ({len(experiencia.conquistas)}):")
    for conquista in experiencia.conquistas:
        print(f"    - {conquista.texto}")
    print(f"  Skills ({len(experiencia.skills)}): {' | '.join(experiencia.skills)}")


def main() -> None:
    load_dotenv()
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        cliente = Mock(spec=ClienteOpenAI)
        cliente.solicitar_json.return_value = {
            "contexto": "(dry-run) contexto.",
            "responsabilidades": ["(dry-run) responsabilidade 1", "(dry-run) responsabilidade 2", "(dry-run) 3"],
            "realizacoes": ["(dry-run) realização 1", "(dry-run) realização 2", "(dry-run) 3"],
            "skills": ["(dry-run)"],
        }
    else:
        cliente = ClienteOpenAI()
    estruturador = EstruturarExperienciaService(CompletadorBlocosExperienciaOpenAIClient(cliente))

    print("=== 1. Reconhecimento (sem IA): o texto completo sai idêntico nos quatro blocos ===")
    reconhecida = estruturador.executar(_experiencia(COMPLETA))
    _blocos(reconhecida)
    print(f"  Chamadas à IA: {cliente.solicitar_json.call_count} (esperado: 0)")
    print(f"  Descrição restante: {reconhecida.descricao!r} (esperado: '')")

    print("\n=== 2. Geração: só as skills no texto; a IA completa os outros três blocos ===")
    inicio = time.perf_counter()
    completada = estruturador.executar(_experiencia(SO_SKILLS))
    latencia = time.perf_counter() - inicio
    _blocos(completada)
    skills_originais = tuple(skill.strip() for skill in SO_SKILLS.split(":", 1)[1].split("|"))
    print(f"  Skills reconhecidas intactas: {completada.skills == skills_originais} (esperado: True)")
    numeros = NUMERO.findall(" ".join([completada.contexto, *completada.responsabilidades, *(c.texto for c in completada.conquistas)]))
    print(f"  Números gerados (conferir se são realistas para o papel): {numeros or 'nenhum'}")
    print(f"  Latência: {latencia:.1f}s")

    print("\n=== 3. Tempo: seis experiências de uma vez ===")
    experiencias = [_experiencia(SO_SKILLS, empresa=f"Empresa {n}") for n in range(6)]
    inicio = time.perf_counter()
    estruturadas = estruturador.executar_varias(experiencias)
    latencia = time.perf_counter() - inicio
    print(f"  Experiências estruturadas: {len(estruturadas)} em {latencia:.1f}s (esperado: menos de 60s)")


if __name__ == "__main__":
    main()
