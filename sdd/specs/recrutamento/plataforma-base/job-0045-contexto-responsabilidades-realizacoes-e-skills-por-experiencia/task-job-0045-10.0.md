# Tarefa 10.0: E2E e avaliação manual com o exemplo da Starian

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Valida o fluxo completo no navegador e a qualidade do conteúdo gerado pela IA, que testes automatizados não medem.

<requirements>
- Playwright: importar um currículo com blocos, editar skills, salvar, adaptar a uma vaga e arrastar uma tag entre categorias; ajustar `frontend/e2e/apoio.ts` se preciso.
- Avaliação manual com chaves reais de IA, sem teste automatizado de qualidade.
- Roteiro com o exemplo da Starian: blocos reconhecidos saem idênticos no PDF; blocos ausentes são gerados de forma realista; rótulos em pt e en.
- Registrar o tempo da importação com várias experiências (aviso atual de até 1 minuto).
- Testes seguem `.windsurf/rules/testing-rules.md` (TDD, Arrange/Act/Assert).
</requirements>

## Subtarefas

- [x] 10.1 Escrever o teste E2E do fluxo principal.
- [x] 10.2 Rodar o E2E e corrigir os ajustes de apoio.
- [ ] 10.3 Executar o roteiro manual e registrar o resultado (depende de `OPENAI_API_KEY`, ver Status).
- [x] 10.4 Registrar as questões em aberto restantes do PRD.

## Detalhes de Implementação

Techspec: "Testes de Serviço" e "Riscos Conhecidos". PRD: Objetivos e Questões em Aberto.

Complexidade: low. Dependências: 8.0, 9.0.

## Critérios de Sucesso

- O fluxo E2E passa.
- O roteiro manual confirma fidelidade do reconhecido, realismo do gerado e tempo aceitável.

## Testes da Tarefa

- [x] Playwright em `frontend/e2e`.
- [ ] Avaliação manual com chaves reais (ver Status).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `frontend/e2e/apoio.ts`
- `frontend/e2e/ (spec novo)`
- `src/jobsync/tests/e2e/app_e2e.py`

## Roteiro executável

O arquivo `avaliar-blocos.py`, nesta pasta, usa o `EstruturarExperienciaService` e o `CompletadorBlocosExperienciaOpenAIClient` reais com o exemplo da Starian do PRD. Faz três verificações: (1) o texto completo é reconhecido nos quatro blocos, sem IA e sem alterações; (2) com só a linha `Technologies:`, a IA completa os outros três blocos e as skills reconhecidas ficam intactas; (3) seis experiências em paralelo, para medir a latência dentro do aviso de até 1 minuto.

```bash
PYTHONPATH=src python sdd/specs/recrutamento/plataforma-base/job-0045-contexto-responsabilidades-realizacoes-e-skills-por-experiencia/avaliar-blocos.py
```

## Status

**E2E (Playwright), executado:** a suíte inteira passou contra a API real com PostgreSQL e dublês só nas portas de IA (57 testes). Os dois fluxos novos estão em `frontend/e2e/quatro-blocos.spec.ts`:

- perfil antigo: estruturar as experiências, editar skills em tags, salvar e ver as tecnologias incluídas (`Perfil salvo. Tecnologias incluídas pelas skills: Flyway, Kafka.`), com recarga da página;
- currículo adaptado: quatro blocos na revisão e arrastar uma tag de uma categoria para outra com o mouse.

Também ajustei o E2E existente "ajustar para uma vaga" (a experiência nova usa "Principais responsabilidades" no lugar de "Descrição").

**Roteiro de avaliação manual, parcialmente validado:** com `--dry-run` (IA simulada), a verificação 1 usa o exemplo real da Starian e o resultado sai idêntico, sem chamar a IA (0 chamadas, descrição restante vazia). As verificações 2 e 3 só foram validadas com a IA simulada.

**Avaliação de qualidade com a IA real, não executada pela IA:** o ambiente de desenvolvimento não tem `OPENAI_API_KEY`. Preencha a tabela após a execução local.

| Verificação | Resultado esperado | Resultado | Latência |
|-------------|--------------------|-----------|----------|
| 1. Reconhecimento (Starian completo) | Quatro blocos idênticos ao texto; 0 chamadas à IA | OK (validado, sem IA) | n/a |
| 2. Geração a partir só das skills | 3 a 5 itens por lista, contexto de 1 a 3 frases, skills reconhecidas intactas, números realistas | | |
| 3. Seis experiências em paralelo | Menos de 60 s | | |

## Questões em aberto do PRD (situação)

- Questão 1 (realizações e banco de conquistas): implementado como a mesma lista (`conquistas`); falta só a confirmação do produto.
- Questão 2 (limites): implementado como 3 a 5 itens nas listas e 1 a 3 frases no contexto, na geração pela IA (não são invariante do domínio).
- Questão 3 (números estimados): o aviso aparece na importação, na migração e na revisão; marcar por item continua fora de escopo.
- Questão 5 (migração): a adaptação direta de um perfil antigo segue pela descrição; a estruturação é um passo explícito do usuário em Meu perfil.
