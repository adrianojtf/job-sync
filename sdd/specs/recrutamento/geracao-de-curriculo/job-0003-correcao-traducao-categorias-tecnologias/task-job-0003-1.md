# Tarefa 1.0: Definir catálogo de localização e fallback

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Criar uma camada centralizada de localização para os textos de apresentação usados na geração do currículo, incluindo mapeamentos mínimos para português e inglês e um fallback previsível para idiomas não mapeados.

<requirements>
- Definir os rótulos de seções e categorias de tecnologia esperados para pt e en.
- Garantir que idiomas desconhecidos utilizem fallback consistente.
- Preservar rótulos não mapeados sem alterar o conteúdo factual do currículo.
</requirements>

## Subtarefas

- [ ] 1.1 Definir o catálogo de seções e categorias de tecnologia para português e inglês com base no PRD e na Tech Spec.
- [ ] 1.2 Implementar o mecanismo de fallback para idioma desconhecido e para rótulos não mapeados.
- [ ] 1.3 Documentar o contrato da camada de localização para uso pelo gerador de PDF.

## Detalhes de Implementação

Consultar `prd-job-0003.md` e `techspec-job-0003.md` para alinhar os textos esperados e os pontos de integração. A implementação deve ficar em camada de infraestrutura/apresentação e não deve introduzir lógica de tradução no domínio.

## Critérios de Sucesso

- O catálogo cobre os rótulos de seções e categorias definidos na spec.
- O fallback é previsível e testado.
- Nenhum rótulo factual do currículo é alterado.

## Testes da Tarefa

- [ ] Testes de unidade para mapeamento pt/en e fallback.

## Arquivos relevantes

- `infrastructure/localizacao/` (novo componente)
- `tests/test_catalogo_localizacao.py` (novo ou atualizado)
