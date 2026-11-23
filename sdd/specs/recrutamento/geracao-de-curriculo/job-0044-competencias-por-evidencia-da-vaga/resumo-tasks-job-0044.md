# Resumo de Tarefas de Implementação de Competências por Evidência da Vaga (JOB-0044)

## Tarefas

- [x] 1.0 `SelecaoDeCompetencias` e `limitar_ao_teto` (domínio puro)
- [x] 2.0 Prompt: tirar a frase "todas as tecnologias" e pôr a lista permitida na instrução de tecnologias
- [x] 3.0 Serviço de adaptação: seleção antes da IA, filtro e teto depois, e `lacunas_tecnologia`
- [x] 4.0 API e tipos: `lacunas_tecnologia` no schema, `schema.d.ts` e Postman
- [x] 5.0 Título "Competências" e "Skills": catálogo, PDF, tela e testes existentes
- [x] 6.0 Aviso das lacunas na revisão
- [ ] 7.0 E2E e fechamento

## Dependências

- 1.0 e 5.0 não dependem de nenhuma outra tarefa e podem ser feitas em paralelo.
- 2.0 depende da 1.0.
- 3.0 depende de 1.0 e 2.0.
- 4.0 depende da 3.0.
- 6.0 depende da 4.0.
- 7.0 depende de 3.0, 5.0 e 6.0.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | `SelecaoDeCompetencias` e `limitar_ao_teto` | low | — | Seleção, lacunas, equivalência, teto e ordem. |
| 2.0 | Prompt sem a frase obrigatória e com a lista permitida | medium | 1.0 | `test_ajustador_texto_client`. |
| 3.0 | Serviço de adaptação com filtro, teto e lacunas | high | 1.0, 2.0 | Serviço com fakes. |
| 4.0 | API e tipos de `lacunas_tecnologia` | low | 3.0 | Schema e router. |
| 5.0 | Título "Competências" e "Skills" | low | — | Catálogo, PDF e telas. |
| 6.0 | Aviso das lacunas na revisão | low | 4.0 | Vitest. |
| 7.0 | E2E e fechamento | medium | 3.0, 5.0, 6.0 | Playwright e suítes completas. |
