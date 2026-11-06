# Tarefa 3.0: CatalogoLocalizacao — título "Technical Skills" e rótulo de contexto

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Ajustar os rótulos de apresentação para ficarem iguais ao modelo: o título da seção de tecnologias em inglês passa a ser "Technical Skills", e o catálogo ganha o rótulo de contexto ("Context" / "Contexto").

<requirements>
- `localizar_secao("en", "tecnologias")` deve retornar `Technical Skills`.
- `localizar_secao("pt", "tecnologias")` continua retornando `Tecnologias`.
- Novo método ou chave para o rótulo de contexto: `Context` em inglês e `Contexto` em português, com o mesmo fallback de idioma já existente.
- A conversão para caixa alta fica no gerador de PDF, não no catálogo.
- Sem dependência de infraestrutura (`shared_kernel/domain`).
</requirements>

## Subtarefas

- [ ] 3.1 Atualizar o teste existente em `test_catalogo_localizacao.py:10` para `Technical Skills` (red).
- [ ] 3.2 Escrever testes do rótulo de contexto em pt, en e idioma desconhecido.
- [ ] 3.3 Implementar as mudanças em `CatalogoLocalizacao`.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md` a tabela "Componentes modificados" (linha `CatalogoLocalizacao`).

## Critérios de Sucesso

- Testes do catálogo verdes.
- Teste `test_localiza_titulo_de_secao_para_ingles` do gerador continua verde.

## Testes da Tarefa

- [ ] `Technical Skills` para `en`.
- [ ] `Tecnologias` para `pt`.
- [ ] Rótulo de contexto em `en`, `pt` e fallback.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/shared_kernel/domain/catalogo_localizacao.py`
- `src/jobsync/tests/shared_kernel/test_catalogo_localizacao.py`
