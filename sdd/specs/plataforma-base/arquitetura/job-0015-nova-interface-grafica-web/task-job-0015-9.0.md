# Tarefa 9.0: Tela Visão geral (T2)

<critical>Ler os arquivos prd-job-0015.md e techspec-job-0015.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Entregar o painel inicial do protótipo, que resume a busca do candidato em uma tela só. Os indicadores são calculados no cliente a partir das listas já existentes, sem endpoint novo.

- **Complexidade:** medium
- **Dependências:** 5.0, 7.0

<requirements>
- Saudação com o nome do perfil estruturado (ou o identificador) e a data atual (RF3.1).
- Indicadores: currículos salvos, vagas salvas, candidaturas ativas (Aplicado + Entrevista) e em Entrevista/Oferta (RF3.2). Sem "Compatibilidade média".
- "Vagas recentes": últimas vagas e candidaturas com status e link (RF3.3).
- Card "Currículo principal" com completude (7 seções) e botão "Editar currículo" (RF3.4).
- Card de dica com o fluxo sugerido (RF3.5).
- "Atividade recente" derivada de `data_captura`, `data_upload` e `historico_status` (RF3.6).
- Botão "Ajustar para uma vaga" abre o modal da tarefa 6.0 (RF3.7).
- Primeiro acesso: estado vazio "Complete seu currículo mestre".
- `montarResumo` e `calcularCompletude` como funções puras.
</requirements>

## Subtarefas

- [x] 9.1 Escrever os testes (red) e implementar `montarResumo` e `calcularCompletude`.
- [x] 9.2 Implementar os indicadores com `StatCard`.
- [x] 9.3 Implementar "Vagas recentes", o card do currículo e o card de dica.
- [x] 9.4 Implementar "Atividade recente" e o estado vazio.

## Detalhes de Implementação

Ver `prd-job-0015.md` → F3 e `techspec-job-0015.md` → "Modelos de Dados" (`ResumoVisaoGeral`, `Atividade`, `CompletudePerfil`). Layout de referência: seções `.stats`, `.layout` e `.activity` do protótipo.

## Critérios de Sucesso

- Os números batem com as telas de origem para o mesmo perfil.
- Layout responsivo em 1280px, 1000px e 375px, como no protótipo.
- Perfil novo vê o estado vazio com o próximo passo.

## Testes da Tarefa

- [x] Testes de unidade: `montarResumo` com listas vazias e com dados; atividades ordenadas da mais recente para a mais antiga.
- [x] Testes de unidade: `calcularCompletude` com 0, parcial e 7 seções.
- [x] Testes de unidade: o botão principal abre o modal de Ajustar para uma vaga.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/src/features/visao-geral/` (novo)
- `sdd/prototipos/carreira_saas_prototipo.html`
- `frontend/src/features/ajustar-vaga/`
