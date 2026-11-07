# Resumo de Tarefas de Implementação de Conquistas e Contexto nas Experiências (JOB-0035)

## Tarefas

- [x] 1.0 ExperienciaAdaptada e refatoração do rascunho
- [x] 2.0 Porta de ajuste, adapter e adaptação
- [x] 3.0 Gerador de PDF e prompt da fonte PDF
- [x] 4.0 Casos de uso de sugestão
- [x] 5.0 API
- [x] 6.0 Cliente de API e tipos
- [x] 7.0 SugestaoIA genérico e formulário
- [x] 8.0 Tela de revisão
- [x] 9.0 E2E, acessibilidade e suíte completa

## Dependências

- Backend: 1.0 → 2.0 e 3.0 (em paralelo) → 4.0 → 5.0.
- Frontend: 6.0 (depende de 5.0) → 7.0 → 8.0 → 9.0.

## Decisões adotadas

- Contratos: a task 5.0 só soma os campos novos (`conquistas`, `contexto` e o endpoint `/experiencias-adaptadas/sugestoes`). Os legados (`descricao` e `contexto_vaga`) saem na task 8.0, depois que o frontend migrar, para o frontend, os tipos gerados e o E2E ficarem verdes a cada task.
- Faixa de conquistas: de 2 a 6 no prompt; o domínio exige ao menos uma.
- `contexto_vaga` removido de `/experiencias-profissionais/sugestoes`.
- Fonte PDF incluída por convenção de texto (task 3.0).
- Métricas estimáveis pela IA, com aviso fixo na revisão (decisão de produto).
- Regenerar o `schema.d.ts` com Python 3.12, o mesmo do CI.

## Desvios em relação à Tech Spec

- **Contratos em duas etapas:** a task 5.0 só somou `conquistas`, `contexto` e o endpoint `/experiencias-adaptadas/sugestoes`; a task 8.0 removeu os legados (`descricao` do rascunho e `contexto_vaga` do endpoint do perfil). Assim frontend, tipos gerados e E2E ficaram verdes a cada task.
- **Legados rejeitados, não ignorados:** `ExperienciaAdaptadaSchema` e `SugerirAjusteExperienciaRequest` usam `extra="forbid"`. Um cliente antigo recebe 422 em vez de perder o conteúdo da experiência em silêncio.
- **Ponte provisória das tasks 2.0 a 7.0:** conquistas e contexto foram achatados em texto no schema do rascunho e na sugestão da JOB-0034. Removida na task 8.0.
- **Prompt de sistema do ajuste de texto:** deixou de proibir "inventar resultado", que contradizia a estimativa de métricas permitida nas experiências.
- **Sugestão da experiência:** componente próprio na feature de revisão (`SugestaoExperienciaAdaptada`), sem lógica da feature no hook compartilhado.

## Validação realizada

- Backend: 486 testes de pytest. Frontend: 217 testes de Vitest, lint, `tsc` e build. E2E e acessibilidade (Playwright). Contrato (`schema.d.ts`) idêntico ao gerado com Python 3.12, o do CI.
- PDF real, pela API: o rascunho devolvido por `/rascunhos-adaptados` é aceito como veio por `/curriculos-revisados`; o PDF traz as conquistas e o contexto editados (e não o texto bruto da IA), com o rótulo do idioma e o contexto em fonte oblíqua cinza.
- PDF real, pela interface: edição de conquistas e contexto na revisão, confirmação e download; texto, fonte (`Helvetica-Oblique`) e cor (`#666666`) conferidos com `pdfplumber` (passada manual, não automatizada).

## Pontos em aberto

- **IA real não validada:** todos os testes usam dublês. Não se sabe se o modelo segue o formato (2 a 6 conquistas, contexto de 1 a 3 frases, linha `Contexto:` na fonte PDF) nem como estima números.
- **Números estimados:** a única proteção é o aviso fixo na revisão.
- **Tecnologias da vaga nas experiências:** o prompt do usuário do ajuste de texto manda incluir todas as tecnologias da vaga em qualquer seção, o que empurra tecnologias para dentro das conquistas na fonte PDF. Pré-existente, não tratado.
- **Bullets sem recuo:** a segunda linha de um bullet que quebra volta à margem, diferente do exemplo de referência. Pré-existente, não tratado.
