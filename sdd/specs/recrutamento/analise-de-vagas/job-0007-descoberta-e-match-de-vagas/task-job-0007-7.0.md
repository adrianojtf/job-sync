# Tarefa 7.0: Integrar botão "Candidatar" na UI

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Adicionar o botão "Candidatar" em cada vaga da lista da página "Vagas" (Tarefa 6.0). Ao clicar, roda `CandidatarNaVagaExterna`, exibe o PDF adaptado e a carta de apresentação para download, e abre a URL original da vaga em nova aba.

<requirements>
- Botão "Candidatar" em cada item da lista de vagas descobertas.
- Ao clicar: chama `CandidatarNaVagaExterna.executar(...)` com o PDF do currículo já selecionado, os dados da vaga (`VagaExterna`) e o idioma alvo.
- Exibe: botão de download do PDF adaptado, texto da carta de apresentação (copiável), e nota do ATS Score já recalculado.
- Abre `url_vaga` em nova aba via `st.link_button` — sem tentativa de preencher formulários do site de destino (autofill fora de escopo, ver PRD).
- Tratamento de erro: se `CandidatarNaVagaExterna` falhar (ex: PDF inválido), exibir mensagem de erro clara sem quebrar a página.
- Complexidade: low.
</requirements>

## Subtarefas

- [ ] 7.1 Adicionar a composição (`@st.cache_resource`) do `CandidatarNaVagaExterna` com as portas já existentes (currículo, vaga, PDF, carta).
- [ ] 7.2 Adicionar o botão "Candidatar" em cada item da lista de vagas.
- [ ] 7.3 Exibir o resultado (PDF para download, carta de apresentação, ATS Score) e o `st.link_button` para a vaga original.
- [ ] 7.4 Tratar erros de forma amigável na UI.

## Detalhes de Implementação

Consultar a seção "Fluxo de dados do 'Candidatar'" de `techspec-job-0007.md`. Reaproveitar o padrão de exibição de PDF/download já usado na página "Adaptar Currículo".

## Critérios de Sucesso

- Clicar em "Candidatar" gera o PDF adaptado, a carta de apresentação e abre a vaga original em nova aba, sem quebrar a página em caso de erro.

## Testes da Tarefa

- [ ] Validação manual: candidatar-se a uma vaga descoberta real e conferir PDF, carta e abertura da URL original.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/ui/app_streamlit.py`
