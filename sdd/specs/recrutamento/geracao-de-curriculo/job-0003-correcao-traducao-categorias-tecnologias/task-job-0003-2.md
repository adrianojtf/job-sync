# Tarefa 2.0: Adaptar o fluxo de geração de PDF para repassar o idioma alvo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Ajustar a interface de geração de PDF e o caso de uso de adaptação do currículo para que o idioma alvo seja repassado ao gerador no momento da geração do PDF.

<requirements>
- Estender a porta de geração de PDF para receber o idioma alvo.
- Atualizar o caso de uso `AdaptarCurriculoParaVaga` para encaminhar `idioma_alvo` ao gerador.
- Manter a compatibilidade do fluxo atual sem reestruturar o domínio.
</requirements>

## Subtarefas

- [x] 2.1 Atualizar a assinatura da porta `GeradorPdfPort` para receber o idioma alvo.
- [x] 2.2 Adaptar o caso de uso `AdaptarCurriculoParaVaga` para repassar `solicitacao.idioma_alvo` ao gerador.
- [x] 2.3 Revisar impactos em implementações alternativas da porta e em testes existentes.

## Detalhes de Implementação

Consultar `prd-job-0003.md` e `techspec-job-0003.md` para confirmar a integração esperada entre aplicação, porta e uso do idioma no pipeline de geração de PDF.

## Critérios de Sucesso

- O idioma alvo é repassado em todo o fluxo de geração de PDF.
- A alteração não introduz regressões no processo atual de adaptação.
- A assinatura do fluxo fica alinhada com a Tech Spec.

## Testes da Tarefa

- [x] Testes de integração para o fluxo de adaptação e geração de PDF com idioma alvo.

## Arquivos relevantes

- `application/ports/gerador_pdf_port.py`
- `application/use_cases/adaptar_curriculo_para_vaga.py`
- `tests/` relacionados ao fluxo de geração de PDF
