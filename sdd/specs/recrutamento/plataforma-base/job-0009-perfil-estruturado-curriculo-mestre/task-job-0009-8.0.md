# Tarefa 8.0: UI — integrar perfil como fonte padrão em Adaptar/ATS/Candidatar

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Nas três páginas existentes ("Adaptar Currículo", "Analisar ATS", "Vagas" / botão Candidatar), verificar se o usuário tem um perfil estruturado com conteúdo mínimo; se tiver, usar esse perfil diretamente (sem pedir upload de PDF); caso contrário, manter o fluxo atual de upload/biblioteca.

<requirements>
- Criar um helper `_obter_curriculo_do_perfil(repositorio_perfil_estruturado, perfil_identificador) -> Curriculo | None`: busca o perfil (`BuscarPerfilEstruturado`), e se existir, converte via `MontarCurriculoDoPerfilEstruturado`; retorna `None` se o perfil não existir ou não tiver conteúdo mínimo.
- Em cada uma das três páginas: se o helper retornar um `Curriculo`, pular a UI de upload/biblioteca e passar `curriculo_pre_montado=<Curriculo>` ao InputDto correspondente.
- Se o helper retornar `None`, manter o comportamento atual (upload de PDF / biblioteca, passando `pdf_curriculo=...`).
- Indicar visualmente na UI quando o perfil estruturado está sendo usado (ex: `st.caption("Usando dados do seu perfil salvo.")`), para o usuário entender de onde vêm os dados.
- Complexidade: medium (repetir a mesma lógica de decisão em três lugares, com cuidado para não quebrar os fluxos de upload já existentes).
</requirements>

## Subtarefas

- [ ] 8.1 Implementar o helper `_obter_curriculo_do_perfil`.
- [ ] 8.2 Integrar o helper em `_pagina_adaptar_curriculo`, passando `curriculo_pre_montado` quando disponível.
- [ ] 8.3 Integrar o helper em `_pagina_analisar_ats`, passando `curriculo_pre_montado` quando disponível.
- [ ] 8.4 Integrar o helper em `_renderizar_vaga_descoberta`/`_pagina_vagas` (fluxo "Candidatar"), passando `curriculo_pre_montado` quando disponível.
- [ ] 8.5 Validar manualmente os dois caminhos em cada página: com perfil preenchido (sem pedir PDF) e sem perfil preenchido (upload continua funcionando como antes).

## Detalhes de Implementação

Consultar a seção "Fluxo de dados — uso do perfil em Adaptar/ATS/Candidatar" de `techspec-job-0009.md`.

## Critérios de Sucesso

- Com perfil preenchido, as três funcionalidades funcionam sem pedir upload de PDF.
- Sem perfil preenchido (ou perfil vazio), as três funcionalidades continuam funcionando exatamente como antes desta fase.

## Testes da Tarefa

- [ ] Validação manual: com perfil preenchido, usar "Adaptar Currículo" sem fazer upload de PDF — deve funcionar usando os dados do perfil.
- [ ] Validação manual: com perfil preenchido, usar "Analisar ATS" e "Candidatar" (Vagas) da mesma forma.
- [ ] Validação manual: sem perfil preenchido, confirmar que as três funcionalidades continuam pedindo upload de PDF como antes.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/ui/app_streamlit.py`
