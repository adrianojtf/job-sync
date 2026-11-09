# Tarefa 1.0: Regra do limite de currículos no domínio curriculo_salvo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Hoje a regra do limite de 10 currículos por perfil vive dentro do caso de uso `SalvarCurriculo`. O caso de uso novo (tarefa 3.0) precisa da mesma regra. Esta tarefa leva a regra para o domínio, para existir em um único lugar.

<requirements>
- Criar `curriculo_salvo/domain/limite_curriculos_salvos.py` com `LIMITE_CURRICULOS_POR_PERFIL = 10`, a exceção `LimiteCurriculosSalvosExcedido` (continua subclasse de `ValueError`) e `garantir_espaco(quantidade_atual: int) -> None`.
- `garantir_espaco` levanta a exceção quando `quantidade_atual >= LIMITE_CURRICULOS_POR_PERFIL`, com a mesma mensagem de hoje.
- `SalvarCurriculo` passa a usar `garantir_espaco`, sem mudar comportamento nem mensagem.
- `curriculo_salvo/service_layer/salvar_curriculo/__init__.py` continua exportando `LIMITE_CURRICULOS_POR_PERFIL` e `LimiteCurriculosSalvosExcedido` (o Streamlit importa daqui).
- O domínio não importa nada de infraestrutura.
</requirements>

## Subtarefas

- [ ] 1.1 Escrever os testes de `garantir_espaco` (red).
- [ ] 1.2 Criar o módulo de domínio com a constante, a exceção e a função.
- [ ] 1.3 Fazer `SalvarCurriculo` usar a regra do domínio e reexportar os nomes.
- [ ] 1.4 Confirmar que os testes existentes de `SalvarCurriculo` e o import do Streamlit continuam válidos.

## Detalhes de Implementação

Consultar em `techspec-job-0037.md` as seções "Componentes" (linhas de `curriculo_salvo`) e "Interfaces Principais".

## Critérios de Sucesso

- Existe uma única definição do limite e da exceção.
- Nenhum teste existente de `SalvarCurriculo` precisa mudar de expectativa.

## Testes da Tarefa

- [ ] `garantir_espaco` com 9 currículos não levanta.
- [ ] `garantir_espaco` com 10 currículos levanta `LimiteCurriculosSalvosExcedido` com a mensagem atual.
- [ ] `LimiteCurriculosSalvosExcedido` continua sendo `ValueError`.
- [ ] `SalvarCurriculo` continua recusando o 11º currículo e aceitando até o 10º.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo_salvo/domain/limite_curriculos_salvos.py` (novo)
- `src/jobsync/curriculo_salvo/service_layer/salvar_curriculo/service.py`
- `src/jobsync/curriculo_salvo/service_layer/salvar_curriculo/__init__.py`
- `src/jobsync/tests/curriculo_salvo/`
- `src/jobsync/entrypoints/streamlit_app.py` (referência: importa a exceção)
