# Tarefa 1.0: Domínio de lacunas, porta, adapter de IA e caso de uso IdentificarLacunasDaVaga

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Cria o núcleo da etapa de perguntas: o que é uma lacuna, a porta de IA que as identifica e o caso de uso que limita a 5 e nunca bloqueia a geração.

<requirements>
- `LacunaDaVaga(tema, pergunta)` e `HistoricoDoCandidato(resumo, experiencias, tecnologias)` em `curriculo/domain/lacuna_da_vaga.py`; tema e pergunta não vazios.
- `principais(lacunas, limite=5)` remove duplicatas de tema e corta no limite, sem depender de a IA obedecer.
- `IdentificadorLacunasPort` em `identificador_lacunas_port.py`.
- `IdentificadorLacunasOpenAIClient`: prompt com vaga, cargo-alvo e histórico (incluindo conquistas); pede temas centrais (práticas, tipo de atuação), exclui o que o histórico sustenta, ordena por centralidade e devolve perguntas fechadas.
- `IdentificarLacunasDaVaga` em `curriculo/service_layer/identificar_lacunas_da_vaga/` com `executar`; `RuntimeError` ou `ValueError` da IA vira tupla vazia com log de aviso; histórico sem experiências devolve vazio sem chamar a IA.
- Sem importar o `model` do domínio `perfil_estruturado`.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 1.1 Escrever os testes de `LacunaDaVaga` e `principais` (red); implementar (green).
- [x] 1.2 Declarar a porta e o `HistoricoDoCandidato`.
- [x] 1.3 Escrever os testes de `IdentificarLacunasDaVaga` (red): limite de 5, falha da IA, histórico vazio.
- [x] 1.4 Implementar o caso de uso, o DTO e o `__init__` (green).
- [x] 1.5 Escrever os testes do prompt do adapter (red) e implementar o adapter (green), incluindo a resposta fora do formato levantando `ValueError`.
- [x] 1.6 Refatorar e rodar os testes de `curriculo`.

## Detalhes de Implementação

Techspec: "Interfaces Principais", "Pontos de Integração" (lacunas) e "Decisões Principais" (falha vira sem lacunas, domínio recebe `HistoricoDoCandidato`). PRD: RF 1 a 4.

## Critérios de Sucesso

- Nunca mais de 5 lacunas, sem tema repetido.
- Falha da IA não impede o fluxo.
- Nenhuma regressão nos testes de `curriculo`.

## Testes da Tarefa

- [x] Testes de unidade do domínio, do caso de uso e do adapter (cliente falso).
- [x] Regressão: `src/jobsync/tests/curriculo/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/lacuna_da_vaga.py (novo)`
- `src/jobsync/curriculo/domain/identificador_lacunas_port.py (novo)`
- `src/jobsync/curriculo/adapters/identificador_lacunas_openai_client.py (novo)`
- `src/jobsync/curriculo/service_layer/identificar_lacunas_da_vaga/ (novo)`
- `src/jobsync/curriculo/__init__.py`

## Resultado da execução

- `LacunaDaVaga`, `HistoricoDoCandidato` e `principais` (limite 5, sem tema repetido) em `curriculo/domain/lacuna_da_vaga.py`; porta `IdentificadorLacunasPort`, adapter `IdentificadorLacunasOpenAIClient` e caso de uso `IdentificarLacunasDaVaga` (falha da IA vira lista vazia com aviso; sem experiências não chama a IA).
- A normalização de texto virou `shared_kernel/domain/texto_normalizado.py`, reutilizada pelo banco de conquistas (JOB-0042), porque os domínios não podem se importar.
- O prompt omite a linha de requisitos técnicos quando a análise da vaga está vazia.
