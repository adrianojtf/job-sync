# Tarefa 3.0: CatalogoLocalizacao — título "Technical Skills"

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Ajustar o rótulo de apresentação para ficar igual ao modelo: o título da seção de tecnologias em inglês passa a ser "Technical Skills".

O rótulo do contexto ("Context" / "Contexto") não entra aqui: o JOB-0035 já o definiu em `curriculo/domain/rotulos_experiencia.py`, e este JOB o reutiliza.

<requirements>
- `localizar_secao("en", "tecnologias")` deve retornar `Technical Skills`.
- `localizar_secao("pt", "tecnologias")` continua retornando `Tecnologias`.
- A conversão para caixa alta fica no gerador de PDF, não no catálogo.
- Nenhum rótulo de contexto no catálogo (fonte única em `rotulos_experiencia.py`).
- Sem dependência de infraestrutura (`shared_kernel/domain`).
</requirements>

## Subtarefas

- [ ] 3.1 Atualizar o teste existente em `test_catalogo_localizacao.py` para `Technical Skills` (red).
- [ ] 3.2 Alterar o rótulo em `CatalogoLocalizacao`.

## Detalhes de Implementação

Consultar em `techspec-job-0016.md` a tabela "Componentes modificados" (linha `CatalogoLocalizacao`).

## Critérios de Sucesso

- Testes do catálogo verdes.
- Teste `test_localiza_titulo_de_secao_para_ingles` do gerador continua coerente com o novo título.

## Testes da Tarefa

- [ ] `Technical Skills` para `en`.
- [ ] `Tecnologias` para `pt`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/shared_kernel/domain/catalogo_localizacao.py`
- `src/jobsync/tests/shared_kernel/test_catalogo_localizacao.py`
- `src/jobsync/tests/curriculo/test_gerador_pdf_client.py`
