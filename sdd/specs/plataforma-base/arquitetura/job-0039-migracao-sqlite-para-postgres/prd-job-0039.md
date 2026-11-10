# Documento de Requisitos de Produto (PRD) — JOB-0039

- **Código**: `job-0039`
- **Módulo**: `plataforma-base`
- **Subsistema**: `arquitetura`
- **Status**: Rascunho

## Visão Geral

O job-sync guarda hoje todos os dados (perfis, tokens de captura, vagas, candidaturas, currículos salvos e perfis estruturados) em um único arquivo SQLite, `storage/job_sync.db`. Este PRD define a troca desse banco por PostgreSQL, sem perder nenhum dado já cadastrado e sem mudar o que o candidato vê e faz no produto.

Analogia: hoje os dados ficam em uma pasta de arquivo dentro da casa do app. A migração leva tudo para um arquivo central, com portaria e controle de acesso (o servidor Postgres). O conteúdo da pasta precisa chegar inteiro, e o candidato não deve notar a mudança de endereço.

Premissa (a confirmar nas questões em aberto): a motivação é adotar um banco de servidor, mais adequado a vários acessos simultâneos e a uma operação além da máquina local. Esta motivação não consta no repositório.

## Objetivos

- Executar o produto inteiro sobre PostgreSQL.
- Levar 100% dos dados atuais do SQLite para o PostgreSQL.
- Manter o comportamento visível: nenhuma tela, endpoint ou regra de negócio muda.
- Tornar a troca reversível: o arquivo SQLite original continua intacto até o candidato decidir descartá-lo.

Como medir o sucesso:

- A contagem de registros por tabela é igual no SQLite e no PostgreSQL após a migração.
- Cada PDF de currículo salvo tem o mesmo conteúdo (verificado por hash) nos dois bancos.
- A ordem dos cartões em cada coluna do board é a mesma antes e depois.
- A suíte de testes (unitários, integração e E2E) passa usando PostgreSQL.
- A duração da parada durante a troca é registrada. Não há limite máximo enquanto o sistema não estiver em produção.

## Histórias de Usuário

Persona principal: **candidato** que acompanha candidaturas, vagas capturadas e currículos no job-sync.

Persona secundária: **responsável pela operação** (quem instala, atualiza e faz backup do job-sync).

1. Como candidato, eu quero que todas as minhas candidaturas, vagas e currículos continuem aparecendo depois da troca de banco, para não refazer nenhum cadastro.
2. Como candidato, eu quero que a ordem dos cartões no board continue a mesma, para não perder minha priorização.
3. Como candidato, eu quero que o token da extensão do Chrome continue válido, para não reconfigurar a captura de vagas.
4. Como responsável pela operação, eu quero ver um relatório da migração (registros lidos, gravados e problemas), para saber que nada se perdeu.
5. Como responsável pela operação, eu quero poder executar a migração de teste sem alterar o banco de destino, para ensaiar antes da troca real.
6. Como responsável pela operação, eu quero voltar ao SQLite se algo falhar, para não ficar sem o sistema.
7. Como desenvolvedor, eu quero subir o ambiente local com PostgreSQL por instruções claras no README, para trabalhar sem passos escondidos.

Casos extremos:

- Registro no SQLite que aponta para outro registro inexistente (por exemplo, candidatura com vaga removida).
- Data gravada em formato inesperado.
- Execução da migração duas vezes (a segunda não pode duplicar nem sobrescrever dados).
- Falha no meio da migração (o destino não pode ficar pela metade).
- PostgreSQL indisponível ou com credencial errada na subida da API.

## Funcionalidades Principais

### F1. Persistência em PostgreSQL

Todas as seis áreas de dados passam a ser lidas e gravadas no PostgreSQL.

Requisitos funcionais:

1. RF-01: O sistema deve ler e gravar perfis, tokens de captura, vagas, candidaturas, currículos salvos e perfis estruturados no PostgreSQL.
2. RF-02: O comportamento de todos os endpoints existentes deve permanecer igual, incluindo ordenação, filtros e códigos de erro.
3. RF-03: A configuração do banco deve vir de variável de ambiente, sem credenciais no código nem no repositório.
4. RF-04: O sistema deve falhar na inicialização, com mensagem clara, se não conseguir conectar ao PostgreSQL.
5. RF-05: A estrutura do banco (tabelas e colunas) deve ser criada e atualizada de forma controlada e versionada, não a cada abertura de conexão.

### F2. Migração dos dados atuais

Uma ferramenta de linha de comando copia o conteúdo do arquivo SQLite para o PostgreSQL.

Requisitos funcionais:

6. RF-06: A ferramenta deve copiar todas as tabelas, respeitando as dependências entre elas.
7. RF-07: A ferramenta deve preservar os identificadores, a ordem dos cartões nas colunas e o conteúdo binário dos PDFs.
8. RF-08: A ferramenta deve oferecer modo de simulação (dry-run) que lê e valida sem gravar no destino.
9. RF-09: A ferramenta deve gravar tudo ou nada: se algo falhar, nenhuma linha permanece no destino.
10. RF-10: A ferramenta deve recusar a execução quando o destino já tiver dados, para evitar duplicidade.
11. RF-11: A ferramenta deve detectar e relatar inconsistências do SQLite (referências órfãs, datas inválidas) antes de gravar.
12. RF-12: A ferramenta deve produzir relatório final com contagem por tabela (origem e destino) e resultado da validação por hash dos PDFs.
13. RF-13: A ferramenta deve abrir o SQLite somente para leitura, sem alterar o arquivo original.

### F3. Troca e retorno

14. RF-14: Deve existir um roteiro documentado de troca: parar a API, fazer backup do `.db`, migrar, validar e subir a API no PostgreSQL.
15. RF-15: Deve existir um roteiro documentado de retorno ao SQLite por meio da versão anterior do sistema e do backup do arquivo.

## Experiência do Usuário

- O candidato não vê mudança de interface. Só percebe uma indisponibilidade curta durante a troca.
- O responsável pela operação usa o terminal. As mensagens da ferramenta ficam em português, com resumo claro de sucesso ou falha e próximo passo.
- O README e o `.env.example` descrevem o novo modo de configuração e o passo a passo da migração.
- Sem requisitos de acessibilidade novos, pois a interface não muda.

## Restrições Técnicas de Alto Nível

- O PostgreSQL (versão 15.3) está instalado na máquina que executa o sistema, fora do `docker-compose`. O backend roda direto na máquina por enquanto. O uso em container fica para depois, e o backend em container precisará alcançar o Postgres do host.
- O sistema ainda não está em produção, então não há usuários a proteger durante a troca.
- Segredos de conexão não vão para o repositório nem para logs.
- O conteúdo dos currículos (dados pessoais) trafega e fica armazenado apenas no banco do próprio responsável.
- As regras de arquitetura do projeto continuam valendo (hexagonal, domínios isolados, verificadas pelo `import-linter`).
- Os testes de repositório precisam de um PostgreSQL real, inclusive no CI.
- Volume atual de dados: pequeno (uso individual). O número exato de registros será levantado antes da migração.

## Fora de Escopo

- Mudança de regras de negócio, telas ou contratos de API.
- Suporte simultâneo a SQLite e PostgreSQL em produção.
- Sincronização contínua ou dual-write entre os dois bancos.
- Mover PDFs gerados da pasta `storage/` para o banco. Só os PDFs já gravados em `curriculo_salvo` migram.
- Otimizações de performance, índices adicionais e particionamento.
- Alta disponibilidade, réplicas e rotina de backup automatizada do PostgreSQL.
- Autenticação e multiusuário novos.

## Questões em Aberto

1. Qual é a motivação principal da troca (concorrência, deploy fora da máquina local, outra)? Isso ajusta prioridades de teste.
2. Qual o tamanho atual do `job_sync.db` e o número de registros por tabela?
3. Resolvida: o sistema não está em produção, então não há limite de janela de parada por enquanto. Retomar este ponto antes de qualquer uso em produção.
4. As datas atuais são horários locais sem fuso. Mantemos "sem fuso" na migração? A Tech Spec propõe manter e tratar fuso em outra demanda.
5. Quem fará o backup do PostgreSQL após a troca? Fica fora do escopo, mas precisa de responsável.
