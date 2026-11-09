# Especificação Técnica — JOB-0016

## Resumo Executivo

Esta Tech Spec implementa o PRD `prd-job-0016.md`: deixar o PDF gerado igual ao modelo `modelo-referencia-curriculo-en.pdf` (nesta pasta), com atenção especial aos tópicos iniciados por `-`.

A solução fica no adapter `GeradorPdfClient` (ReportLab), sem mudar a porta `GeradorPdfPort` nem o agregado `Curriculo`. O adapter passa a:
- usar a fonte Carlito, embarcada no repositório;
- ler os tokens visuais (cores, tamanhos, recuos) de um objeto de estilo único;
- interpretar cada bloco de experiência em partes (empresa, período, cargo, tópicos, contexto) antes de renderizar.

Em paralelo, os prompts de extração e ajuste por IA ganham regras explícitas para **preservar quebras de linha e tópicos `-`**. Sem isso, o gerador recebe prosa e não tem tópicos para formatar. Esse é o defeito visto hoje nos PDFs em `storage/`. O ajuste das experiências em conquistas + contexto é do JOB-0035, e este JOB só garante que o PDF desenhe o resultado (ver "Relação com o JOB-0035").

Analogia: o gerador de PDF é a gráfica. O modelo é a prova de impressão. O prompt de IA é o redator. Se o redator entregar o texto sem os tópicos, a gráfica não tem como imprimir tópicos. Por isso o JOB corrige os dois pontos.

## Arquitetura do Sistema

### Visão Geral dos Componentes

Medidas extraídas do modelo com `pdfplumber` (fonte da verdade do layout):

| Elemento | Fonte / tamanho | Cor | Posição / espaçamento |
|---|---|---|---|
| Página | — | — | Carta 612 × 792 pt, margens laterais 45 pt |
| Nome | Carlito Bold 16 | `#1F3864` | Centralizado, caixa alta |
| Contato | Carlito Regular 10 | `#595959` (link `#0563C1`, sublinhado) | Centralizado |
| Título de seção | Carlito Bold 11 | `#1F3864` | Caixa alta; linha 0,75 pt `#1F3864` ~13 pt abaixo |
| Rótulo de tecnologia | Carlito Bold 10,5 (inclui os dois-pontos) | `#000000` | Uma categoria por linha, passo ~14,8 pt |
| Corpo / perfil | Carlito Regular 10,5 | `#000000` | Entrelinha 12,8 pt |
| Empresa | Carlito Bold 11,5 | `#000000` | Esquerda |
| Período | Carlito Regular 10,5 | `#595959` | Alinhado à direita, termina em x = 513 pt |
| Cargo | Carlito Italic 10,5 | `#1F3864` | Linha abaixo da empresa |
| Tópico | `●` 10 + Carlito Regular 10,5 | `#000000` | Marcador em x = 63 pt (recuo 18), texto em x = 81 pt (recuo 36), recuo pendente |
| Contexto | Carlito Italic 10,5 | `#595959` | Sem recuo, após os tópicos |

Componentes novos:

| Componente | Local | Responsabilidade |
|---|---|---|
| `EstiloCurriculoPdf` | `src/jobsync/curriculo/adapters/pdf/estilo_curriculo_pdf.py` | Value Object (dataclass frozen) com os tokens da tabela acima e fábrica dos `ParagraphStyle` |
| `RegistradorFontesPdf` | `src/jobsync/curriculo/adapters/pdf/registrador_fontes_pdf.py` | Registra a família Carlito no ReportLab uma única vez; fallback para Helvetica |
| `InterpretadorExperiencias` | `src/jobsync/curriculo/adapters/pdf/interpretador_experiencias.py` | Converte o texto da seção em `list[BlocoExperiencia]` |
| `BlocoExperiencia` | mesmo arquivo do interpretador | Dataclass frozen: `empresa`, `periodo`, `cargo`, `topicos`, `contexto` |
| Fontes Carlito | `src/jobsync/curriculo/adapters/pdf/fontes/` | `Carlito-Regular.ttf`, `Carlito-Bold.ttf`, `Carlito-Italic.ttf`, `Carlito-BoldItalic.ttf` e `OFL.txt` |

Componentes modificados:

| Componente | Mudança |
|---|---|
| `GeradorPdfClient` (`src/jobsync/curriculo/adapters/gerador_pdf_client.py`) | Novo cabeçalho, títulos, tecnologias, experiências, formação; usa os componentes acima; remove `_estilo_contexto` e `_eh_linha_de_contexto` do JOB-0035 |
| `CatalogoLocalizacao` (`src/jobsync/shared_kernel/domain/catalogo_localizacao.py`) | Título `tecnologias` em inglês passa de `Technologies` para `Technical Skills` (igual ao modelo). O rótulo do contexto não entra aqui: a fonte única é `curriculo/domain/rotulos_experiencia.py` (JOB-0035) |
| `AjustadorTextoClient` (`src/jobsync/curriculo/adapters/ajustador_texto_client.py`) | Regra geral de preservação de linhas e tópicos e regra da seção TECNOLOGIAS (RF 28 e 29). A instrução da seção EXPERIENCIAS é do JOB-0035 |
| `ExtratorCurriculoClient` (`src/jobsync/curriculo/adapters/extrator_curriculo_client.py`) | Regra para preservar quebras de linha e converter `●`/`•` em `- ` (RF 31) |

Fluxo de dados (sem mudança de orquestração):

1. `AdaptarCurriculoParaVaga` / `CandidatarNaVagaExterna` chamam `GeradorPdfPort.gerar(curriculo, idioma_alvo)`.
2. `GeradorPdfClient` registra fontes (idempotente) e monta o cabeçalho.
3. Para cada `TipoSecao` em `_ORDEM_SECOES`, renderiza título + linha e delega ao formatador da seção.
4. Na seção de experiências, `InterpretadorExperiencias` gera os blocos, e o gerador transforma cada bloco em flowables.

## Design de Implementação

### Interfaces Principais

```python
@dataclass(frozen=True)
class BlocoExperiencia:
    empresa: str
    periodo: str = ""
    cargo: str = ""
    topicos: tuple[str, ...] = ()
    contexto: str = ""
    descricao: tuple[str, ...] = ()  # linhas soltas, desenhadas como texto normal


class InterpretadorExperiencias:
    def interpretar(self, conteudo: str) -> list[BlocoExperiencia]: ...


class RegistradorFontesPdf:
    def registrar(self) -> FamiliaFonte: ...  # nomes regular/bold/italic efetivos
```

`GeradorPdfPort.gerar(curriculo, idioma_alvo) -> bytes` permanece igual.

### Regras de interpretação de experiências

Entrada: texto da seção, blocos separados por linha em branco.

1. **Cabeçalho (1ª linha do bloco):** aplicar regex de período no fim da linha.
   - Mês: `Jan|Feb|...|Dec` e `Jan|Fev|...|Dez` (com ou sem ponto), ou `MM/AAAA`, ou só `AAAA`.
   - Fim: outra data ou `Present|Presente|Atual|Current|Hoje`.
   - Separador: `-`, `–` ou `—`, com espaços opcionais.
   - **Formato com travessão** (gerado por `MontarCurriculoDoPerfilEstruturado` e pelo `para_texto` do JOB-0035): `Cargo — Empresa (Período)`. Reconhecido quando a linha contém ` — ` (travessão U+2014, nunca hífen, para não confundir com `SIPPulse - High-Performance...`). Os parênteses finais são opcionais: o `para_texto` do JOB-0035 os omite quando não há período. Resultado: `cargo` = texto antes do travessão, `empresa` = texto entre o travessão e os parênteses (ou o fim da linha), `periodo` = conteúdo dos parênteses (vazio se `()` ou ausente). Parênteses cujo conteúdo não é período, data ou ano (ex.: `(UFSC)`) permanecem no nome.
   - Formação e certificações usam a mesma regra com `Curso — Instituição (Período)` e `Nome — Instituição (Ano)`: o lado esquerdo vai para a linha em itálico azul e o direito, em negrito.
   - Sem período encontrado: `empresa` = linha inteira, `periodo` = `""` (RF 24).
2. **Cargo (2ª linha):** só quando o cargo não veio do cabeçalho com travessão, e quando não começa com marcador, não começa com rótulo de contexto e tem até 80 caracteres sem ano de 4 dígitos (regra atual de `_parece_posicao_experiencia`, reaproveitada).
3. **Tópicos:** linhas que começam com `-`, `•`, `●` ou `*`. Remover o marcador e espaços.
4. **Contexto:** linha que tem, antes do primeiro `:`, um rótulo de `ROTULOS_CONTEXTO_RECONHECIDOS` (`jobsync.curriculo.domain.rotulos_experiencia`; mesma regra do JOB-0035: sem diferenciar maiúsculas, aceita `Contexto:texto` sem espaço, e `Contextualizei...` não é rótulo), mais as linhas seguintes que não são tópicos nem rótulo (continuação do mesmo parágrafo, unidas por espaço). O rótulo permanece no texto exibido.
5. **Descrição:** qualquer outra linha (sem marcador, sem rótulo, fora do cabeçalho e do cargo) vai para `descricao` e é desenhada como texto normal, como hoje. Isso preserva o texto corrido de currículos antigos e o comportamento do JOB-0035 (`Contextualizei...` não vira itálico). Nenhum texto se perde.

### Regras de renderização

- **Cabeçalho:** `Paragraph(nome.upper(), estilo.nome)` com `alignment=TA_CENTER`. O contato usa `<link href="https://{linkedin}" color="#0563C1"><u>{linkedin}</u></link>`, com o prefixo `https://` só quando ausente.
- **Título de seção:** `Paragraph(titulo.upper(), estilo.titulo_secao)` + `HRFlowable(width="100%", thickness=0.75, color="#1F3864", spaceBefore=2, spaceAfter=6)`.
- **Tecnologias:** um `Paragraph` por linha não vazia. Reaproveitar `_negritar_categorias_tecnologia` (JOB-0002/0003). Se o conteúdo vier em uma única linha com várias categorias (`Languages: ..., Frameworks: ...`), quebrar antes de cada rótulo conhecido do catálogo (proteção contra saída da IA, RF 14).
- **Empresa + período:** `Table([[Paragraph(empresa), Paragraph(periodo)]], colWidths=[largura_util - 54 - L, L])`, com `L = 140 pt`, coluna 2 `ALIGN=RIGHT` e paddings zerados. A largura do período termina em 468 pt a partir da margem (513 pt absoluto), igual ao modelo (ver Questão 2 do PRD). A tabela mantém a ordem de leitura "empresa → período" na extração de texto (ATS).
- **Tópicos:** `Paragraph(texto, estilo.topico, bulletText="●")`, com `leftIndent=36`, `bulletIndent=18`, `bulletFontName` = Carlito e `bulletFontSize=10`. O recuo pendente vem do próprio `leftIndent` (RF 19). `spaceAfter=3` entre tópicos (RF 20).
- **Contexto:** `Paragraph(texto, estilo.contexto)` em itálico cinza.
- **Bloco de experiência:** `KeepTogether([tabela_cabecalho, cargo, primeiro_topico_ou_contexto])` para evitar cabeçalho órfão no fim da página. `Spacer(1, 8)` entre blocos (RF 22).
- **Formação/Certificações:** mesmo `InterpretadorExperiencias` (instituição + período, depois curso/grau em itálico azul). Reaproveita a tabela de cabeçalho. Idiomas: `<b>idioma</b> — nível`, uma linha por item.
- **Escape:** manter `_escape_text` antes de aplicar qualquer markup.

### Modelos de Dados

Sem mudança em entidades de domínio, banco de dados ou DTOs. `BlocoExperiencia` é um modelo interno do adapter (apresentação), não do domínio.

### Endpoints de API

Nenhum endpoint novo ou alterado. Os endpoints que retornam PDF passam a devolver o novo layout sem mudança de contrato.

## Pontos de Integração

- **ReportLab 4.2.5** (já em `requirements*.txt`): `pdfmetrics.registerFont(TTFont(...))` e `registerFontFamily("Carlito", normal=..., bold=..., italic=..., boldItalic=...)`, para que `<b>` e `<i>` funcionem dentro dos `Paragraph`.
- **Fonte Carlito:** licença SIL OFL 1.1, distribuição permitida com o arquivo `OFL.txt`. Os arquivos ficam dentro de `src/`, então o `COPY src/ ./src/` do `Dockerfile` já os inclui. Nenhuma mudança no Dockerfile é necessária.
- **Erros:** se os TTF não forem encontrados, `RegistradorFontesPdf` registra um `logger.warning` e retorna a família Helvetica. O PDF continua sendo gerado (degradação visual, não falha).
- **OpenAI:** apenas mudança de texto dos prompts. Sem novo modelo, chamada ou custo.

### Ajustes de prompt

Texto a incluir (em português, como os prompts atuais):

- `AjustadorTextoClient`, regra geral: "Preserve a estrutura de linhas do conteúdo original. Cada linha que começa com '- ' no original deve continuar sendo uma linha que começa com '- ' na saída. Nunca junte tópicos em um parágrafo."
- `TECNOLOGIAS`: "Mantenha uma categoria por linha, no formato 'Rótulo: item1, item2'."
- `EXPERIENCIAS` e `AjustadorExperienciaOpenAIClient`: **fora deste JOB.** O JOB-0035 define o prompt (2 a 6 conquistas + contexto) e o formato JSON. Este JOB só garante a leitura do texto resultante.
- `ExtratorCurriculoClient`: "Preserve as quebras de linha originais. Converta marcadores '●' ou '•' em '- '."

### Contrato de texto de experiência

Formato que o PDF aceita, vindo da IA (fonte PDF) ou da conversão do JOB-0035 e do Perfil Estruturado:

```
Empresa Período            ou   Cargo — Empresa (Período)
Cargo                           - conquista
- conquista                     Contexto: texto
Contexto: texto
```

Blocos separados por linha em branco. Cargo, tópicos e contexto são opcionais.

## Abordagem de Testes

### Testes Unidade

Seguir `.windsurf/rules/testing-rules.md`: AAA separado por linha em branco, sem comentários, comportamento pela API pública.

`src/jobsync/tests/curriculo/test_interpretador_experiencias.py` (`TestInterpretadorExperiencias`):
- separa empresa e período `Mar 2026 - Present`;
- separa período entre parênteses do formato do perfil estruturado;
- linha sem período retorna `periodo == ""`;
- reconhece cargo, tópicos `-`, `•` e `●`, e contexto `Context:` / `Contexto:`;
- formato com travessão `Cargo — Empresa (Período)`: separa os três campos; `()` vazio e parênteses ausentes dão `periodo == ""`; hífen no nome da empresa não separa;
- formação `Curso — Instituição (Período)` e certificação `Nome — Instituição (Ano)`;
- bloco só com contexto (caso "Starian") e bloco sem contexto;
- múltiplos blocos separados por linha em branco;
- nenhuma linha de entrada é descartada.

`src/jobsync/tests/curriculo/test_gerador_pdf_client.py`: novos testes que chamam `gerar()` e inspecionam o PDF com `pdfplumber` (já é dependência):
- nome centralizado, em caixa alta, `Carlito-Bold` 16 pt, cor `#1F3864`;
- título `EXPERIENCE` em caixa alta e presença de linha horizontal abaixo;
- tópico `-` gera caractere `●` com x ≈ 63 pt, e a linha de continuação começa em x ≈ 81 pt;
- período com `x1` ≈ 513 pt e cor `#595959`;
- cargo em `Carlito-Italic` com cor `#1F3864`;
- tecnologias: uma linha por categoria, mesmo quando a entrada vem em linha única;
- link do LinkedIn presente nas anotações da página;
- ordem do texto extraído: empresa → período → cargo → tópicos → contexto.

Testes existentes que mudam de expectativa (atualizar, não remover):
- `test_formatar_experiencias_com_cabecalho_e_posicao`, `test_nao_aplica_negrito_em_descricao_de_experiencia` e `test_adiciona_espacamento_extra_entre_blocos_de_experiencia`: hoje verificam `<b>...</b>` e `&bull;` nos `Paragraph`. Reescrever para a nova saída (tabela de cabeçalho + `bulletText`).
- `src/jobsync/tests/shared_kernel/test_catalogo_localizacao.py:10`: `Technologies` → `Technical Skills`.
- Testes do JOB-0035 em `test_gerador_pdf_client.py` (contexto em itálico cinza): trocar `Helvetica-Oblique` e `#666666` por `Carlito-Italic` e `#595959`, mantendo as demais asserções.

`test_registrador_fontes_pdf.py`: registra Carlito quando os arquivos existem; retorna Helvetica quando o diretório não existe (usar `tmp_path`).

Testes de prompt (`AjustadorTextoClient` e `ExtratorCurriculoClient`, com `unittest.mock` no `ClienteOpenAI`): verificar que o `prompt_usuario`/`prompt_sistema` enviado contém a regra de preservação de tópicos e, para TECNOLOGIAS, a de uma categoria por linha.

### Testes de Serviço

- Teste visual manual: gerar o PDF com o mesmo conteúdo do modelo e comparar lado a lado (`pdftoppm -r 80`). Anexar as duas imagens no PR.
- Rodar `lint-imports` (contratos do `setup.cfg`) para garantir que `adapters/pdf/` não fere as camadas.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. **Fontes e estilo:** `RegistradorFontesPdf`, `EstiloCurriculoPdf` e os arquivos Carlito. Base de todo o resto.
2. **`InterpretadorExperiencias` (TDD):** lógica pura, sem ReportLab. Fácil de testar isoladamente.
3. **`GeradorPdfClient`:** cabeçalho, títulos, tecnologias, perfil, experiências, formação, nessa ordem. Atualizar os testes existentes afetados.
4. **`CatalogoLocalizacao`:** novo título `Technical Skills`.
5. **Prompts de IA:** extrator e ajustador de seção (regra geral e TECNOLOGIAS). As experiências ficam no JOB-0035.
6. **Validação visual** contra o modelo e ajuste fino de espaçamentos.

### Dependências Técnicas

- Nenhuma infraestrutura nova.
- Download dos TTF da Carlito (pacote `fonts-crosextra-carlito` ou repositório oficial `googlefonts/carlito`), uma única vez, para commit no repositório.

## Monitoramento e Observabilidade

- `logger.warning("Fonte Carlito não encontrada em %s; usando Helvetica", caminho)` no fallback de fonte.
- `logger.debug` com a contagem de blocos, tópicos e blocos sem período identificado por geração. Isso ajuda a detectar quando a IA voltou a devolver prosa.
- Sem log do conteúdo do currículo (dados pessoais).

## Considerações Técnicas

### Decisões Principais

| Decisão | Justificativa | Alternativas rejeitadas |
|---|---|---|
| Manter ReportLab | Já é dependência, roda na imagem slim, testes já existem | WeasyPrint/HTML (novas libs nativas); LibreOffice (pesado, fora do container) |
| Embarcar Carlito em `src/` | Igual ao modelo, licença OFL, funciona no Docker sem `apt-get` | Instalar via `apt` no Dockerfile (não cobre ambiente local/Streamlit); Helvetica (visual diferente) |
| `Table` para empresa + período | Alinhamento à direita confiável e ordem de leitura linear | `canvas.drawRightString` (fora do fluxo, quebra paginação) |
| `bulletText` no `Paragraph` | Recuo pendente nativo, uma linha de código por tópico | `ListFlowable` (mais verboso, sem ganho aqui) |
| Interpretador no adapter, não no domínio | É regra de apresentação; evita mudar o agregado `Curriculo` (fora de escopo do PRD) | Estruturar experiências no domínio (mudança grande, afeta extração e IA) |
| Corrigir no mesmo JOB os prompts de extração, de tecnologias e a regra geral | Sem tópicos na entrada, o layout não atende o PRD | JOB separado (entrega visual incompleta) |
| Travessão (U+2014) como separador do formato `Cargo — Empresa (Período)` | Evita mudar `MontarCurriculoDoPerfilEstruturado` e o `para_texto` do JOB-0035; hífen nunca separa | Mudar os dois geradores para o formato do modelo (dois lugares a alterar e testar) |
| Reutilizar `rotulos_experiencia.py` (JOB-0035) para o rótulo do contexto | Já está na `main`; fonte única (DRY) | Duplicar o rótulo no `CatalogoLocalizacao` (era o plano antes do JOB-0035 ser integrado) |

### Riscos Conhecidos

- **IA ainda devolver prosa:** mitigado pelas regras de prompt e pela proteção no gerador (quebra de categorias de tecnologia). Para experiências, prosa vira contexto, sem perda de texto.
- **Regex de período com falso positivo** (ex.: nome de empresa com ano): exigir que o período esteja no fim da linha e tenha o separador de intervalo.
- **Diferença de paginação** em relação ao modelo: aceitável, desde que estilos e espaçamentos batam. `KeepTogether` evita cabeçalho órfão.
- **Tamanho do repositório:** os 4 TTF somam cerca de 2,7 MB (medido no pacote `fonts-crosextra-carlito`).
- **Regressão nos comportamentos do JOB-0035:** este JOB reescreve `_formatar_conteudo_experiencias`, onde o JOB-0035 colocou o reconhecimento do contexto. Mitigação: manter as asserções dos testes dele e trocar só fonte e cor.
- **Travessão em nome de empresa:** um nome com ` — ` e parênteses no fim seria separado de forma errada. Caso raro, e o resultado é só visual (nenhum texto se perde).

### Relação com o JOB-0035

O JOB-0035 já está na `main` (PR 47). Ele criou `ExperienciaAdaptada` (com `para_texto`), `rotulos_experiencia.py`, os prompts de experiências e um desenho provisório do contexto no `GeradorPdfClient`.

| Tema | JOB-0016 | JOB-0035 (na `main`) |
|---|---|---|
| Desenho do contexto no PDF | Substitui o provisório pelo estilo do modelo | Deixou `_estilo_contexto` e `_eh_linha_de_contexto` (Helvetica Oblique, `#666666`) |
| Leitura de `Cargo — Empresa (Período)` | Faz (parênteses opcionais) | `para_texto` gera esse formato |
| Rótulo `Contexto`/`Context` | Reutiliza `ROTULOS_CONTEXTO_RECONHECIDOS` | `curriculo/domain/rotulos_experiencia.py` |
| Prompt de EXPERIENCIAS e `AjustadorExperienciaOpenAIClient` | Não altera | Alterou |
| Regra geral de tópicos, TECNOLOGIAS e extração | Altera | Não alterou |

Comportamentos do JOB-0035 que o novo gerador deve manter (há testes em `test_gerador_pdf_client.py`): rótulo nos dois idiomas, sem diferenciar maiúsculas e aceitando `Contexto:texto` sem espaço; `Contextualizei...` não é rótulo; contexto logo após o cabeçalho não vira negrito; caracteres especiais escapados; sem contexto, sem linha em itálico. Muda só a fonte (`Carlito-Italic`) e a cor (`#595959`, contraste de cerca de 7:1, cálculo meu).

### Conformidade com Padrões

- `.windsurf/rules/code-design-standards.md`: mudança restrita à camada `adapters` do domínio `curriculo`; `shared_kernel/domain` recebe apenas rótulos (sem IO). Domínio sem dependência de ReportLab.
- `.windsurf/rules/testing-rules.md`: classes de teste `Test<Classe>`, AAA, mocks só com `unittest.mock`, testes pela API pública.
- `.windsurf/rules/general-rules.md`: mudanças limitadas ao escopo do PRD.
- `AGENTS.md`: SOLID (SRP — estilo, fontes e interpretação separados do gerador), DRY (reuso das funções de negrito do JOB-0002/0003 e de `_parece_posicao_experiencia`), KISS/YAGNI (sem sistema de temas), TDD.
- Desvio: nenhum identificado.

### Arquivos relevantes e dependentes

- `src/jobsync/curriculo/adapters/gerador_pdf_client.py`
- `src/jobsync/curriculo/adapters/pdf/` (novo)
- `src/jobsync/curriculo/domain/gerador_pdf_port.py` (sem mudança, referência)
- `src/jobsync/curriculo/domain/curriculo.py` (sem mudança, referência)
- `src/jobsync/shared_kernel/domain/catalogo_localizacao.py`
- `src/jobsync/curriculo/adapters/ajustador_texto_client.py`
- `src/jobsync/curriculo/domain/rotulos_experiencia.py` e `experiencia_adaptada.py` (JOB-0035; referência, não alterar)
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0035-conquistas-e-contexto-nas-experiencias/` (referência)
- `src/jobsync/curriculo/adapters/extrator_curriculo_client.py`
- `src/jobsync/perfil_estruturado/domain/montar_curriculo_do_perfil_estruturado_service.py` (formato de entrada a suportar)
- `src/jobsync/curriculo/service_layer/adaptar_curriculo_para_vaga/service.py` e `src/jobsync/vaga_externa/service_layer/candidatar_na_vaga_externa/service.py` (consumidores da porta)
- `src/jobsync/tests/curriculo/test_gerador_pdf_client.py`
- `src/jobsync/tests/shared_kernel/test_catalogo_localizacao.py`
- `Dockerfile` (sem mudança; já copia `src/`)
- `sdd/specs/recrutamento/geracao-de-curriculo/job-0016-layout-pdf-curriculo-modelo-referencia/modelo-referencia-curriculo-en.pdf`
