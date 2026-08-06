"""Pacote raiz do Job Sync.

Este pacote centraliza os domínios da aplicação em `src/jobsync/`.
Durante a migração incremental, símbolos podem ser reexportados aqui para
compatibilidade, mas o objetivo final é que cada domínio seja importado
diretamente (ex: `from jobsync.curriculo.domain import ...`).
"""
