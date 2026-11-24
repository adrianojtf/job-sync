# Tarefa 4.0: Reconhecedor de blocos, porta de IA, cliente OpenAI e EstruturarExperienciaService

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Reconhece os quatro blocos no texto da experiência com um parser determinístico e usa a IA só para completar os blocos ausentes, sem reescrever o reconhecido.

<requirements>
- `BlocosExperiencia` (VO, blocos parciais ou completos) e `ReconhecedorBlocosExperiencia` em `perfil_estruturado/domain/blocos_experiencia.py`, usando os rótulos do `shared_kernel` (pt e en, apelidos).
- `CompletadorBlocosExperienciaPort.completar(experiencia, idioma) -> BlocosExperiencia`; o cliente `CompletadorBlocosExperienciaOpenAIClient` fica em `adapters`.
- `EstruturarExperienciaService.executar(experiencia, idioma)`: reconhece, chama a porta só se faltar bloco, junta (o reconhecido prevalece); falha da IA devolve os reconhecidos e os demais vazios, com aviso.
- Prompt: completar sem alterar o existente; 3 a 5 itens por lista; contexto de 1 a 3 frases; métricas e contextos realistas para o setor e o papel, preferindo dados da fonte; no idioma do texto.
- Resposta fora do formato é rejeitada com erro claro.
- Log sem texto de currículo: `Experiencias estruturadas (total, reconhecidas, completadas_pela_ia)`.
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 4.1 Escrever os testes do reconhecedor, do service (porta fake) e do cliente (red).
- [x] 4.2 Implementar o reconhecedor e os VOs (green).
- [x] 4.3 Implementar a porta, o service e o cliente OpenAI (green).
- [x] 4.4 Refatorar e rodar `tests/perfil_estruturado`.

## Detalhes de Implementação

Techspec: "Visão Geral dos Componentes", "Interfaces Principais", "Pontos de Integração" e "Decisões Principais" (parser antes da IA). PRD: RF 6 a 9.

Complexidade: high. Dependências: 1.0, 2.0.

## Critérios de Sucesso

- Os blocos do exemplo da Starian (Context, Key Responsibilities, Key Achievements, Technologies) são reconhecidos sem chamar a IA.
- Nenhum bloco reconhecido é alterado pela IA.
- Falha da IA não perde o que foi reconhecido.

## Testes da Tarefa

- [x] Testes de `TestReconhecedorBlocosExperiencia` (pt, en, apelidos, sem rótulo, parciais).
- [x] Testes de `TestEstruturarExperienciaService` com porta fake.
- [x] Testes do cliente com `ClienteOpenAI` mockado (formato inválido e limites).
- [x] Regressão: `src/jobsync/tests/perfil_estruturado/`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/perfil_estruturado/domain/blocos_experiencia.py (novo)`
- `src/jobsync/perfil_estruturado/domain/completador_blocos_experiencia_port.py (novo)`
- `src/jobsync/perfil_estruturado/domain/estruturar_experiencia_service.py (novo)`
- `src/jobsync/perfil_estruturado/adapters/completador_blocos_experiencia_openai_client.py (novo)`
- `src/jobsync/shared_kernel/domain/rotulos_blocos_experiencia.py`
- `src/jobsync/tests/perfil_estruturado/ (testes novos)`
