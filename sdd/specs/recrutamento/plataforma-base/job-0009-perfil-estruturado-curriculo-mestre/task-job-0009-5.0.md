# Tarefa 5.0: Porta ExtratorPerfilEstruturadoPort + adapter Groq + use case ImportarPerfilDePdf

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar a extração de dados estruturados de perfil diretamente de um PDF via IA, reaproveitando o extrator de texto (`ExtratorTextoPdfPlumber`) e o cliente Groq já existentes, com um novo prompt que pede a estrutura completa (experiências, formação, certificações, idiomas e tecnologias como listas de objetos) em vez de texto livre por seção.

<requirements>
- `ExtratorPerfilEstruturadoPort` (ABC) em `src/domain/perfil_estruturado/extrator_perfil_estruturado_port.py`: `extrair(self, pdf_bytes: bytes) -> DadosPerfilExtraidos`.
- `ExtratorPerfilEstruturadoGroq`: reaproveita `ExtratorTextoPdfPlumber` (extração de texto bruto) e `ClienteGroq.solicitar_json` (mesmo padrão dos outros adapters Groq). Novo prompt de sistema pedindo JSON com nome, email, linkedin, resumo, e listas de experiências/formações/certificações/idiomas/tecnologias.
- Mesma robustez a dados malformados já aplicada nos demais adapters Groq desta base de código: nunca deixar `.strip()` ou acesso a campo quebrar se o modelo devolver um tipo inesperado (ex: um objeto aninhado em vez de string) — coagir com `str(valor)` antes de `.strip()`, e tratar listas ausentes/malformadas como lista vazia.
- `ImportarPerfilDePdf`: pacote com `dtos.py` (`ImportarPerfilDePdfInputDto` com `pdf_curriculo: bytes`), `validator.py` (PDF não vazio), `use_case.py` (`executar(input_dto) -> DadosPerfilExtraidos`, chama `extrator.extrair`), `__init__.py`.
- Complexidade: medium (prompt novo + parsing de listas de objetos aninhados, com a mesma robustez a malformação já estabelecida no projeto).
</requirements>

## Subtarefas

- [ ] 5.1 Criar `src/domain/perfil_estruturado/extrator_perfil_estruturado_port.py` com a porta.
- [ ] 5.2 Implementar `src/infrastructure/llm/extrator_perfil_estruturado_groq.py`, incluindo o novo prompt de sistema.
- [ ] 5.3 Implementar o parsing robusto da resposta JSON para `DadosPerfilExtraidos` (incluindo conversão de string para `NivelIdioma`, com fallback seguro se o valor não corresponder a nenhum membro do enum).
- [ ] 5.4 Criar pacote `src/application/use_cases/importar_perfil_de_pdf/`.
- [ ] 5.5 Escrever testes do adapter (fake de `ClienteGroq`, cobrindo resposta bem formada e resposta malformada/com campos ausentes) e do use case (fake do adapter).

## Detalhes de Implementação

Consultar as seções "Interfaces Principais" e "Riscos Conhecidos" de `techspec-job-0009.md`. Seguir o estilo de `src/infrastructure/llm/gerador_sugestoes_ats_groq.py` (que já trata respostas malformadas com `_normalizar_sugestoes`) como referência de robustez.

## Critérios de Sucesso

- `ExtratorPerfilEstruturadoGroq.extrair` converte uma resposta bem formada da IA em `DadosPerfilExtraidos` corretamente.
- Resposta malformada (campos ausentes, tipos inesperados) não lança exceção não tratada — degrada para valores vazios/padrão nos campos afetados.
- `ImportarPerfilDePdf.executar` repassa o resultado do extrator sem alteração.

## Testes da Tarefa

- [ ] Teste unitário: resposta bem formada da IA é convertida corretamente em `DadosPerfilExtraidos`, incluindo múltiplas experiências/formações/idiomas.
- [ ] Teste unitário: resposta com campos ausentes ou tipos inesperados não lança exceção, produz valores vazios/padrão nos campos afetados.
- [ ] Teste unitário: `ImportarPerfilDePdf` com PDF vazio levanta `ValueError`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `src/domain/perfil_estruturado/extrator_perfil_estruturado_port.py`
- `src/infrastructure/llm/extrator_perfil_estruturado_groq.py`
- `src/application/use_cases/importar_perfil_de_pdf/dtos.py`
- `src/application/use_cases/importar_perfil_de_pdf/use_case.py`
- `src/application/use_cases/importar_perfil_de_pdf/validator.py`
- `src/application/use_cases/importar_perfil_de_pdf/__init__.py`
- `src/tests/infrastructure/llm/test_extrator_perfil_estruturado_groq.py`
- `src/tests/application/use_cases/importar_perfil_de_pdf/test_use_case.py`
