---
trigger: always_on
description: Regras gerais de desenvolvimento compartilhadas entre todos os projetos back-end Python
globs:
---

# Regras para APIs REST
- Quando for criar routers/endpoints, verifique outros routers do projeto para utilizar os mesmos padrões de organização e decoradores (FastAPI).
- Só altere o contrato de APIs Rest (path/URL, retorno de erros, estrutura de dados, etc.), quando isso for explicitamente solicitado.
- Use Pydantic models para validação de input/output e documentação automática.
- Mantenha consistência nos nomes de endpoints e parâmetros com a linguagem ubíqua do domínio.
