# Tarefa 3.0: Domain Service MontarCurriculoDoPerfilEstruturado

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar o Domain Service que converte um `PerfilEstruturado` no `Curriculo` já existente (Fase 0), formatando cada lista de entidades estruturadas em texto por seção. Retorna `None` quando não há conteúdo mínimo, permitindo que a UI trate isso como "perfil inexistente".

<requirements>
- `MontarCurriculoDoPerfilEstruturado.executar(perfil: PerfilEstruturado) -> Curriculo | None`.
- Mapeamento de seções: `resumo_profissional` → `TipoSecao.PERFIL`; `experiencias` → `TipoSecao.EXPERIENCIAS` (cada entrada formatada como "Cargo — Empresa (período)\nDescrição", entradas separadas por linha em branco); `formacoes` → `TipoSecao.FORMACAO` (formato análogo); `certificacoes` → `TipoSecao.CERTIFICACOES`; `idiomas` → `TipoSecao.IDIOMAS` (ex: "Inglês — Avançado"); `tecnologias` → `TipoSecao.TECNOLOGIAS` (join com ", ").
- Seções sem conteúdo (lista vazia ou string vazia) são omitidas do `Curriculo` resultante — nunca criar uma `SecaoCurriculo` com `conteudo` vazio (violaria a invariante já existente de `SecaoCurriculo`).
- Se, depois de montar, nenhuma seção tiver conteúdo, retornar `None` em vez de um `Curriculo` sem seções.
- `nome_completo`, `email`, `linkedin` do `Curriculo` vêm diretamente do `PerfilEstruturado`.
- Complexidade: medium (várias formatações de texto, mas sem lógica condicional complexa).
</requirements>

## Subtarefas

- [ ] 3.1 Criar `src/domain/perfil_estruturado/montar_curriculo_do_perfil_estruturado_service.py` com a classe `MontarCurriculoDoPerfilEstruturado`.
- [ ] 3.2 Implementar a formatação de cada tipo de seção (experiências, formação, certificações, idiomas, tecnologias, resumo).
- [ ] 3.3 Implementar o retorno `None` quando não há nenhuma seção com conteúdo.
- [ ] 3.4 Escrever testes cobrindo: perfil completo, perfil parcial (só algumas seções), perfil vazio (retorna `None`).

## Detalhes de Implementação

Consultar a seção "Interfaces Principais" (assinatura e docstring) de `techspec-job-0009.md`. Reaproveitar `Curriculo`/`SecaoCurriculo`/`TipoSecao` de `src/domain/curriculo/__init__.py` sem modificá-los.

## Critérios de Sucesso

- Um `PerfilEstruturado` com todas as seções preenchidas gera um `Curriculo` com todas as seções correspondentes.
- Um `PerfilEstruturado` com só algumas seções preenchidas gera um `Curriculo` só com essas seções.
- Um `PerfilEstruturado` totalmente vazio (sem resumo, experiências, formação, certificações, idiomas, tecnologias) retorna `None`.

## Testes da Tarefa

- [ ] Teste unitário: perfil completo gera `Curriculo` com todas as seções, conteúdo formatado corretamente.
- [ ] Teste unitário: perfil só com `resumo_profissional` e `tecnologias` gera `Curriculo` só com `TipoSecao.PERFIL` e `TipoSecao.TECNOLOGIAS`.
- [ ] Teste unitário: perfil sem nenhum conteúdo retorna `None`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/domain/perfil_estruturado/montar_curriculo_do_perfil_estruturado_service.py`
- `src/tests/domain/perfil_estruturado/test_montar_curriculo_do_perfil_estruturado_service.py`
