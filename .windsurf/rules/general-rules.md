---
trigger: always_on
description: Regras gerais de desenvolvimento compartilhadas entre todos os projetos
globs:
---

# Ferramentas de Desenvolvimento
- Utilize o MCP (Model Context Protocol) Server da JetBrains sempre que estiver disponível.

# Princípios e Práticas de Design
- Clean Code
- Don't Repeat Yourself (DRY)
- KISS / YAGNI
- Tell Don't Ask
- SOLID
- Domain-Driven Design (DDD)
- Hexagonal Architecture / Ports and Adapters
- Design Patterns (GoF e outros)

# Práticas Recomendadas de Desenvolvimento
- Test-Driven Development (TDD) / Red-Green-Refactor
- Refatoração continua

# Processamento de Código
- Seja cauteloso, fazendo apenas as mudanças que são solicitadas ou que você tem certeza de que são bem compreendidas e relacionadas a alteração solicitada.
- Quando for reutilizar uma classe ou interface já existente, verifique qual é o seu pacote para fazer o import correto.
- Considere o projeto raiz no path quando for buscar por diretórios e arquivos, para evitar criar diretórios que já existem ou no local errado.

# Autores de Referência
- Martin Fowler
- Uncle Bob (Robert C. Martin)
- Eric Evans
- Vaughn Vernon
- Michael C. Feathers
- Harry Percival & Bob Gregory (Cosmic Python)
