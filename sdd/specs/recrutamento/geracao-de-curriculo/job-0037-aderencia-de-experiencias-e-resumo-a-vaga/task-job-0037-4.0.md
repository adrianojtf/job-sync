# Tarefa 4.0: Trocas, cargo-alvo e responsabilidades implícitas na adaptação

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

A adaptação passa a gerar o plano, a passar as diretrizes de cada experiência e a devolver os ajustes no rascunho. Os prompts ganham as regras de troca, de manutenção explícita e de responsabilidades implícitas ao cargo.

<requirements>
- `AjustadorExperienciaPort.ajustar(experiencia, contexto, diretrizes)`.
- Prompt de experiência: troca com citação explícita no contexto (RF5); manutenção com citação explícita (RF6); responsabilidades implícitas típicas do cargo, sem métricas inventadas (RF10 a RF13); "não acrescente tecnologias além das do texto e das trocas indicadas".
- `AjustadorTextoPort.ajustar_secao(secao, contexto, ajustes)`: TECNOLOGIAS lista original e alvo (RF7); PERFIL pode citar o alvo (RF8) e deixa de conflitar com a instrução geral do prompt de usuário.
- Fonte PDF: seção EXPERIENCIAS recebe só cargo-alvo e regra de responsabilidades implícitas.
- `AdaptarCurriculoParaVaga`: chama o identificador, gera o plano, passa diretrizes e ajustes; falha do identificador gera `WARNING` e `PlanoAdaptacao.vazio()`.
- `RascunhoCurriculoAdaptado.ajustes_tecnologia`.
- Logs `INFO` com contagens de equivalências, trocas e manutenções, sem nomes.
- Injeção do identificador em `dependencies.py` e no Streamlit.
- Complexidade: high. Dependências: 3.0.
</requirements>

## Subtarefas

- [x] 4.1 Testes dos prompts e da adaptação (Red).
- [x] 4.2 Porta e adapter de experiência.
- [x] 4.3 Porta e adapter de texto (TECNOLOGIAS, PERFIL, EXPERIENCIAS da fonte PDF).
- [x] 4.4 Rascunho com `ajustes_tecnologia`.
- [x] 4.5 `AdaptarCurriculoParaVaga` e injeção.
- [x] 4.6 Dublês de E2E, incluindo o do identificador de equivalências (vindo da task 3.0).

## Detalhes de Implementação

Ver "Fluxo da adaptação" e "Regras dos prompts" em `techspec-job-0037.md`.

## Critérios de Sucesso

- Cada experiência recebe só as suas diretrizes.
- Adaptação conclui com plano vazio quando o identificador falha.
- O PDF gerado pelo fluxo atual continua igual quando não há trocas.

## Testes da Tarefa

- [x] Testes de unidade dos adapters, do rascunho e de `AdaptarCurriculoParaVaga`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/{ajustador_experiencia_port.py,ajustador_texto_port.py,rascunho_curriculo_adaptado.py}`
- `src/jobsync/curriculo/adapters/{ajustador_experiencia_openai_client.py,ajustador_texto_client.py}`
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/`
- `src/jobsync/entrypoints/api/dependencies.py`, `src/jobsync/entrypoints/streamlit_app.py`
- `src/jobsync/tests/curriculo/`, `src/jobsync/tests/e2e/app_e2e.py`
