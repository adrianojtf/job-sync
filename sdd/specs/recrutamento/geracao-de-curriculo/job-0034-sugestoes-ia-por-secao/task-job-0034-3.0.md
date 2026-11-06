# Tarefa 3.0: Casos de uso SugerirAjusteSecaoCurriculo e SugerirAjusteExperiencia

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Expor as portas de ajuste existentes (com vaga) e a nova (sem vaga) em dois casos de uso pontuais e sem estado.

<requirements>
- `SugerirAjusteSecaoCurriculo.executar(secao, contexto | None)` e `SugerirAjusteExperiencia.executar(experiencia, contexto | None)`.
- Com contexto usa `AjustadorTextoPort`/`AjustadorExperienciaPort`; sem contexto usa `MelhoradorTextoCurriculoPort`.
- Seções aceitas: PERFIL, TECNOLOGIAS, EXPERIENCIAS; demais levantam `ValueError`.
- Limite de 5.000 caracteres por texto (validator); experiência exige descrição.
- Cargo, empresa e período da saída são sempre os do input.
- Falha do provedor (`RuntimeError`/`ValueError`) vira `SugestaoIAIndisponivel`, com handler 502 em `exceptions.py`.
- Log INFO com modo, tipo, tamanhos e duração, sem conteúdo.
- Risco documentado: o ajuste de tecnologias da vaga inclui tecnologias que o usuário pode não ter.
- Complexidade: high. Dependências: 1.0, 2.0.
</requirements>

## Subtarefas

- [ ] 3.1 Testes dos dois casos de uso (Red).
- [ ] 3.2 Exceção e handler 502.
- [ ] 3.3 Validators.
- [ ] 3.4 Services e DTOs.

## Detalhes de Implementação

Ver "Interfaces Principais", "Pontos de Integração" e "Monitoramento" em `techspec-job-0034.md`.

## Critérios de Sucesso

- Com contexto delega à porta de vaga com o texto recebido; sem contexto delega à porta nova.
- Falha da IA resulta em 502 e nunca altera dados.

## Testes da Tarefa

- [ ] Testes de unidade dos dois casos de uso e do handler.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/service_layer/sugerir_ajuste_secao_curriculo/`
- `src/jobsync/curriculo/service_layer/sugerir_ajuste_experiencia/`
- `src/jobsync/curriculo/service_layer/sugestao_ia_indisponivel.py`
- `src/jobsync/entrypoints/api/exceptions.py`
