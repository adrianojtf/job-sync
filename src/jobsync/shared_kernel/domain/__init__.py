"""Value Objects e conceitos de domínio compartilhados entre domínios.

Conceitos centralizados aqui são usados por mais de um domínio sem que
domínios distintos precisem depender diretamente uns dos outros.

Decisões de migração:
- NomeArquivo e CatalogoLocalizacao foram movidos para ca porque sao
  utilizados por curriculo, vaga_externa e outros domínios.
- AnaliseVaga, ResultadoAtsScore e seus tipos correlatos
  (RequisitoTecnico, CategoriaRequisitoTecnico, TipoRequisitoTecnico,
  OrigemRequisitoTecnico) sao *candidatos* a shared_kernel: sao Value
  Objects imutáveis consumidos pelos domínios vaga, ats_score,
  curriculo e vaga_externa. No entanto, a migracao destes conceitos sera
  realizado junto com a migracao dos domínios vaga e ats_score
  (tarefas 3.0 a 6.0), evitando refatoracoes de grande porte que
  quebrariam o baseline verde neste passo incremental.
"""

from jobsync.shared_kernel.domain.catalogo_localizacao import CatalogoLocalizacao
from jobsync.shared_kernel.domain.nome_arquivo import NomeArquivo
from jobsync.shared_kernel.domain.score_avaliacao import (
    ResultadoDimensaoAvaliacao,
    calcular_score_geral,
)

__all__ = [
    "CatalogoLocalizacao",
    "NomeArquivo",
    "ResultadoDimensaoAvaliacao",
    "calcular_score_geral",
]
