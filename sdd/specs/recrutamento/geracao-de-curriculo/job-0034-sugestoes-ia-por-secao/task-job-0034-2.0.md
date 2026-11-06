# Tarefa 2.0: Porta MelhoradorTextoCurriculoPort e adapter OpenAI

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar a porta que melhora a escrita de uma seção ou experiência sem vaga-alvo (modo "Meu perfil") e seu adapter OpenAI.

<requirements>
- Porta em `curriculo/domain/melhorador_texto_curriculo_port.py` com `melhorar_secao` e `melhorar_experiencia`.
- Adapter `MelhoradorTextoCurriculoOpenAIClient` seguindo `AjustadorExperienciaOpenAIClient`: mantém idioma, não inventa fatos, preserva bullets "-", resposta em JSON `{"texto_sugerido": ...}`.
- JSON inválido ou resposta vazia levanta erro do provedor.
- Complexidade: medium. Dependências: nenhuma.
</requirements>

## Subtarefas

- [ ] 2.1 Testes do adapter com mock de `ClienteOpenAI` (Red).
- [ ] 2.2 Porta.
- [ ] 2.3 Adapter e prompt.

## Detalhes de Implementação

Ver "Interfaces Principais" (prompt do adapter) em `techspec-job-0034.md`. Referência de teste: `tests/curriculo/test_ajustador_texto_client.py`.

## Critérios de Sucesso

- O prompt contém as regras de não inventar fatos e manter o idioma; a experiência devolvida preserva cargo, empresa e período.

## Testes da Tarefa

- [ ] Testes de unidade do adapter.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/domain/melhorador_texto_curriculo_port.py`
- `src/jobsync/curriculo/adapters/melhorador_texto_curriculo_openai_client.py`
- `src/jobsync/tests/curriculo/test_melhorador_texto_curriculo_openai_client.py`
