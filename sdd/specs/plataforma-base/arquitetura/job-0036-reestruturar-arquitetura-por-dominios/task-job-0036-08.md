# Tarefa 8.0: Migrar entrypoints

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Mover os adapters de entrada (`streamlit_app.py` e `servidor_captura.py`) para `src/jobsync/entrypoints/`, reconfigurar a injeção de dependências e garantir que os contratos de API e UI permaneçam inalterados.

<requirements>
- Criar `src/jobsync/entrypoints/`.
- Mover `src/ui/app_streamlit.py` para `src/jobsync/entrypoints/streamlit_app.py`.
- Mover `src/infrastructure/api/servidor_captura.py` para `src/jobsync/entrypoints/servidor_captura.py`.
- Atualizar imports internos para `jobsync.*`.
- Criar raiz de composição (`dependencies.py` ou `composition_root.py`) para instanciar adapters e services.
- Garantir que `POST /api/vagas/capturar` continue funcionando.
- Garantir que o app Streamlit inicie.
</requirements>

## Subtarefas

- [x] 8.1 Criar `src/jobsync/entrypoints/`.
- [x] 8.2 Mover `streamlit_app.py` e `servidor_captura.py`.
- [x] 8.3 Criar raiz de composição com `Depends` / injeção de dependências.
- [x] 8.4 Atualizar todos os imports para o novo pacote `jobsync`.
- [x] 8.5 Fazer smoke test do Streamlit e do servidor de captura.

## Detalhes de Implementação

Ver `techspec.md` → Componentes `entrypoints` e Considerações Técnicas. Entrypoints são adapters de entrada que traduzem HTTP/Streamlit em chamadas à camada `service_layer`.

## Critérios de Sucesso

- `streamlit run src/jobsync/entrypoints/streamlit_app.py` inicia sem erro.
- `POST /api/vagas/capturar` responde corretamente.
- Nenhum import para `application`, `domain`, `infrastructure` legado em `entrypoints`.

## Testes da Tarefa

- [ ] Smoke test do Streamlit.
- [ ] Testes do endpoint `/api/vagas/capturar` com FastAPI `TestClient`.
- [ ] `pytest` geral passa.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `src/ui/app_streamlit.py`
- `src/infrastructure/api/servidor_captura.py`
- `src/jobsync/entrypoints/`
- `src/jobsync/<dominio>/adapters/` (repositórios e clients)
