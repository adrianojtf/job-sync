# Tarefa 10.0: Ensaio e troca real dos dados

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Tarefa operacional e manual, feita por quem opera o sistema, com o `job_sync.db` real e o Postgres instalado.

<requirements>
- Registrar tamanho do `.db` e contagem por tabela antes da troca.
- Executar `--dry-run` em uma cópia do `.db` real e tratar eventuais problemas relatados.
- Parar a API, fazer backup do `.db`, rodar a migração, conferir o relatório e subir a API com `DATABASE_URL`.
- Conferir no sistema: board com a mesma ordem, currículos salvos com PDF abrindo, perfil estruturado e token da extensão do Chrome válido.
- Registrar o resultado e a duração da parada neste arquivo.
</requirements>

## Subtarefas

- [ ] 10.1 Levantar volumes do banco atual.
- [ ] 10.2 Ensaiar com `--dry-run` em cópia.
- [ ] 10.3 Executar a troca seguindo o roteiro do README.
- [ ] 10.4 Conferir os fluxos principais e registrar o resultado.
- [ ] 10.5 Guardar o `.db` original até a decisão de descartá-lo.

## Detalhes de Implementação

Techspec: "Roteiro de troca" e "Roteiro de retorno". PRD: histórias 1 a 6; questões 2 e 3.

## Critérios de Sucesso

- Contagens e hashes iguais no relatório.
- Duração da parada dentro do limite definido pelo responsável.
- Plano de retorno testado de forma documental (passos conferidos).

## Testes da Tarefa

- [ ] Validação manual dos fluxos listados; não há teste automatizado.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `storage/job_sync.db` (apenas leitura)
- `README.md` (roteiros)
