# Tarefa 5.0: Telas Meu perfil (T3) e Meus currículos (T4)

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Entregar as duas telas que alimentam os demais fluxos com currículo: o currículo mestre (perfil estruturado) e a biblioteca de PDFs.

- **Complexidade:** high
- **Dependências:** 4.0

<requirements>
- Meu perfil: dados pessoais, resumo, experiências, formações, certificações, idiomas (níveis BASICO a NATIVO) e tecnologias, com adicionar e remover itens (RF4.1).
- Perfil inexistente (404): formulário vazio com orientação, não erro.
- Importar de PDF novo ou de um currículo da biblioteca, pré-preencher e só salvar depois da revisão (RF4.2).
- Salvar via `POST /v1/perfil-estruturado` ou `PUT /v1/perfil-estruturado/{id}` e confirmar com toast (RF4.3).
- Avaliar uma experiência contra uma descrição de vaga com `POST /v1/experiencias-profissionais/avaliacoes`, mostrando score e dimensões (RF4.4).
- Meus currículos: listar, enviar PDF com nome de referência (máx. 5 MB), baixar e remover com confirmação (RF5.1 a RF5.3).
- Informar o limite de 10 currículos antes do upload. A regra final continua no backend.
</requirements>

## Subtarefas

- [ ] 5.1 Escrever os testes do formulário (red) com `react-hook-form` e `useFieldArray`.
- [ ] 5.2 Implementar `features/perfil/` (formulário, salvar, estado vazio).
- [ ] 5.3 Implementar a importação de PDF com revisão.
- [ ] 5.4 Implementar a avaliação de experiência com `ScoreDimensions`.
- [ ] 5.5 Escrever os testes (red) e implementar `features/curriculos/`.

## Detalhes de Implementação

Ver `prd-job-0015.md` → F4 e F5, e `techspec-job-0015.md` → "Endpoints de API" (linhas T3 e T4) e "Riscos Conhecidos" (limite de 5 MB). Referência funcional: `_pagina_meu_perfil` e `_renderizar_biblioteca_curriculos` em `streamlit_app.py`.

## Critérios de Sucesso

- Um perfil salvo na nova UI aparece igual no Streamlit, e o contrário também.
- Importar um PDF pré-preenche todas as seções reconhecidas.
- Baixar um currículo gera o mesmo arquivo enviado.

## Testes da Tarefa

- [ ] Testes de unidade: adicionar e remover experiência e enviar o payload esperado (MSW).
- [ ] Testes de unidade: 404 mostra o estado vazio; importar preenche o formulário sem salvar.
- [ ] Testes de unidade: upload bloqueado com 10 currículos ou arquivo > 5 MB; remover pede confirmação e invalida a lista.
- [ ] Testes de unidade: avaliação de experiência mostra as 4 dimensões.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/perfil/` (novo)
- `frontend/src/features/curriculos/` (novo)
- `src/jobsync/entrypoints/api/routers/perfil_estruturado_router.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/streamlit_app.py` (referência)
