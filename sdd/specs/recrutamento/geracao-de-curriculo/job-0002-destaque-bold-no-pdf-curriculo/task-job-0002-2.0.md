# Tarefa 2.0: Implementar ênfase em negrito para Tecnologias, Experiências e Formação

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Implementar a lógica de ênfase no adapter de PDF para aplicar negrito apenas aos elementos definidos no PRD e na Tech Spec: etiquetas de categoria na seção de Tecnologias, cabeçalhos de experiência (empresa + período) e cargos, e títulos/categorias na formação acadêmica.

<requirements>
- Aplicar negrito compatível com ReportLab às etiquetas de categoria na seção de Tecnologias.
- Aplicar negrito ao cabeçalho empresa+período e à posição da experiência.
- Aplicar negrito aos títulos de formação e categorias na seção de Formação acadêmica.
- Não alterar o conteúdo das descrições ou dos itens de tecnologia.
</requirements>

## Subtarefas

- [ ] 2.1 Implementar detecção e ênfase para categorias de tecnologia: Languages, Frameworks, Web Development, DevOps, Databases, Version Control, Other.
- [ ] 2.2 Implementar detecção e ênfase do cabeçalho de experiência e da posição ocupada.
- [ ] 2.3 Implementar detecção e ênfase de títulos/categorias na formação acadêmica.
- [ ] 2.4 Garantir que a ênfase não seja aplicada em descrições de atividades ou textos que não sejam cabeçalhos.

## Detalhes de Implementação

Use o mecanismo de formatação inline proposto no `techspec-job-0002.md` e aplique a transformação de string de forma conservadora para evitar ênfase excessiva. O adapter deve processar texto de apresentação e preservar as partes não destacadas.

## Critérios de Sucesso

- [ ] As etiquetas de categoria em Tecnologias são renderizadas em negrito sem alterar o conteúdo listado.
- [ ] O cabeçalho e a posição das experiências aparecem em negrito no PDF.
- [ ] Os títulos/categorias de formação acadêmica aparecem em negrito.
- [ ] As descrições de atividades permanecem no estilo normal.

## Testes da Tarefa

- [ ] Atualizar ou adicionar testes que verifiquem a saída de formatação para cada seção relevante.
- [ ] Usar exemplos de texto parecidos com o PRD para cobrir tecnologias, experiência e formação.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `sdd/specs/recrutamento/geracao-de-curriculo/job-0002-destaque-bold-no-pdf-curriculo/prd-job-0002.md`
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0002-destaque-bold-no-pdf-curriculo/techspec-job-0002.md`
- `infrastructure/pdf/gerador_pdf_reportlab.py`
- `tests/test_gerador_pdf.py`
