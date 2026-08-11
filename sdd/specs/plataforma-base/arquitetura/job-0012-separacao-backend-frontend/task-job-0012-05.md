# Tarefa 05: Preparar deploy independente

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Garantir que o backend possa ser executado e implantado sem depender do Streamlit ou de outro frontend.

<requirements>
- Criar `Dockerfile` na raiz que instale dependências e rode `uvicorn`.
- Atualizar `.env.example` com variáveis do backend (`DATABASE_PATH`, `GROQ_API_KEY`, `CORS_ORIGINS`, `PORT`, `HOST`, `LOG_LEVEL`).
- Atualizar `README.md` com instruções de subir o backend localmente.
- Garantir que o container sobe e responde em `/health`.
</requirements>

## Subtarefas

- [ ] 5.1 Criar `Dockerfile` com build em duas etapas ou simples.
- [ ] 5.2 Atualizar `.env.example` e `README.md`.
- [ ] 5.3 Testar build do container e subir com `docker run` (ou `docker compose`).
- [ ] 5.4 Validar endpoint `/health`.

## Detalhes de Implementação

Ver `techspec-job-0012.md` -> Monitoramento e Observabilidade e Considerações Técnicas. O deploy independente é o entregável final.

## Critérios de Sucesso

- `docker build -t job-sync-backend .` completa sem erros.
- `docker run -p 8000:8000 job-sync-backend` expõe a API e `/docs`.
- Instruções no README permitem subir o backend sem o Streamlit.

## Testes da Tarefa

- [ ] Build do Dockerfile bem-sucedido.
- [ ] Container responde a `/health` e `/docs`.
- [ ] `pytest` passa dentro do container (ou na CI).

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes

- `Dockerfile`
- `.env.example`
- `README.md`
- `requirements.txt`
