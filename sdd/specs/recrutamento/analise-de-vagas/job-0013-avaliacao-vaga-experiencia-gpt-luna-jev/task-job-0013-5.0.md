# Tarefa 5.0: Integrar avaliações ao fluxo de adaptação

<critical>Ler `prd-job-0013.md` e `techspec-job-0013.md` desta pasta antes de iniciar a tarefa.</critical>

## Visão Geral

Integrar Jev ao fluxo existente de adaptação: avaliar a vaga antes do ajuste e, quando a entrada vier de perfil estruturado, manter cada experiência separada para adaptá-la e avaliá-la individualmente.

<requirements>
- Executar a avaliação da descrição de vaga antes de iniciar a adaptação.
- Uma avaliação com score baixo não deve bloquear a adaptação.
- Preservar cargo, empresa, período e limites de cada experiência do perfil estruturado durante ajuste e reconstrução da seção.
- Após a adaptação, avaliar cada experiência separadamente usando a mesma vaga-alvo.
- Para entrada somente em PDF, não executar a avaliação individual automática das experiências.
- Acrescentar os resultados automáticos à resposta da adaptação sem remover ou renomear campos atuais.
- Resolver a questão de comportamento quando Jev estiver indisponível antes de fechar o fluxo.
</requirements>

## Subtarefas

- [x] 5.1 Registrar a política fail-open: prosseguir com a adaptação e sinalizar avaliações Jev indisponíveis.
- [x] 5.2 Carregar as experiências estruturadas no DTO de adaptação preservando seus metadados.
- [x] 5.3 Avaliar a descrição antes do ajuste e incluir o resultado na resposta da adaptação.
- [x] 5.4 Adaptar e avaliar cada experiência estruturada, remontando a seção usada no currículo final.
- [x] 5.5 Atualizar schemas e dependências do endpoint sem alterar o caminho ou remover campos atuais.

## Detalhes de Implementação

Seguir o fluxo descrito em `techspec-job-0013.md`. Não segmentar por heurística a seção de experiências extraída de um PDF. O caso de uso deve receber avaliadores por portas e continuar responsável por orquestrar o fluxo, sem chamar outro Service.

Se uma chamada Jev falhar, continuar a adaptação e retornar os resultados Jev disponíveis com status explícito para as avaliações indisponíveis. Nota baixa também não bloqueia o fluxo.

## Critérios de Sucesso

- A avaliação da vaga acontece antes da primeira alteração do currículo.
- Perfil estruturado resulta em uma avaliação por experiência adaptada, com os metadados preservados.
- PDF continua recebendo a avaliação automática da vaga, mas não avaliação individual das experiências.
- Score baixo ou indisponibilidade do Jev não impedem a adaptação; as avaliações indisponíveis são sinalizadas na resposta.
- A resposta mantém os campos atuais e inclui os novos resultados documentados.

## Testes da Tarefa

- [x] Testes unitários com fakes verificam ordem das chamadas, resultado baixo não bloqueante e uma avaliação por experiência.
- [x] Teste do fluxo com perfil estruturado verifica preservação de cada experiência e montagem do currículo.
- [x] Teste do fluxo PDF verifica que não ocorre avaliação individual automática.
- [x] Testes cobrem a política definida para indisponibilidade do Jev.
- [x] Teste de API verifica compatibilidade dos campos atuais e os novos campos opcionais.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/`
- `src/jobsync/curriculo/domain/curriculo.py`
- `src/jobsync/perfil_estruturado/domain/montar_curriculo_do_perfil_estruturado_service.py`
- `src/jobsync/entrypoints/api/routers/curriculo_router.py`
- `src/jobsync/entrypoints/api/schemas/curriculo.py`
- Testes de adaptação e de perfil estruturado
