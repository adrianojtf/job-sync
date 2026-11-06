# Tarefa 6.0: Telas Ajustar para uma vaga (T5) e Analisar ATS (T6)

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Entregar o fluxo de maior valor do produto: a partir de uma vaga, avaliar a descrição, gerar o currículo adaptado, ver a nota ATS e gerar a carta. Inclui também o diagnóstico rápido de ATS sem gerar PDF.

- **Complexidade:** high
- **Dependências:** 5.0

<requirements>
- Modal "Ajustar para uma vaga" igual ao protótipo (título, empresa, descrição) mais idioma (pt/en) e fonte do currículo (perfil estruturado ou biblioteca) (RF6.1).
- Validação: título e descrição obrigatórios (comportamento do protótipo).
- "Analisar vaga": `POST /v1/vagas/avaliacoes` com score e 4 dimensões (RF6.2).
- "Gerar currículo adaptado": `POST /v1/curriculos/{id}/adaptacoes`, download do PDF e avaliações por experiência (RF6.3).
- Na mesma tela: `POST /v1/curriculos/{id}/analises-ats` (nota, requisitos faltantes, sugestões) e `POST /v1/cartas-apresentacao` com copiar e baixar (RF6.4).
- Aceitar dados pré-preenchidos via estado de navegação, para as tarefas 7.0 e 8.0 (RF6.5).
- `status_avaliacao_vaga = indisponivel`: aviso informativo, sem bloquear.
- Mensagens de progresso por etapa e aviso "pode levar até 1 minuto".
- Analisar ATS (T6): fonte do currículo e descrição (colada ou de uma vaga salva), sem gerar PDF (RF7.1).
</requirements>

## Subtarefas

- [x] 6.1 Escrever os testes do modal (red) e implementá-lo em `features/ajustar-vaga/`.
- [x] 6.2 Implementar o hook `useAjustarVaga` e a página de resultado.
- [x] 6.3 Implementar os blocos de avaliação da vaga, das experiências, ATS e carta.
- [x] 6.4 Implementar o pré-preenchimento via estado de navegação.
- [x] 6.5 Implementar `features/analisar-ats/`.

## Detalhes de Implementação

Ver `prd-job-0015.md` → F6 e F7, e `techspec-job-0015.md` → "Interfaces Principais" (`useAjustarVaga`) e "Pontos de Integração" (timeouts e tratamento de erros). Referência funcional: `_pagina_adaptar_curriculo` e `_pagina_analisar_ats` em `streamlit_app.py`.

## Critérios de Sucesso

- Do modal preenchido até o download do PDF em no máximo 4 cliques (métrica do PRD).
- PDF baixado com o `nome_arquivo` retornado pela API.
- Falha de IA mostra toast com "Tentar novamente" e mantém os dados digitados.

## Testes da Tarefa

- [x] Testes de unidade: modal bloqueia envio sem título ou descrição e fecha com `Esc`.
- [x] Testes de unidade: avaliação mostra score e 4 dimensões; `indisponivel` mostra aviso e permite seguir.
- [x] Testes de unidade: gerar dispara o download; ATS lista requisitos faltantes; carta pode ser copiada.
- [x] Testes de unidade: Analisar ATS com descrição de vaga salva.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/ajustar-vaga/` (novo)
- `frontend/src/features/analisar-ats/` (novo)
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/api/routers/vaga_router.py`
- `src/jobsync/entrypoints/api/schemas/curriculo.py`, `vaga.py`, `avaliacao.py`
