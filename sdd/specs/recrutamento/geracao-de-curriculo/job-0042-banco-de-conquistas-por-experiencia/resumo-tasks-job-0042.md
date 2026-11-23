# Resumo de Tarefas de Implementação de Banco de Conquistas por Experiência (JOB-0042)

## Tarefas

- [ ] 1.0 Conquista no domínio da experiência e persistência no JSONB
- [ ] 2.0 API do perfil: conquistas nos schemas e endpoint de conquistas parecidas
- [ ] 3.0 Seleção de 3 a 5 conquistas por experiência na adaptação
- [ ] 4.0 Frontend: banco de conquistas em Meu perfil com aviso de duplicidade
- [ ] 5.0 Avaliação manual do banco de conquistas

## Dependências

- 1.0 não depende de nenhuma outra tarefa.
- 2.0 e 3.0 dependem da 1.0 e podem ser feitas em paralelo.
- 4.0 depende da 2.0.
- 5.0 depende da 3.0 e da 4.0.
- Dependência externa: JOB-0035 e JOB-0037, já integradas.

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Conquista no domínio da experiência e persistência no JSONB | medium | — | Domínio: `Conquista` e `ExperienciaProfissional` (vazio, duplicata, parecidas). Repositório: salvar e ler com conquistas, e ler linha antiga sem a chave. |
| 2.0 | API do perfil: conquistas nos schemas e endpoint de conquistas parecidas | medium | 1.0 | Schemas com e sem `conquistas`; `POST /perfil-estruturado/conquistas/parecidas`; `VerificarConquistasParecidas`. |
| 3.0 | Seleção de 3 a 5 conquistas por experiência na adaptação | medium | 1.0 | `_experiencias_do_perfil` repassa as conquistas; o prompt do ajustador traz o bloco, a regra de 3 a 5, a proibição de acrescentar número e o fallback; experiência sem banco não muda. |
| 4.0 | Frontend: banco de conquistas em Meu perfil com aviso de duplicidade | medium | 2.0 | `PerfilPage` e `formulario-perfil`: lista, cadastro, edição, exclusão e aviso de duplicidade; o payload do `PUT` carrega as conquistas. |
| 5.0 | Avaliação manual do banco de conquistas | low | 3.0, 4.0 | Avaliação manual com chaves reais, sem teste automatizado de qualidade. |
