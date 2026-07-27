# Tarefa 4.0: Cobrir testes unitários e de integração para português e inglês

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Ampliar e ajustar a cobertura de testes para validar o catálogo de localização, a propagação do idioma alvo e a renderização correta do PDF em português e inglês.

<requirements>
- Cobrir os cenários principais de mapeamento e fallback da camada de localização.
- Validar o fluxo completo de adaptação e geração de PDF com idioma alvo.
- Garantir que os testes cubram o comportamento esperado para os dois idiomas suportados.
</requirements>

## Subtarefas

- [ ] 4.1 Adicionar testes unitários para o catálogo de localização cobrindo pt, en e fallback.
- [ ] 4.2 Atualizar os testes do gerador PDF para validar rótulos, categorias e preservação do conteúdo factual.
- [ ] 4.3 Adicionar testes de integração para o fluxo completo de `AdaptarCurriculoParaVaga` repassando o idioma alvo.

## Detalhes de Implementação

Consultar `prd-job-0003.md` e `techspec-job-0003.md` para alinhar os cenários esperados e os critérios de aceitação das funcionalidades de localização e geração de PDF.

## Critérios de Sucesso

- A suíte de testes cobre os principais cenários de português e inglês.
- O fluxo de geração do PDF é validado sem depender de comportamento manual.
- As alterações são verificadas antes da conclusão da implementação.

## Testes da Tarefa

- [ ] Executar a suíte relevante antes de considerar a tarefa concluída.

## Arquivos relevantes

- `tests/test_catalogo_localizacao.py`
- `tests/test_gerador_pdf.py`
- `tests/` relacionados ao caso de uso de adaptação
