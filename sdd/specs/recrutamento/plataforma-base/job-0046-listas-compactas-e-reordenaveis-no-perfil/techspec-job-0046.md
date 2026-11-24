# Especificação Técnica — JOB-0046

PRD: `prd-job-0046.md` (mesma pasta). Protótipo: `sdd/prototipos/perfil_experiencias_prototipo.html`.

## Resumo Executivo

A mudança é quase toda de frontend. `ListaItensCurriculo` ganha modos opcionais (cartão recolhível, reordenável, linha única, limite, ordenação por período), e a revisão do currículo adaptado continua a usá-lo sem as novas props. A reordenação usa o `@dnd-kit` já instalado, com `useFieldArray.move()` do React Hook Form. As tecnologias viram `string[]` no formulário e reaproveitam `EditorTags` e `soltarTag`. O desfazer guarda um instantâneo de `form.getValues()`, e o `ToastProvider` passa a aceitar uma ação.

No backend há uma única mudança de contrato: o objeto de valor `Periodo` (`shared_kernel`) e o limite de 15 itens são validados no `SalvarPerfilEstruturadoInputValidator`, que já resulta em 422. As entidades de domínio não mudam, para o repositório continuar lendo perfis já salvos com período livre. Um espelho `periodo.ts` valida no frontend com a mesma tabela de casos. O aviso ao sair vira o hook compartilhado `useAvisoAlteracoesNaoSalvas` (`useBlocker` e `beforeunload`).

Decisões fechadas com o produto nas perguntas 1 a 5 (estender o componente, desfazer, aviso ao sair, `Periodo` na validação de entrada, constante de limite). Para as perguntas 6 a 10 adotei as recomendadas, que ficam registradas em "Decisões Principais".

## Arquitetura do Sistema

### Visão Geral dos Componentes

**Novos (backend)**

| Componente | Responsabilidade |
|---|---|
| `shared_kernel/domain/periodo.py` | `Periodo`: lê e valida `início - fim`, expõe o ano e mês iniciais e se o período é atual; `PeriodoInvalido(ValueError)` com mensagem e exemplo; `validar_ano(texto)` para certificações |

**Modificados (backend)**

- `perfil_estruturado/service_layer/salvar_perfil_estruturado/validator.py`: valida período de experiências e formações (se preenchido), ano das certificações e o limite de 15 itens em experiências, formações, certificações e idiomas. Tecnologias ficam fora do limite.
- `perfil_estruturado/domain/perfil_estruturado.py`: só a constante `LIMITE_DE_ITENS_POR_LISTA = 15`; nenhuma invariante nova nas entidades.
- `entrypoints/api/routers/perfil_estruturado_router.py`: sem código novo (o `ValueError` já vira 422 no `POST` e no `PUT`); a mensagem cita item e campo (ex.: "Experiência 2: período inválido. Use Mar 2024 - Atual ou 2020 - 2022.").

**Novos (frontend)**

| Componente | Responsabilidade |
|---|---|
| `shared/formulario-curriculo/periodo.ts` | Espelho do `Periodo`: `validarPeriodo`, `validarAno`, `inicioDoPeriodo`, `ordenarPorPeriodo` |
| `shared/formulario-curriculo/limites.ts` | `LIMITE_DE_ITENS = 15` |
| `shared/formulario-curriculo/CartaoDaLista.tsx` | Item recolhível com alça (`useSortable`), resumo, chips, botões de abrir e de mover |
| `shared/formulario-curriculo/anuncios-de-lista.ts` | Anúncios em português do arrasto de itens (mesmo padrão de `anuncios-de-tags.ts`) |
| `shared/formulario-curriculo/use-cartoes-abertos.ts` | Cartões abertos lembrados no `localStorage` |
| `shared/formulario-curriculo/use-historico-do-formulario.ts` | `registrar()` e `desfazer()` sobre `getValues()` e `reset()` |
| `shared/formulario-curriculo/ListaDeTecnologias.tsx` | Tags reordenáveis das tecnologias gerais |
| `shared/formulario-curriculo/AvisoAlteracoesNaoSalvas.tsx` e `use-aviso-alteracoes-nao-salvas.ts` | `useBlocker`, `beforeunload` e `ConfirmacaoModal` |

**Modificados (frontend)**

- `ListaItensCurriculo.tsx` e `campos-curriculo.ts`: novas props opcionais e `CampoItem.validar`.
- `ToastProvider.tsx` e `toast-context.ts`: ação e duração por aviso.
- `features/perfil/PerfilPage.tsx` e `formulario-perfil.ts`: usam os novos modos; `tecnologias` passa a `string[]`.
- `features/ajustar-vaga/RevisaoCurriculoAdaptado.tsx`, `AjustarVagaPage.tsx`, `features/analisar-ats/AnalisarAtsPage.tsx` e `features/descobrir-vagas/DescobrirVagasPage.tsx`: só o aviso ao sair.
- `test/renderizar-app.tsx`: garantir roteador de dados (exigido pelo `useBlocker`).

### Fluxo de dados

1. O usuário arrasta; o `onDragEnd` chama `registrar()` e `move(de, para)`; o toast oferece "Desfazer".
2. "Salvar perfil" valida no formulário (`validar` por campo) e envia o `PUT` atual; o backend revalida (422 como rede de segurança).
3. Os cartões abertos vivem no `localStorage` e não passam pela API.

## Design de Implementação

### Interfaces Principais

```python
# shared_kernel/domain/periodo.py
class PeriodoInvalido(ValueError): ...

@dataclass(frozen=True)
class Periodo:
    inicio: tuple[int, int | None]      # (ano, mês)
    fim: tuple[int, int | None] | None  # None = atual
    @classmethod
    def ler(cls, texto: str) -> "Periodo": ...  # levanta PeriodoInvalido
```

```tsx
// ListaItensCurriculo (props novas, todas opcionais)
interface ModosDaLista<V> {
  modo?: "formulario" | "cartao" | "linha";
  resumoDoItem?: (valores: V) => { titulo: string; subtitulo?: string; meta?: string; chips?: ReactNode };
  reordenavel?: boolean;
  limite?: number;
  ordenarPor?: { rotulo: string; chave: (valores: V) => number | null };
  chaveDoItem?: (valores: V) => string;
  historico?: HistoricoDoFormulario;
}
```

### Modelos de Dados

- **Formato do período:** `início - fim`; cada lado é `aaaa`, `mmm aaaa` (mês abreviado em português ou inglês) ou `mm/aaaa`; o fim pode ser `Atual` ou `Presente`; separador hífen ou travessão, com ou sem espaços; início não pode ser depois do fim. Certificação: `aaaa`. Campo vazio é válido.
- **Formulário de perfil:** `tecnologias: string[]` (hoje `string`); o envio e a leitura da API já são lista, então só a conversão de `formulario-perfil.ts` muda.
- **Armazenamento local:** chave `jobsync:perfil:cartoes:{perfil}:{lista}`, valor lista de chaves de item (`empresa|cargo|período`, `instituição|curso|período`, `nome|instituição|ano`). Ao carregar, vale a interseção com os itens atuais.
- **Banco e API:** sem campo novo; a ordem é a posição na lista salva.

### Endpoints de API

Sem endpoint novo. `POST /v1/perfil-estruturado` e `PUT /v1/perfil-estruturado/{id}` passam a devolver 422 para período, ano ou quantidade de itens inválidos (única mudança de contrato, pedida no PRD). O endpoint de conquista aprovada, que usa a posição da experiência, não muda: o fluxo de adaptação sempre lê o perfil salvo.

## Pontos Integração

Nenhum serviço externo. O app Streamlit legado salva pelo mesmo caso de uso: passa a receber o 422 e já mostra o erro (`st.error`), sem alteração.

## Abordagem de Testes

### Testes Unidade

- **Backend (TDD):** `Periodo` (tabela de casos válidos e inválidos, início maior que fim, `Atual`, meses em pt e en, travessão, sem espaços); `SalvarPerfilEstruturadoInputValidator` (período e ano inválidos, 16 itens, tecnologias acima de 15 aceitas, período vazio aceito); repositório lê perfil salvo com período livre sem erro.
- **Tabela compartilhada:** `frontend/src/shared/formulario-curriculo/periodo.casos.json` lida pelo pytest e pelo Vitest, para os dois lados nunca divergirem.
- **Frontend (Vitest):** `periodo.ts`; `ordenarPorPeriodo` (atual primeiro, vazios no fim mantendo a ordem, desempate estável); `ListaItensCurriculo` nos três modos (recolher e abrir, limite desabilita adicionar, botões de mover, `move` por mock do `DndContext` no padrão de `CandidaturasPage.test.tsx`, desfazer); `use-cartoes-abertos` (storage ausente ou lançando erro); `ToastProvider` com ação; aviso ao sair em cada tela (navegação bloqueada, confirmar, cancelar, `beforeunload`, sem aviso depois de salvar).
- **E2E (Playwright):** arrasto real e teclado em cada lista (padrão de `quatro-blocos.spec.ts`); período inválido bloqueia o salvar; cartões abertos voltam após recarregar; aviso ao sair; o axe de `acessibilidade.spec.ts` sobre `/perfil` com cartões e alças.

### Testes de Serviço

`test_perfil_estruturado_router.py`: 422 com a mensagem do item para período, ano e limite; contrato anterior continua aceito com dados válidos.

## Sequenciamento de Desenvolvimento

### Ordem de Construção

1. `Periodo` e validador (backend), com a tabela compartilhada: base das regras, sem dependência de UI.
2. `periodo.ts`, `limites.ts` e `CampoItem.validar` (frontend), com os mesmos casos.
3. `ToastProvider` com ação e `use-historico-do-formulario`.
4. `ListaItensCurriculo` em modo cartão com reordenação, anúncios, limite e ordenar por período.
5. Cartões abertos lembrados e a lista de idiomas em linha única.
6. Tecnologias como tags reordenáveis.
7. Aviso ao sair e aplicação nas telas do escopo.
8. Integração no `PerfilPage`, E2E e acessibilidade.

### Dependências Técnicas

JOB-0045 (quatro blocos e skills) integrada; `@dnd-kit` e `react-router-dom` 6.30 com `createBrowserRouter` já presentes.

## Monitoramento e Observabilidade

- Backend: `WARNING` ao recusar o perfil por período ou limite, só com o nome da lista e a posição do item, sem texto do currículo.
- Frontend: sem telemetria nova. A falha ao ler ou gravar o `localStorage` é silenciosa, e o perfil funciona sem ele.

## Considerações Técnicas

### Decisões Principais

- **Estender, não duplicar:** um só componente de lista evita repetir validação e campos; a revisão usa o modo padrão (formulário).
- **Validação fora do domínio:** validar no construtor das entidades quebraria a leitura de perfis já salvos; por isso o `Periodo` e o limite ficam no validator de entrada e na API.
- **Aviso ao sair só nas telas do escopo:** modais pequenos ficam de fora. Nas telas de pedido (Ajustar vaga, Analisar ATS, Descobrir vagas), o formulário é reiniciado após o envio com sucesso, para só avisar por texto ainda não enviado.
- **Chave por conteúdo para lembrar cartões:** evita depender da posição (quebraria ao reordenar). Se o usuário editar o título do item, o cartão volta recolhido.
- **Perfis acima de 15 itens:** precisam cortar até 15 para salvar (regra simples e previsível).
- **Ordenar por período:** ano e mês iniciais, mais recente primeiro; `Atual` vale como o mais recente; vazio fica no fim, sem mover.
- **Sem normalização:** o período é gravado como digitado.
- **Rejeitadas:** componente novo só para o perfil (duplicaria campos); validar no domínio (quebra a leitura); posição como chave dos cartões; guardar a preferência de cartões na API.

### Riscos Conhecidos

- **Perfis existentes:** período livre ou mais de 15 itens obrigam correção no próximo salvar. Mitigação: a mensagem aponta item e campo, e o cartão com erro abre sozinho.
- **Dois diálogos ao voltar na revisão:** o "Voltar" já pergunta; o aviso do roteador não pode repetir a pergunta. Mitigação: marcar a saída confirmada antes de navegar.
- **Testes sem roteador de dados:** `useBlocker` exige `createBrowserRouter` ou `createMemoryRouter`. Mitigação: ajustar `renderizar-app` e os testes de página.
- **Arrasto em listas longas e no toque:** cartões abertos dificultam. Mitigação: recolher tudo ao pegar e usar o atraso de toque do board de candidaturas.
- **Divergência entre as validações:** a tabela compartilhada de casos cobre os dois lados.

### Conformidade com Padrões

- `.windsurf/rules/code-design-standards.md`: objeto de valor em `shared_kernel/domain`, validação de entrada no `Validator` do service e nenhuma dependência do domínio sobre infraestrutura.
- `.windsurf/rules/back-end-general-rules.md`: sem path novo; a mudança de contrato (422) foi pedida explicitamente no PRD; erro no formato padrão.
- `.windsurf/rules/testing-rules.md`: `TestClasse`, sem comentários, Arrange/Act/Assert separados.
- `.windsurf/rules/general-rules.md` e `AGENTS.md`: TDD, mudanças só no necessário e imports conferidos pelo pacote real.
- Desvios: nenhum.

### Arquivos relevantes e dependentes

- Backend: `src/jobsync/shared_kernel/domain/periodo.py` (novo), `perfil_estruturado/domain/perfil_estruturado.py`, `perfil_estruturado/service_layer/salvar_perfil_estruturado/validator.py`, `entrypoints/api/routers/perfil_estruturado_router.py`, `entrypoints/streamlit_app.py` (só consumidor), `tests/perfil_estruturado/` e `tests/entrypoints/api/test_perfil_estruturado_router.py`.
- Frontend: `shared/formulario-curriculo/{ListaItensCurriculo,campos-curriculo,EditorTags,competencias,anuncios-de-tags}.ts*` e os arquivos novos listados acima, `shared/ui/{ToastProvider,toast-context,ConfirmacaoModal}.ts*`, `features/perfil/{PerfilPage,formulario-perfil}.ts*`, `features/ajustar-vaga/{RevisaoCurriculoAdaptado,AjustarVagaPage}.tsx`, `features/analisar-ats/AnalisarAtsPage.tsx`, `features/descobrir-vagas/DescobrirVagasPage.tsx`, `app/rotas.tsx`, `test/renderizar-app.tsx`.
- Testes e E2E: `frontend/e2e/{quatro-blocos,acessibilidade}.spec.ts` como referência, novo `frontend/e2e/perfil-listas.spec.ts`.
