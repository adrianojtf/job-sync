# Tarefa 3.0: Identificador de equivalências (porta e adapter)

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Uma chamada de IA por adaptação aponta pares equivalentes entre as tecnologias do perfil e as da vaga.

<requirements>
- `IdentificadorEquivalenciasPort.identificar(experiencias, contexto) -> tuple[EquivalenciaTecnologia, ...]`.
- `IdentificadorEquivalenciasOpenAIClient` com `ClienteOpenAI`: envia descrições das experiências e requisitos explícitos e implícitos da análise.
- Regras do prompt: mesma categoria; original presente no texto; alvo presente na vaga; sem idiomas como tecnologia.
- Resposta `{"equivalencias": [{"original": "...", "alvo": "..."}]}`; formato inválido levanta `ValueError`; lista vazia é válida.
- Dublê determinístico em `app_e2e.py` (ex.: React → Angular quando a vaga cita Angular).
- Complexidade: medium. Dependências: 2.0.
</requirements>

## Subtarefas

- [ ] 3.1 Testes do adapter com mock do `ClienteOpenAI` (Red).
- [ ] 3.2 Porta.
- [ ] 3.3 Adapter e prompt.
- [ ] 3.4 Dublê de E2E.

## Detalhes de Implementação

Ver "`IdentificadorEquivalenciasOpenAIClient`" em "Regras dos prompts" de `techspec-job-0037.md`.

## Critérios de Sucesso

- Prompt contém as regras de categoria e de presença.
- Parse aceita lista vazia e rejeita item sem `original` ou `alvo`.

## Testes da Tarefa

- [ ] Testes de unidade do adapter (prompt, parse, erros).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/identificador_equivalencias_port.py` (novo)
- `src/jobsync/curriculo/adapters/identificador_equivalencias_openai_client.py` (novo)
- `src/jobsync/tests/curriculo/`, `src/jobsync/tests/e2e/app_e2e.py`
