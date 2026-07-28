# Tarefa 4.0: Implementar adapter GeradorCartaApresentacaoGroq

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o adapter que gera o texto da carta de apresentação via API Groq, reaproveitando `ClienteGroq` e seguindo o mesmo padrão estrutural de `infrastructure/llm/ajustador_texto_groq.py` (prompt de sistema + prompt de usuário estruturado com a análise de vaga).

<requirements>
- Implementar `GeradorCartaApresentacaoPort.gerar(curriculo, analise_vaga, idioma_alvo) -> str`.
- O prompt deve incluir a `AnaliseVaga` estruturada (requisitos explícitos/implícitos) e o conteúdo do `Curriculo`, nunca inventando fatos não presentes no currículo original (PRD, requisito funcional 6).
- A carta deve ser gerada no idioma alvo (`pt`/`en`), reaproveitando o mapeamento de nomes de idioma já usado em `ajustador_texto_groq.py`.
- Resposta da IA deve ser JSON estrito (mesmo padrão de `ClienteGroq.solicitar_json`) — complexidade: medium.
</requirements>

## Subtarefas

- [x] 4.1 Criar `infrastructure/llm/gerador_carta_apresentacao_groq.py` com a classe `GeradorCartaApresentacaoGroq`, recebendo `ClienteGroq` no construtor.
- [x] 4.2 Montar o prompt de sistema e de usuário incluindo currículo (seções relevantes) e análise de vaga estruturada.
- [x] 4.3 Tratar resposta vazia/inválida do modelo levantando `ValueError` claro (mesmo padrão de `AjustadorTextoGroq`).
- [x] 4.4 Escrever testes unitários seguindo o padrão de `tests/infrastructure/llm/test_ajustador_texto_groq.py` (mockando `ClienteGroq`).

## Detalhes de Implementação

Consultar a seção "Decisões Principais" de `techspec-job-0005.md`: a carta é gerada via IA (não template estático), reaproveitando o padrão de prompt já validado em `AjustadorTextoGroq`. Usar `infrastructure/llm/ajustador_texto_groq.py` como referência direta de estrutura de código.

## Critérios de Sucesso

- O adapter gera uma carta coerente com currículo e vaga fornecidos, no idioma correto.
- Resposta inválida/vazia do modelo gera erro claro, não exceção genérica.

## Testes da Tarefa

- [x] Teste unitário: prompt enviado ao `ClienteGroq` inclui requisitos explícitos e implícitos da `AnaliseVaga`.
- [x] Teste unitário: idioma alvo é refletido na instrução de idioma do prompt.
- [x] Teste unitário: resposta vazia do modelo levanta `ValueError`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `infrastructure/llm/gerador_carta_apresentacao_groq.py`
- `tests/infrastructure/llm/test_gerador_carta_apresentacao_groq.py`
